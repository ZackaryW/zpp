from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from zpp.core.catalog import decode_repository_context, decode_trait_document
from zpp.core.composition import compose_trait_family
from zpp.core.evidence import EvidenceRuntime, collect_evidence, evidence_requests
from zpp.core.models import (
    PROTECTED_CONTEXT_KEYS,
    ActivationMode,
    FacetContext,
    ResolutionResult,
    SourceKind,
    SourceRef,
    TargetIdentity,
    frozen_mapping,
    normalize_workflow_stage,
)
from zpp.core.resolution import resolve_traits, select_trait_families
from zpp.core.session import (
    build_resolution_context,
    complete_stored_context,
    encode_session_context,
    restore_session_context,
)


@dataclass(frozen=True, slots=True)
class BoundTraitDocument:
    family: str
    values: Mapping[str, object]
    identifier: str | None = None
    order: int = 0
    path: Path | None = None


@dataclass(frozen=True, slots=True)
class BoundTraitSource:
    kind: SourceKind
    identifier: str
    order: int
    documents: tuple[BoundTraitDocument, ...]


@dataclass(frozen=True, slots=True)
class TraitInvocation:
    target: Path
    stage: str | None
    facets: Mapping[str, str | Sequence[str]]
    stored_context: str | None
    repository_context: BoundTraitDocument | None
    sources: tuple[BoundTraitSource, ...]
    requested_families: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class ResolvedBody:
    family: str
    body: str
    source: SourceRef
    flavor_position: int


@dataclass(frozen=True, slots=True)
class TraitInvocationResult:
    resolution: ResolutionResult
    bodies: tuple[ResolvedBody, ...]
    context: str
    explanation: Mapping[str, object]


class TraitApplication:
    def __init__(
        self,
        evidence_runtime: Callable[[Path], EvidenceRuntime],
    ) -> None:
        self._evidence_runtime = evidence_runtime

    def resolve(self, invocation: TraitInvocation) -> TraitInvocationResult:
        target = invocation.target.resolve()
        repository_context = self._repository_context(invocation)
        families = self._families(invocation.sources)
        selected_families = select_trait_families(
            families, invocation.requested_families
        )
        evidence_families = tuple(
            family
            for family in selected_families
            if family.activation is not ActivationMode.ALWAYS_RUN
        )
        evidence = collect_evidence(
            evidence_requests(evidence_families), self._evidence_runtime(target)
        )
        fingerprints = {
            key: value
            for result in evidence.values()
            for key, value in result.fingerprints.items()
        }
        identity = TargetIdentity(str(target))
        stored = restore_session_context(
            invocation.stored_context, identity, fingerprints
        )
        invocation_values = self._normalize_facets(invocation.facets)
        stage = normalize_workflow_stage(invocation.stage)
        if stage is not None:
            invocation_values["stage"] = stage.value
        direct = FacetContext(
            values=frozen_mapping(invocation_values),
            provenance=frozen_mapping({key: "invocation" for key in invocation_values}),
        )
        known = build_resolution_context(direct, repository_context, stored)
        resolved = resolve_traits(
            selected_families,
            known,
            evidence,
            requested=tuple(family.family for family in selected_families),
        )
        completed = complete_stored_context(resolved, identity)
        bodies = tuple(
            ResolvedBody(
                family.family,
                retained.flavor.content.body,
                retained.source,
                retained.flavor.position,
            )
            for family in resolved.families
            for retained in family.retained
        )
        return TraitInvocationResult(
            resolution=resolved,
            bodies=bodies,
            context=encode_session_context(completed),
            explanation=MappingProxyType(self._explain(selected_families, resolved)),
        )

    @staticmethod
    def _repository_context(invocation: TraitInvocation) -> FacetContext:
        document = invocation.repository_context
        if document is None:
            return FacetContext()
        source = SourceRef(
            SourceKind.REPOSITORY,
            document.identifier or "repository-context",
            document.order,
            document.path,
        )
        return decode_repository_context(document.values, source)

    @staticmethod
    def _families(sources: Sequence[BoundTraitSource]):
        grouped = defaultdict(list)
        for source in sources:
            for local_position, document in enumerate(source.documents):
                reference = SourceRef(
                    source.kind,
                    document.identifier or source.identifier,
                    source.order + document.order + local_position,
                    document.path,
                )
                grouped[document.family].append(
                    decode_trait_document(document.family, document.values, reference)
                )
        return tuple(
            compose_trait_family(family, contributions)
            for family, contributions in sorted(grouped.items())
        )

    @staticmethod
    def _normalize_facets(
        facets: Mapping[str, str | Sequence[str]],
    ) -> dict[str, str | tuple[str, ...]]:
        normalized: dict[str, str | tuple[str, ...]] = {}
        for key, value in facets.items():
            if not key:
                raise ValueError("facet names must not be empty")
            if key in PROTECTED_CONTEXT_KEYS:
                raise ValueError(
                    f"protected context key requires its explicit option: {key}"
                )
            if isinstance(value, str):
                if not value:
                    raise ValueError(f"facet value must not be empty: {key}")
                normalized[key] = value
                continue
            items = tuple(value)
            if not items or any(not item for item in items):
                raise ValueError(f"facet values must not be empty: {key}")
            if len(set(items)) != len(items):
                raise ValueError(f"facet values must be distinct: {key}")
            normalized[key] = items
        return normalized

    @staticmethod
    def _explain(families, result: ResolutionResult) -> dict[str, object]:
        effective = {family.family: family for family in families}
        return {
            "context": {
                "values": dict(result.context.values),
                "provenance": dict(result.context.provenance),
                "evidence": dict(result.context.evidence),
                "fingerprints": dict(result.context.fingerprints),
                "members": {
                    key: [
                        {
                            "value": member.value,
                            "source": member.source,
                            "evidence": list(member.evidence),
                        }
                        for member in members
                    ]
                    for key, members in result.context.members.items()
                },
            },
            "families": [
                {
                    "family": resolution.family,
                    "selection": effective[resolution.family].selection.value,
                    "activation": effective[resolution.family].activation.value,
                    "policy_source": effective[
                        resolution.family
                    ].policy_source.identifier,
                    "mode": effective[resolution.family].mode.value,
                    "excluded_sources": [
                        source.identifier
                        for source in effective[resolution.family].excluded_sources
                    ],
                    "decisions": [
                        {
                            "effective_position": decision.flavor.effective_position,
                            "flavor_position": decision.flavor.flavor.position,
                            "source": decision.flavor.source.identifier,
                            "facets": dict(decision.flavor.flavor.facets),
                            "selected": decision.selected,
                            "reason": decision.reason,
                            "evidence": (
                                decision.evidence.branch_position
                                if decision.evidence is not None
                                else None
                            ),
                        }
                        for decision in resolution.decisions
                    ],
                    "backfill": dict(resolution.backfill.values),
                }
                for resolution in result.families
            ],
        }
