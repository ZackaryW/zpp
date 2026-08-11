from __future__ import annotations

import json
from collections.abc import Mapping
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from zpp.models import (
    FacetContext,
    FacetProvenance,
    ResolutionContext,
    StoredContext,
    TargetIdentity,
)


class SessionContextError(ValueError):
    pass


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _TargetInput(_StrictModel):
    repository: str = Field(min_length=1)


class _ProvenanceInput(_StrictModel):
    source: str = Field(min_length=1)
    evidence: tuple[str, ...] = ()


class _StoredInput(_StrictModel):
    version: int
    target: _TargetInput
    facets: dict[str, str | tuple[str, ...] | bool]
    provenance: dict[str, _ProvenanceInput]
    fingerprints: dict[str, str]

    @field_validator("version")
    @classmethod
    def supported_version(cls, value: int) -> int:
        if value != 1:
            raise ValueError("unsupported ZPP_CONTEXT version")
        return value

    @field_validator("facets", mode="before")
    @classmethod
    def valid_facets(cls, value: object) -> object:
        if not isinstance(value, Mapping):
            raise ValueError("facets must be an object")
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError("facet names must be non-empty strings")
            if isinstance(item, bool):
                continue
            if isinstance(item, str):
                if not item:
                    raise ValueError("facet values must not be empty")
                continue
            if not isinstance(item, (list, tuple)):
                raise ValueError("facet values must be strings arrays or booleans")
            if (
                not item
                or any(not isinstance(entry, str) or not entry for entry in item)
                or len(set(item)) != len(item)
            ):
                raise ValueError(
                    "facet arrays must contain distinct non-empty strings"
                )
        return value

    @field_validator("provenance")
    @classmethod
    def complete_provenance(
        cls,
        value: dict[str, _ProvenanceInput],
        info,
    ) -> dict[str, _ProvenanceInput]:
        facets = info.data.get("facets", {})
        if set(value) != set(facets):
            raise ValueError("provenance must identify every facet exactly once")
        return value


def _empty(target: TargetIdentity) -> StoredContext:
    return StoredContext(
        target=target,
        values=MappingProxyType({}),
        provenance=MappingProxyType({}),
        fingerprints=MappingProxyType({}),
    )


def restore_session_context(
    raw: str | None,
    target: TargetIdentity,
    fingerprints: Mapping[str, str],
) -> StoredContext:
    if raw is None or raw == "":
        return _empty(target)
    try:
        decoded_json = json.loads(raw)
        decoded = _StoredInput.model_validate(decoded_json)
    except (json.JSONDecodeError, ValidationError) as error:
        raise SessionContextError(f"invalid ZPP_CONTEXT: {error}") from error
    if decoded.target.repository != target.repository:
        return _empty(target)

    values: dict[str, str | tuple[str, ...] | bool] = {}
    provenance: dict[str, FacetProvenance] = {}
    for key, value in decoded.facets.items():
        item = decoded.provenance[key]
        drifted = any(
            decoded.fingerprints.get(evidence_key)
            != fingerprints.get(evidence_key)
            for evidence_key in item.evidence
        )
        if drifted:
            continue
        values[key] = tuple(value) if isinstance(value, tuple) else value
        provenance[key] = FacetProvenance(item.source, tuple(item.evidence))
    relevant_keys = {
        evidence_key
        for item in provenance.values()
        for evidence_key in item.evidence
    }
    current_fingerprints = {
        key: fingerprints[key] for key in relevant_keys if key in fingerprints
    }
    return StoredContext(
        target=target,
        values=MappingProxyType(values),
        provenance=MappingProxyType(provenance),
        fingerprints=MappingProxyType(current_fingerprints),
    )


def encode_session_context(context: StoredContext) -> str:
    payload = {
        "version": 1,
        "target": {"repository": context.target.repository},
        "facets": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in context.values.items()
        },
        "provenance": {
            key: {
                "source": item.source,
                "evidence": list(item.evidence),
            }
            for key, item in context.provenance.items()
        },
        "fingerprints": dict(context.fingerprints),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_resolution_context(
    invocation: FacetContext,
    repository: FacetContext,
    stored: StoredContext,
) -> ResolutionContext:
    values: dict[str, str | tuple[str, ...] | bool] = dict(stored.values)
    provenance = {
        key: item.source for key, item in stored.provenance.items()
    }
    values.update(repository.values)
    provenance.update(repository.provenance)
    values.update(invocation.values)
    provenance.update(invocation.provenance)
    return ResolutionContext(
        values=MappingProxyType(values),
        provenance=MappingProxyType(provenance),
    )
