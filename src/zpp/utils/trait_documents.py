from __future__ import annotations

from typing import Annotated, Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError

from zpp.utils.models import TraitDocument, ValidationIssue, ZppValidationError


class _TraitMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: Annotated[str, Field(min_length=1)]
    description: Annotated[str, Field(min_length=1)]
    order: Annotated[int, Field(ge=0)] | None = None
    config: dict[str, JsonValue] = Field(default_factory=dict)
    skill_lookup: list[str] = Field(default_factory=list)


def parse_trait_document(source: str, *, expected_name: str) -> TraitDocument:
    metadata_source, body = _split_frontmatter(source)
    try:
        raw_metadata: Any = yaml.safe_load(metadata_source)
        metadata = _TraitMetadata.model_validate(raw_metadata, strict=True)
    except (yaml.YAMLError, ValidationError) as error:
        raise _as_zpp_validation_error(error) from error

    if metadata.name != expected_name:
        raise ZppValidationError(
            (
                ValidationIssue(
                    location=("name",),
                    message=f"trait name {metadata.name!r} does not match {expected_name!r}",
                ),
            )
        )

    return TraitDocument(
        name=metadata.name,
        description=metadata.description,
        order=metadata.order,
        config=metadata.config,
        skill_lookup=tuple(metadata.skill_lookup),
        body=body,
    )


def render_trait_document(document: TraitDocument) -> str:
    metadata = {
        "name": document.name,
        "description": document.description,
        "order": document.order,
        "config": document.config,
        "skill_lookup": list(document.skill_lookup),
    }
    encoded = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    return f"---\n{encoded}---\n{document.body}"


def _split_frontmatter(source: str) -> tuple[str, str]:
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ZppValidationError(
            (ValidationIssue(location=(), message="trait document must start with '---'"),)
        )

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])

    raise ZppValidationError(
        (ValidationIssue(location=(), message="trait frontmatter is not closed"),)
    )


def _as_zpp_validation_error(error: yaml.YAMLError | ValidationError) -> ZppValidationError:
    if isinstance(error, ValidationError):
        issues = tuple(
            ValidationIssue(
                location=tuple(item["loc"]),
                message=item["msg"],
            )
            for item in error.errors()
        )
    else:
        issues = (ValidationIssue(location=(), message=str(error)),)
    return ZppValidationError(issues)
