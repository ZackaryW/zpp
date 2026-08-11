from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType


class SelectionPolicy(StrEnum):
    FIRST_WIN = "first-win"
    ALL = "all"
    EXTEND = "extend"


class ActivationMode(StrEnum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    ALWAYS_RUN = "always-run"


class CompositionMode(StrEnum):
    LAYERED = "layered"
    REPOSITORY_OVERWRITE = "repository-overwrite"


class SourceKind(StrEnum):
    REPOSITORY = "repository"
    SPACE = "space"
    GLOBAL = "global"


@dataclass(frozen=True, slots=True)
class SourceRef:
    kind: SourceKind
    identifier: str
    order: int = 0
    path: Path | None = None


@dataclass(frozen=True, slots=True)
class FileContains:
    path: str
    text: str


@dataclass(frozen=True, slots=True)
class EvidenceBranch:
    workspace_contains: str | None = None
    file_contains: FileContains | None = None
    which: str | None = None


@dataclass(frozen=True, slots=True)
class TraitContent:
    body: str


@dataclass(frozen=True, slots=True)
class TraitFlavor:
    facets: Mapping[str, str]
    content: TraitContent
    when: tuple[EvidenceBranch, ...] = ()
    position: int = 0


@dataclass(frozen=True, slots=True)
class TraitDocument:
    family: str
    selection: SelectionPolicy
    activation: ActivationMode
    mode: CompositionMode
    flavors: tuple[TraitFlavor, ...]
    source: SourceRef


@dataclass(frozen=True, slots=True)
class EffectiveFlavor:
    flavor: TraitFlavor
    source: SourceRef
    effective_position: int


@dataclass(frozen=True, slots=True)
class EffectiveTraitFamily:
    family: str
    selection: SelectionPolicy
    activation: ActivationMode
    policy_source: SourceRef
    mode: CompositionMode
    flavors: tuple[EffectiveFlavor, ...]
    excluded_sources: tuple[SourceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class FacetContext:
    values: Mapping[str, str | tuple[str, ...] | bool] = field(
        default_factory=lambda: MappingProxyType({})
    )
    provenance: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True, slots=True)
class ResolutionContext:
    values: Mapping[str, str | tuple[str, ...] | bool]
    provenance: Mapping[str, str]
    evidence: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    fingerprints: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    family: str
    flavor_position: int
    branch_position: int


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    matched: bool
    facts: Mapping[str, bool] = field(
        default_factory=lambda: MappingProxyType({})
    )
    fingerprints: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True, slots=True)
class FlavorDecision:
    flavor: EffectiveFlavor
    selected: bool
    reason: str
    evidence: EvidenceRef | None = None


@dataclass(frozen=True, slots=True)
class FamilyResolution:
    family: str
    retained: tuple[EffectiveFlavor, ...]
    bodies: tuple[str, ...]
    backfill: FacetContext
    decisions: tuple[FlavorDecision, ...]


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    families: tuple[FamilyResolution, ...]
    context: ResolutionContext


@dataclass(frozen=True, slots=True)
class TargetIdentity:
    repository: str


@dataclass(frozen=True, slots=True)
class FacetProvenance:
    source: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StoredContext:
    target: TargetIdentity
    values: Mapping[str, str | tuple[str, ...] | bool]
    provenance: Mapping[str, FacetProvenance]
    fingerprints: Mapping[str, str]


def frozen_mapping(values: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(values))
