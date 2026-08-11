from __future__ import annotations

from collections.abc import Sequence

from zpp.core.models import (
    CompositionMode,
    EffectiveFlavor,
    EffectiveTraitFamily,
    SourceKind,
    TraitDocument,
)

_SOURCE_RANK = {
    SourceKind.REPOSITORY: 0,
    SourceKind.SPACE: 1,
    SourceKind.GLOBAL: 2,
}


class CompositionError(ValueError):
    pass


def compose_trait_family(
    family: str,
    contributions: Sequence[TraitDocument],
) -> EffectiveTraitFamily:
    if not contributions:
        raise CompositionError(f"trait family has no contributions: {family}")
    if any(item.family != family for item in contributions):
        raise CompositionError(f"trait contribution family mismatch: {family}")
    invalid_modes = [
        item
        for item in contributions
        if item.mode is CompositionMode.REPOSITORY_OVERWRITE
        and item.source.kind is not SourceKind.REPOSITORY
    ]
    if invalid_modes:
        raise CompositionError(
            "repository-overwrite is valid only for repository contributions"
        )

    ordered = sorted(
        enumerate(contributions),
        key=lambda item: (
            _SOURCE_RANK[item[1].source.kind],
            item[1].source.order,
            item[0],
        ),
    )
    documents = [item for _, item in ordered]
    overwrite = any(
        item.mode is CompositionMode.REPOSITORY_OVERWRITE for item in documents
    )
    excluded = tuple(
        item.source
        for item in documents
        if overwrite and item.source.kind is not SourceKind.REPOSITORY
    )
    included = [
        item
        for item in documents
        if not overwrite or item.source.kind is SourceKind.REPOSITORY
    ]
    policy_document = included[0]
    effective_flavors: list[EffectiveFlavor] = []
    for document in included:
        for flavor in document.flavors:
            effective_flavors.append(
                EffectiveFlavor(
                    flavor=flavor,
                    source=document.source,
                    effective_position=len(effective_flavors),
                )
            )
    return EffectiveTraitFamily(
        family=family,
        selection=policy_document.selection,
        policy_source=policy_document.source,
        mode=(
            CompositionMode.REPOSITORY_OVERWRITE
            if overwrite
            else CompositionMode.LAYERED
        ),
        flavors=tuple(effective_flavors),
        excluded_sources=excluded,
    )
