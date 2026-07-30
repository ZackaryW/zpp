from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from zpp.utils.models import (
    LayerConfig,
    TraitDocument,
    TraitIndex,
    ValidationIssue,
    ZppValidationError,
)


def select_effective_documents(
    activated: Sequence[str],
    indexes: Sequence[TraitIndex],
) -> tuple[TraitDocument, ...]:
    selected: list[TraitDocument] = []
    issues: list[ValidationIssue] = []
    for name in activated:
        record = next(
            (index["traits"][name] for index in reversed(indexes) if name in index["traits"]),
            None,
        )
        if record is None:
            issues.append(
                ValidationIssue(
                    location=("traits", name),
                    message=f"activated trait {name!r} has no authored definition",
                )
            )
            continue
        selected.append(
            TraitDocument(
                name=name,
                description=record["description"],
                order=record["order"],
                config=dict(record["config"]),
                skill_lookup=tuple(record["skill_lookup"]),
                body=record["body"],
            )
        )
    if issues:
        raise ZppValidationError(tuple(issues))
    return tuple(selected)


def apply_trait_config_overlays(
    documents: Sequence[TraitDocument],
    configurations: Sequence[LayerConfig],
) -> tuple[TraitDocument, ...]:
    overlaid: list[TraitDocument] = []
    for document in documents:
        config = dict(document.config)
        for layer in configurations:
            config.update(layer.traits_config.get(document.name, {}))
        overlaid.append(replace(document, config=config))
    return tuple(overlaid)


def order_effective_traits(
    documents: Sequence[TraitDocument],
    activation_order: Sequence[str],
) -> tuple[TraitDocument, ...]:
    positions = {name: position for position, name in enumerate(activation_order)}
    return tuple(
        sorted(
            documents,
            key=lambda document: (
                0 if document.order is not None else 1,
                document.order if document.order is not None else 0,
                positions.get(document.name, len(positions)),
            ),
        )
    )
