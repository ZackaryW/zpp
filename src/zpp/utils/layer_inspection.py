from __future__ import annotations

import json
from pathlib import Path

from zpp.utils.control_documents import validate_layer_config, validate_trigger_config
from zpp.utils.models import (
    AuthoredLayerPaths,
    LayerInspection,
    ValidationIssue,
    ZppValidationError,
)
from zpp.utils.trait_compiler import compile_trait_index


def inspect_authored_layer(paths: AuthoredLayerPaths) -> LayerInspection:
    if not paths.root.exists():
        return LayerInspection(state="absent", missing=(paths.root,))
    if not paths.root.is_dir():
        return LayerInspection(
            state="invalid",
            issues=(_issue(paths.root, "authored layer root is not a directory"),),
        )

    missing: list[Path] = []
    issues: list[ValidationIssue] = []
    for managed_file, validator in (
        (paths.config, validate_layer_config),
        (paths.triggers, validate_trigger_config),
    ):
        if not managed_file.exists():
            missing.append(managed_file)
            continue
        if not managed_file.is_file():
            issues.append(_issue(managed_file, "managed source is not a file"))
            continue
        try:
            validator(json.loads(managed_file.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            issues.append(_issue(managed_file, str(error)))
        except ZppValidationError as error:
            issues.extend(_with_source(error, managed_file))

    if not paths.traits.exists():
        missing.append(paths.traits)
    elif not paths.traits.is_dir():
        issues.append(_issue(paths.traits, "traits source is not a directory"))
    else:
        try:
            compile_trait_index(sorted(paths.traits.glob("*.md")))
        except ZppValidationError as error:
            issues.extend(error.issues)
        except OSError as error:
            issues.append(_issue(paths.traits, str(error)))

    if issues:
        state = "invalid"
    elif missing:
        state = "partial"
    else:
        state = "complete"
    return LayerInspection(state=state, missing=tuple(missing), issues=tuple(issues))


def _issue(source: Path, message: str) -> ValidationIssue:
    return ValidationIssue(location=(), message=message, source=source)


def _with_source(error: ZppValidationError, source: Path) -> tuple[ValidationIssue, ...]:
    return tuple(
        ValidationIssue(location=issue.location, message=issue.message, source=source)
        for issue in error.issues
    )
