from __future__ import annotations

import json
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath

from zpp.utils.control_documents import validate_layer_config, validate_trigger_config
from zpp.utils.models import (
    AuthoredLayerFile,
    AuthoredLayerSnapshot,
    CreationEntry,
    CreationPlan,
    ValidationIssue,
    ZppValidationError,
)
from zpp.utils.trait_documents import parse_trait_document


def collect_authored_layer(root: Traversable) -> AuthoredLayerSnapshot:
    if not root.is_dir() or _is_symlink(root):
        raise ValueError("authored layer root is not a regular directory")

    config = _read_file(root.joinpath("config.json"))
    triggers = _read_file(root.joinpath("trait.json"))
    issues: list[ValidationIssue] = []
    _validate_json_source(
        config,
        root.joinpath("config.json"),
        validate_layer_config,
        issues,
    )
    _validate_json_source(
        triggers,
        root.joinpath("trait.json"),
        validate_trigger_config,
        issues,
    )

    traits_root = root.joinpath("traits")
    if not traits_root.is_dir() or _is_symlink(traits_root):
        raise ValueError("authored traits source is not a regular directory")

    files = [
        AuthoredLayerFile(PurePosixPath("config.json"), config),
        AuthoredLayerFile(PurePosixPath("trait.json"), triggers),
    ]
    for source in sorted(traits_root.iterdir(), key=lambda item: item.name):
        if not source.name.endswith(".md"):
            continue
        content = _read_file(source)
        try:
            parse_trait_document(
                content.decode("utf-8"),
                expected_name=source.name.removesuffix(".md"),
            )
        except UnicodeError as error:
            issues.append(_issue(source, str(error)))
        except ZppValidationError as error:
            issues.extend(_with_source(error, source))
        files.append(
            AuthoredLayerFile(
                PurePosixPath("traits", source.name),
                content,
            )
        )
    if issues:
        raise ZppValidationError(tuple(issues))
    return AuthoredLayerSnapshot(tuple(files))


def authored_layer_creation_plan(
    snapshot: AuthoredLayerSnapshot,
    destination: Path,
) -> CreationPlan:
    entries = [
        CreationEntry(destination, "directory"),
        CreationEntry(destination / "traits", "directory"),
    ]
    entries.extend(
        CreationEntry(
            destination.joinpath(*source.relative_path.parts),
            "binary",
            source.content,
        )
        for source in snapshot.files
    )
    return CreationPlan(tuple(entries))


def _read_file(source: Traversable) -> bytes:
    if not source.is_file() or _is_symlink(source):
        raise ValueError(f"authored source is not a regular file: {source.name}")
    return source.read_bytes()


def _is_symlink(source: Traversable) -> bool:
    return isinstance(source, Path) and source.is_symlink()


def _validate_json_source(
    content: bytes,
    source: Traversable,
    validator,
    issues: list[ValidationIssue],
) -> None:
    try:
        validator(json.loads(content.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError) as error:
        issues.append(_issue(source, str(error)))
    except ZppValidationError as error:
        issues.extend(_with_source(error, source))


def _issue(source: Traversable, message: str) -> ValidationIssue:
    return ValidationIssue(
        location=(),
        message=message,
        source=source if isinstance(source, Path) else None,
    )


def _with_source(
    error: ZppValidationError,
    source: Traversable,
) -> tuple[ValidationIssue, ...]:
    return tuple(
        ValidationIssue(
            location=issue.location,
            message=issue.message,
            source=source if isinstance(source, Path) else None,
        )
        for issue in error.issues
    )
