from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

from zpp.core.models import (
    EffectiveFlavor,
    EffectiveTraitFamily,
    EvidenceRef,
    EvidenceResult,
    FacetContext,
    FamilyResolution,
    FlavorDecision,
    ResolutionContext,
    ResolutionResult,
    SelectionPolicy,
)


def evidence_ref(
    family: EffectiveTraitFamily,
    flavor: EffectiveFlavor,
    branch_position: int,
) -> EvidenceRef:
    return EvidenceRef(family.family, flavor.effective_position, branch_position)


def _contains(value: str | tuple[str, ...] | bool, expected: str) -> bool:
    if isinstance(value, str):
        return value == expected
    if isinstance(value, tuple):
        return expected in value
    return False


def _matches(flavor: EffectiveFlavor, context: ResolutionContext) -> bool:
    return all(
        key in context.values and _contains(context.values[key], expected)
        for key, expected in flavor.flavor.facets.items()
    )


def _compatible(flavor: EffectiveFlavor, context: ResolutionContext) -> bool:
    return all(
        key not in context.values or _contains(context.values[key], expected)
        for key, expected in flavor.flavor.facets.items()
    )


def _successful_evidence(
    family: EffectiveTraitFamily,
    flavor: EffectiveFlavor,
    evidence: Mapping[EvidenceRef, EvidenceResult],
) -> EvidenceRef | None:
    for branch_position, _ in enumerate(flavor.flavor.when):
        ref = evidence_ref(family, flavor, branch_position)
        result = evidence.get(ref)
        if result is not None and result.matched:
            return ref
    return None


def _dominates(left: EffectiveFlavor, right: EffectiveFlavor) -> bool:
    left_facets = set(left.flavor.facets.items())
    right_facets = set(right.flavor.facets.items())
    return right_facets < left_facets


def _select_extend(
    candidates: Sequence[EffectiveFlavor],
) -> tuple[EffectiveFlavor, ...]:
    retained: list[EffectiveFlavor] = []
    for position, candidate in enumerate(candidates):
        candidate_facets = set(candidate.flavor.facets.items())
        duplicate = any(
            set(earlier.flavor.facets.items()) == candidate_facets
            for earlier in candidates[:position]
        )
        dominated = any(
            _dominates(other, candidate)
            for other in candidates
            if other is not candidate
        )
        if not duplicate and not dominated:
            retained.append(candidate)
    return tuple(retained)


def _backfill(
    retained: Sequence[EffectiveFlavor],
    evidence_selected: Mapping[int, EvidenceRef],
    context: ResolutionContext,
) -> FacetContext:
    values: dict[str, list[str]] = {}
    provenance: dict[str, str] = {}
    for flavor in retained:
        if flavor.effective_position not in evidence_selected:
            continue
        for key, value in flavor.flavor.facets.items():
            if key in context.values:
                continue
            bucket = values.setdefault(key, [])
            if value not in bucket:
                bucket.append(value)
            provenance.setdefault(key, "evidence")
    normalized = {
        key: items[0] if len(items) == 1 else tuple(items)
        for key, items in values.items()
    }
    return FacetContext(
        values=MappingProxyType(normalized),
        provenance=MappingProxyType(provenance),
    )


def resolve_trait_family(
    family: EffectiveTraitFamily,
    context: ResolutionContext,
    evidence: Mapping[EvidenceRef, EvidenceResult],
) -> FamilyResolution:
    direct = [flavor for flavor in family.flavors if _matches(flavor, context)]
    evidence_selected: dict[int, EvidenceRef] = {}

    if family.selection is SelectionPolicy.FIRST_WIN:
        if direct:
            retained = (direct[0],)
        else:
            retained = ()
            for flavor in family.flavors:
                if not _compatible(flavor, context):
                    continue
                selected = _successful_evidence(family, flavor, evidence)
                if selected is not None:
                    evidence_selected[flavor.effective_position] = selected
                    retained = (flavor,)
                    break
    else:
        candidates = list(direct)
        direct_positions = {item.effective_position for item in direct}
        for flavor in family.flavors:
            if flavor.effective_position in direct_positions:
                continue
            if not _compatible(flavor, context):
                continue
            selected = _successful_evidence(family, flavor, evidence)
            if selected is not None:
                candidates.append(flavor)
                evidence_selected[flavor.effective_position] = selected
        candidates.sort(key=lambda item: item.effective_position)
        retained = (
            tuple(candidates)
            if family.selection is SelectionPolicy.ALL
            else _select_extend(candidates)
        )

    retained_positions = {item.effective_position for item in retained}
    candidate_positions = {
        item.effective_position for item in direct
    } | set(evidence_selected)
    decisions = tuple(
        FlavorDecision(
            flavor=flavor,
            selected=flavor.effective_position in retained_positions,
            reason=(
                "selected-evidence"
                if flavor.effective_position in retained_positions
                and flavor.effective_position in evidence_selected
                else "selected-direct"
                if flavor.effective_position in retained_positions
                else "dominated"
                if flavor.effective_position in candidate_positions
                and family.selection is SelectionPolicy.EXTEND
                else "shadowed"
                if flavor.effective_position in candidate_positions
                else "not-matched"
            ),
            evidence=evidence_selected.get(flavor.effective_position),
        )
        for flavor in family.flavors
    )
    return FamilyResolution(
        family=family.family,
        retained=retained,
        bodies=tuple(item.flavor.content.body for item in retained),
        backfill=_backfill(retained, evidence_selected, context),
        decisions=decisions,
    )


def resolve_traits(
    families: Sequence[EffectiveTraitFamily],
    context: ResolutionContext,
    evidence: Mapping[EvidenceRef, EvidenceResult],
) -> ResolutionResult:
    resolutions = tuple(
        resolve_trait_family(family, context, evidence) for family in families
    )
    merged_values = dict(context.values)
    merged_provenance = dict(context.provenance)
    merged_evidence = dict(context.evidence)
    merged_fingerprints = dict(context.fingerprints)

    for family in families:
        for flavor in family.flavors:
            for branch_position, _ in enumerate(flavor.flavor.when):
                ref = evidence_ref(family, flavor, branch_position)
                evidence_result = evidence.get(ref)
                if evidence_result is None:
                    continue
                keys = tuple(evidence_result.fingerprints)
                for key, value in evidence_result.facts.items():
                    if key in merged_values:
                        continue
                    merged_values[key] = value
                    merged_provenance[key] = "evidence"
                    merged_evidence[key] = keys
                    merged_fingerprints.update(evidence_result.fingerprints)

    for resolution in resolutions:
        for key, value in resolution.backfill.values.items():
            merged_values[key] = value
            merged_provenance[key] = resolution.backfill.provenance[key]
        for decision in resolution.decisions:
            if not decision.selected or decision.evidence is None:
                continue
            evidence_result = evidence[decision.evidence]
            keys = tuple(evidence_result.fingerprints)
            for key in decision.flavor.flavor.facets:
                if key not in resolution.backfill.values:
                    continue
                existing = list(merged_evidence.get(key, ()))
                existing.extend(item for item in keys if item not in existing)
                merged_evidence[key] = tuple(existing)
            merged_fingerprints.update(evidence_result.fingerprints)
    return ResolutionResult(
        families=resolutions,
        context=ResolutionContext(
            values=MappingProxyType(merged_values),
            provenance=MappingProxyType(merged_provenance),
            evidence=MappingProxyType(merged_evidence),
            fingerprints=MappingProxyType(merged_fingerprints),
        ),
    )
