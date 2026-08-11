from __future__ import annotations

import json
from collections.abc import Mapping
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from zpp.core.models import (
    PROTECTED_CONTEXT_KEYS,
    ContextMember,
    FacetContext,
    FacetProvenance,
    ResolutionContext,
    ResolutionResult,
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


class _MemberInput(_ProvenanceInput):
    value: str | bool


def _validate_facets(value: object) -> object:
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


class _StoredInputV1(_StrictModel):
    version: Literal[1]
    target: _TargetInput
    facets: dict[str, str | tuple[str, ...] | bool]
    provenance: dict[str, _ProvenanceInput]
    fingerprints: dict[str, str]

    @field_validator("facets", mode="before")
    @classmethod
    def valid_facets(cls, value: object) -> object:
        return _validate_facets(value)

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


class _StoredInputV2(_StrictModel):
    version: Literal[2]
    target: _TargetInput
    facets: dict[str, str | tuple[str, ...] | bool]
    members: dict[str, tuple[_MemberInput, ...]]
    fingerprints: dict[str, str]

    @field_validator("facets", mode="before")
    @classmethod
    def valid_facets(cls, value: object) -> object:
        return _validate_facets(value)

    @field_validator("members")
    @classmethod
    def aligned_members(
        cls,
        value: dict[str, tuple[_MemberInput, ...]],
        info,
    ) -> dict[str, tuple[_MemberInput, ...]]:
        facets = info.data.get("facets", {})
        if set(value) != set(facets):
            raise ValueError("members must identify every facet exactly once")
        for key, items in value.items():
            expected = facets[key]
            expected_values = expected if isinstance(expected, tuple) else (expected,)
            if not items or tuple(item.value for item in items) != expected_values:
                raise ValueError("members must align with facet values")
        return value


def _members_for_value(
    value: str | tuple[str, ...] | bool,
    source: str,
    evidence: tuple[str, ...] = (),
) -> tuple[ContextMember, ...]:
    values = value if isinstance(value, tuple) else (value,)
    return tuple(ContextMember(item, source, evidence) for item in values)


def _value_for_members(
    members: tuple[ContextMember, ...],
) -> str | tuple[str, ...] | bool:
    if len(members) == 1:
        return members[0].value
    return tuple(member.value for member in members)  # type: ignore[return-value]


def _provenance_for_members(
    members: tuple[ContextMember, ...],
) -> FacetProvenance:
    evidence: list[str] = []
    for member in members:
        evidence.extend(item for item in member.evidence if item not in evidence)
    return FacetProvenance(members[0].source, tuple(evidence))


def _empty(target: TargetIdentity) -> StoredContext:
    return StoredContext(
        target=target,
        values=MappingProxyType({}),
        provenance=MappingProxyType({}),
        fingerprints=MappingProxyType({}),
        members=MappingProxyType({}),
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
        if not isinstance(decoded_json, Mapping):
            raise ValueError("stored context must be an object")
        version = decoded_json.get("version")
        if version == 1:
            decoded = _StoredInputV1.model_validate(decoded_json)
        elif version == 2:
            decoded = _StoredInputV2.model_validate(decoded_json)
        else:
            raise ValueError("unsupported ZPP_CONTEXT version")
    except (json.JSONDecodeError, ValidationError, ValueError) as error:
        raise SessionContextError(f"invalid ZPP_CONTEXT: {error}") from error
    if decoded.target.repository != target.repository:
        return _empty(target)

    values: dict[str, str | tuple[str, ...] | bool] = {}
    provenance: dict[str, FacetProvenance] = {}
    members: dict[str, tuple[ContextMember, ...]] = {}
    for key, value in decoded.facets.items():
        if key in PROTECTED_CONTEXT_KEYS:
            continue
        if isinstance(decoded, _StoredInputV1):
            item = decoded.provenance[key]
            candidates = _members_for_value(
                tuple(value) if isinstance(value, tuple) else value,
                item.source,
                tuple(item.evidence),
            )
        else:
            candidates = tuple(
                ContextMember(item.value, item.source, tuple(item.evidence))
                for item in decoded.members[key]
            )
        retained = tuple(
            member
            for member in candidates
            if not any(
                decoded.fingerprints.get(evidence_key)
                != fingerprints.get(evidence_key)
                for evidence_key in member.evidence
            )
        )
        if not retained:
            continue
        values[key] = _value_for_members(retained)
        provenance[key] = _provenance_for_members(retained)
        members[key] = retained
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
        members=MappingProxyType(members),
    )


def encode_session_context(context: StoredContext) -> str:
    payload = {
        "version": 2,
        "target": {"repository": context.target.repository},
        "facets": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in context.values.items()
        },
        "members": {
            key: [
                {
                    "value": member.value,
                    "source": member.source,
                    "evidence": list(member.evidence),
                }
                for member in context.members.get(
                    key,
                    _members_for_value(
                        context.values[key],
                        context.provenance[key].source,
                        context.provenance[key].evidence,
                    ),
                )
            ]
            for key in context.values
        },
        "fingerprints": dict(context.fingerprints),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_resolution_context(
    invocation: FacetContext,
    repository: FacetContext,
    stored: StoredContext,
) -> ResolutionContext:
    values: dict[str, str | tuple[str, ...] | bool] = {
        key: value
        for key, value in stored.values.items()
        if key not in PROTECTED_CONTEXT_KEYS
    }
    members = {
        key: value
        for key, value in stored.members.items()
        if key not in PROTECTED_CONTEXT_KEYS
    }
    provenance = {
        key: item.source
        for key, item in stored.provenance.items()
        if key not in PROTECTED_CONTEXT_KEYS
    }
    evidence = {
        key: item.evidence
        for key, item in stored.provenance.items()
        if item.evidence and key not in PROTECTED_CONTEXT_KEYS
    }
    values.update(repository.values)
    provenance.update(repository.provenance)
    for key in repository.values:
        evidence.pop(key, None)
        members[key] = _members_for_value(
            repository.values[key], repository.provenance[key]
        )
    values.update(invocation.values)
    provenance.update(invocation.provenance)
    for key in invocation.values:
        evidence.pop(key, None)
        members[key] = _members_for_value(
            invocation.values[key], invocation.provenance[key]
        )
    relevant = {item for keys in evidence.values() for item in keys}
    return ResolutionContext(
        values=MappingProxyType(values),
        provenance=MappingProxyType(provenance),
        evidence=MappingProxyType(evidence),
        fingerprints=MappingProxyType(
            {
                key: value
                for key, value in stored.fingerprints.items()
                if key in relevant
            }
        ),
        members=MappingProxyType(members),
    )


def complete_stored_context(
    result: ResolutionResult,
    target: TargetIdentity,
) -> StoredContext:
    members = {
        key: result.context.members.get(
            key,
            _members_for_value(
                value,
                result.context.provenance[key],
                result.context.evidence.get(key, ()),
            ),
        )
        for key, value in result.context.values.items()
        if key not in PROTECTED_CONTEXT_KEYS
    }
    provenance = {
        key: _provenance_for_members(items) for key, items in members.items()
    }
    relevant = {
        evidence_key
        for item in provenance.values()
        for evidence_key in item.evidence
    }
    return StoredContext(
        target=target,
        values=MappingProxyType(
            {
                key: value
                for key, value in result.context.values.items()
                if key not in PROTECTED_CONTEXT_KEYS
            }
        ),
        provenance=MappingProxyType(provenance),
        fingerprints=MappingProxyType(
            {
                key: value
                for key, value in result.context.fingerprints.items()
                if key in relevant
            }
        ),
        members=MappingProxyType(members),
    )
