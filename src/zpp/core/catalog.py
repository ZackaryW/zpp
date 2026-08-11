from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

from zpp.core.models import (
    CompositionMode,
    EvidenceBranch,
    FacetContext,
    FileContains,
    SelectionPolicy,
    SourceRef,
    TraitContent,
    TraitDocument,
    TraitFlavor,
    frozen_mapping,
)

_FAMILY = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


class TraitValidationError(ValueError):
    def __init__(
        self,
        *,
        source: SourceRef,
        family: str,
        location: tuple[str | int, ...],
        detail: str,
    ) -> None:
        self.source = source
        self.family = family
        self.location = location
        self.detail = detail
        rendered = ".".join(str(item) for item in location)
        super().__init__(
            f"invalid trait document {source.identifier}:{family}:{rendered}: {detail}"
        )


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _MetaInput(_StrictModel):
    selection: SelectionPolicy
    mode: CompositionMode = CompositionMode.LAYERED


class _FileContainsInput(_StrictModel):
    path: str = Field(min_length=1)
    text: str


class _EvidenceInput(_StrictModel):
    workspace_contains: str | None = None
    file_contains: _FileContainsInput | None = None
    which: str | None = None

    @field_validator("workspace_contains", "which")
    @classmethod
    def non_empty_optional(cls, value: str | None) -> str | None:
        if value == "":
            raise ValueError("must not be empty")
        return value


class _ContentInput(_StrictModel):
    body: str = Field(min_length=1)


class _FlavorInput(_StrictModel):
    facet: dict[str, str] = Field(default_factory=dict)
    when: tuple[_EvidenceInput, ...] = ()
    content: _ContentInput

    @field_validator("facet")
    @classmethod
    def valid_facets(cls, value: dict[str, str]) -> dict[str, str]:
        if any(not key or not item for key, item in value.items()):
            raise ValueError("facet names and values must not be empty")
        return value


class _DocumentInput(_StrictModel):
    meta: _MetaInput
    trait: Annotated[tuple[_FlavorInput, ...], Field(min_length=1)]


class _ContextInput(_StrictModel):
    facet: dict[str, str | tuple[str, ...]] = Field(default_factory=dict)

    @field_validator("facet", mode="before")
    @classmethod
    def valid_context_facets(cls, value: object) -> object:
        if not isinstance(value, Mapping):
            raise ValueError("facet must be a table")
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError("facet names must be non-empty strings")
            if isinstance(item, str):
                if not item:
                    raise ValueError("facet values must not be empty")
                continue
            if not isinstance(item, (list, tuple)):
                raise ValueError("facet values must be strings or string arrays")
            if (
                not item
                or any(not isinstance(entry, str) or not entry for entry in item)
                or len(set(item)) != len(item)
            ):
                raise ValueError(
                    "facet arrays must contain distinct non-empty strings"
                )
        return value


def decode_trait_document(
    family: str,
    values: Mapping[str, object],
    source: SourceRef,
) -> TraitDocument:
    if not _FAMILY.fullmatch(family):
        raise TraitValidationError(
            source=source,
            family=family,
            location=("family",),
            detail="family name is invalid",
        )
    try:
        decoded = _DocumentInput.model_validate(values)
    except ValidationError as error:
        first = error.errors(include_url=False)[0]
        raise TraitValidationError(
            source=source,
            family=family,
            location=tuple(first["loc"]),
            detail=str(first["msg"]),
        ) from error

    if decoded.meta.selection is SelectionPolicy.FIRST_WIN:
        for position, flavor in enumerate(decoded.trait):
            for earlier in decoded.trait[:position]:
                earlier_constraints = set(earlier.facet.items())
                later_constraints = set(flavor.facet.items())
                shadows_every_path = not earlier.when and (
                    not earlier_constraints
                    or (not flavor.when and earlier_constraints <= later_constraints)
                )
                if shadows_every_path:
                    raise TraitValidationError(
                        source=source,
                        family=family,
                        location=("trait", position),
                        detail=(
                            "flavor is unreachable under first-win because an "
                            "earlier unconditional flavor always wins"
                        ),
                    )

    flavors = tuple(
        TraitFlavor(
            facets=frozen_mapping(item.facet),
            when=tuple(
                EvidenceBranch(
                    workspace_contains=branch.workspace_contains,
                    file_contains=(
                        FileContains(
                            path=branch.file_contains.path,
                            text=branch.file_contains.text,
                        )
                        if branch.file_contains is not None
                        else None
                    ),
                    which=branch.which,
                )
                for branch in item.when
            ),
            content=TraitContent(item.content.body),
            position=position,
        )
        for position, item in enumerate(decoded.trait)
    )
    return TraitDocument(
        family=family,
        selection=decoded.meta.selection,
        mode=decoded.meta.mode,
        flavors=flavors,
        source=source,
    )


def decode_repository_context(
    values: Mapping[str, object],
    source: SourceRef,
) -> FacetContext:
    try:
        decoded = _ContextInput.model_validate(values)
    except ValidationError as error:
        first = error.errors(include_url=False)[0]
        raise TraitValidationError(
            source=source,
            family="context",
            location=tuple(first["loc"]),
            detail=str(first["msg"]),
        ) from error
    normalized = {
        key: tuple(value) if isinstance(value, tuple) else value
        for key, value in decoded.facet.items()
    }
    return FacetContext(
        values=frozen_mapping(normalized),
        provenance=frozen_mapping({key: source.identifier for key in normalized}),
    )
