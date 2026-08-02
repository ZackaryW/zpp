from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path

from zpp.utils.models import (
    TraitIndex,
    TraitRecord,
    ValidationIssue,
    ZppValidationError,
)
from zpp.utils.trait_documents import parse_trait_document


def compile_trait_index(sources: Iterable[Path]) -> TraitIndex:
    records: dict[str, TraitRecord] = {}
    record_sources: dict[str, Path] = {}
    issues: list[ValidationIssue] = []
    for source in sources:
        try:
            source_bytes = source.read_bytes()
            document = parse_trait_document(
                source_bytes.decode("utf-8"),
                expected_name=source.stem,
            )
        except ZppValidationError as error:
            issues.extend(
                ValidationIssue(
                    location=issue.location,
                    message=issue.message,
                    source=source,
                )
                for issue in error.issues
            )
            continue
        except (OSError, UnicodeError) as error:
            issues.append(
                ValidationIssue(location=(), message=str(error), source=source)
            )
            continue

        if document.name in records:
            issues.append(
                ValidationIssue(
                    location=("name",),
                    message=(
                        f"duplicate trait {document.name!r}; first defined by "
                        f"{record_sources[document.name]}"
                    ),
                    source=source,
                )
            )
            continue

        records[document.name] = {
            "description": document.description,
            "order": document.order,
            "config": document.config,
            "skill_lookup": list(document.skill_lookup),
            "body": document.body,
            "source_sha256": sha256(source_bytes).hexdigest(),
        }
        record_sources[document.name] = source

    if issues:
        raise ZppValidationError(tuple(issues))

    return {
        "schema_version": 2,
        "traits": {name: records[name] for name in sorted(records)},
    }
