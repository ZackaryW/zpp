"""Capability-local verification subjects for the TOML trait catalog."""

from __future__ import annotations

from zpp.core.catalog import decode_trait_document
from zpp.core.composition import compose_trait_family
from zpp.core.models import SourceKind, SourceRef


def flavor(body: str, **facet: str) -> dict:
    entry: dict = {"content": {"body": body}}
    if facet:
        entry["facet"] = dict(facet)
    return entry


def document(
    *flavors: dict,
    selection: str = "extend",
    activation: str | None = None,
    mode: str | None = None,
) -> dict:
    meta: dict = {"selection": selection}
    if activation is not None:
        meta["activation"] = activation
    if mode is not None:
        meta["mode"] = mode
    return {"meta": meta, "trait": list(flavors)}


def decode(
    values: dict,
    *,
    family: str = "bdd",
    kind: SourceKind = SourceKind.REPOSITORY,
    identifier: str = "source",
):
    return decode_trait_document(family, values, SourceRef(kind, identifier))


def compose(*decoded, family: str = "bdd"):
    return compose_trait_family(family, list(decoded))


def bodies(composed) -> list[str]:
    return [item.flavor.content.body for item in composed.flavors]
