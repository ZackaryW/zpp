from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

from zpp.core.models import (
    PROTECTED_CONTEXT_KEYS,
    ActivationMode,
    ContextMember,
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


class UnknownTraitFamilyError(ValueError):
    pass


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


def _enrichment_compatible(
    flavor: EffectiveFlavor,
    context: ResolutionContext,
) -> bool:
    for key, expected in flavor.flavor.facets.items():
        if key not in context.values or _contains(context.values[key], expected):
            continue
        if context.provenance.get(key) == "evidence" or (
            isinstance(context.values[key], tuple)
            and context.provenance.get(key) != "invocation"
        ):
            continue
        return False
    return True


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


def _enrich_resolution_context(
    families: Sequence[EffectiveTraitFamily],
    context: ResolutionContext,
    evidence: Mapping[EvidenceRef, EvidenceResult],
) -> tuple[ResolutionContext, Mapping[tuple[str, int], EvidenceRef]]:
    """Publish observed facts and one bounded pass of evidence-derived facets."""
    merged_values = dict(context.values)
    merged_provenance = dict(context.provenance)
    merged_evidence = dict(context.evidence)
    merged_fingerprints = dict(context.fingerprints)
    merged_members = {
        key: list(
            context.members.get(
                key,
                tuple(
                    ContextMember(
                        value,
                        context.provenance[key],
                        context.evidence.get(key, ()),
                    )
                    for value in (
                        item if isinstance(item, tuple) else (item,)
                    )
                ),
            )
        )
        for key, item in context.values.items()
    }
    contributors: list[tuple[EffectiveFlavor, EvidenceRef]] = []

    for family in families:
        if family.activation is ActivationMode.ALWAYS_RUN:
            continue

        direct_positions = {
            flavor.effective_position
            for flavor in family.flavors
            if _matches(flavor, context)
        }
        if family.selection is SelectionPolicy.FIRST_WIN and direct_positions:
            candidates: Sequence[EffectiveFlavor] = ()
        else:
            candidates = tuple(
                flavor
                for flavor in family.flavors
                if flavor.effective_position not in direct_positions
                and _enrichment_compatible(flavor, context)
            )

        for flavor in family.flavors:
            for branch_position, _ in enumerate(flavor.flavor.when):
                ref = evidence_ref(family, flavor, branch_position)
                evidence_result = evidence.get(ref)
                if evidence_result is None:
                    continue
                keys = tuple(evidence_result.fingerprints)
                for key, value in evidence_result.facts.items():
                    if key in PROTECTED_CONTEXT_KEYS:
                        continue
                    if key in merged_values:
                        continue
                    merged_values[key] = value
                    merged_provenance[key] = "evidence"
                    merged_evidence[key] = keys
                    merged_members[key] = [ContextMember(value, "evidence", keys)]
                    merged_fingerprints.update(evidence_result.fingerprints)

        for flavor in candidates:
            selected = _successful_evidence(family, flavor, evidence)
            if selected is None:
                continue
            contributors.append((flavor, selected))
            if family.selection is SelectionPolicy.FIRST_WIN:
                break

    for flavor, selected in contributors:
        evidence_result = evidence[selected]
        keys = tuple(evidence_result.fingerprints)
        merged_fingerprints.update(evidence_result.fingerprints)
        for key, value in flavor.flavor.facets.items():
            if key in PROTECTED_CONTEXT_KEYS:
                continue
            if key in context.values:
                existing = context.values[key]
                source = context.provenance.get(key)
                if source == "invocation" or (
                    not isinstance(existing, tuple) and source != "evidence"
                ):
                    continue
            members = merged_members.setdefault(key, [])
            if any(member.value == value for member in members):
                continue
            members.append(ContextMember(value, "evidence", keys))
            values = tuple(member.value for member in members)
            merged_values[key] = values[0] if len(values) == 1 else values
            merged_provenance.setdefault(key, "evidence")
            evidence_keys: list[str] = []
            for member in members:
                evidence_keys.extend(
                    item for item in member.evidence if item not in evidence_keys
                )
            if evidence_keys:
                merged_evidence[key] = tuple(evidence_keys)

    enriched = ResolutionContext(
        values=MappingProxyType(merged_values),
        provenance=MappingProxyType(merged_provenance),
        evidence=MappingProxyType(merged_evidence),
        fingerprints=MappingProxyType(merged_fingerprints),
        members=MappingProxyType(
            {key: tuple(members) for key, members in merged_members.items()}
        ),
    )
    references = {
        (selected.family, flavor.effective_position): selected
        for flavor, selected in contributors
    }
    return enriched, MappingProxyType(references)


def enrich_resolution_context(
    families: Sequence[EffectiveTraitFamily],
    context: ResolutionContext,
    evidence: Mapping[EvidenceRef, EvidenceResult],
) -> ResolutionContext:
    enriched, _ = _enrich_resolution_context(families, context, evidence)
    return enriched


def resolve_trait_family(
    family: EffectiveTraitFamily,
    context: ResolutionContext,
    evidence: Mapping[EvidenceRef, EvidenceResult],
    *,
    activate_all: bool = False,
    preselected_evidence: Mapping[int, EvidenceRef] | None = None,
) -> FamilyResolution:
    direct = (
        list(family.flavors)
        if activate_all
        else [flavor for flavor in family.flavors if _matches(flavor, context)]
    )
    evidence_selected = dict(preselected_evidence or {})

    if family.selection is SelectionPolicy.FIRST_WIN:
        if direct:
            retained = (direct[0],)
        elif not activate_all:
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
                "selected-always-run"
                if activate_all
                and flavor.effective_position in retained_positions
                else "selected-evidence"
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
    *,
    requested: Sequence[str] | None = None,
) -> ResolutionResult:
    selected_families = select_trait_families(families, requested)
    enriched_context, enrichment_evidence = _enrich_resolution_context(
        selected_families,
        context,
        evidence,
    )
    resolutions = tuple(
        resolve_trait_family(
            family,
            enriched_context,
            evidence,
            activate_all=family.activation is ActivationMode.ALWAYS_RUN,
            preselected_evidence={
                position: selected
                for (family_name, position), selected in enrichment_evidence.items()
                if family_name == family.family
            },
        )
        for family in selected_families
    )
    return ResolutionResult(
        families=resolutions,
        context=enriched_context,
    )


def select_trait_families(
    families: Sequence[EffectiveTraitFamily],
    requested: Sequence[str] | None,
) -> tuple[EffectiveTraitFamily, ...]:
    if requested is None:
        return tuple(
            family
            for family in families
            if family.activation is not ActivationMode.MANUAL
        )

    by_name = {family.family: family for family in families}
    names = tuple(dict.fromkeys(requested))
    unknown = tuple(name for name in names if name not in by_name)
    if unknown:
        rendered = ", ".join(unknown)
        raise UnknownTraitFamilyError(f"unknown trait family: {rendered}")
    return tuple(by_name[name] for name in names)
