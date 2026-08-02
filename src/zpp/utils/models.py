from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Literal, TypedDict


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    location: tuple[str | int, ...]
    message: str
    source: Path | None = None


class ZppValidationError(ValueError):
    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        super().__init__("; ".join(issue.message for issue in issues))


@dataclass(frozen=True, slots=True)
class TraitDocument:
    name: str
    description: str
    body: str
    order: int | None = None
    config: dict[str, Any] = field(default_factory=dict)
    skill_lookup: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TriggerRule:
    trait: str
    which: str | None = None
    workspace_contain: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class LayerConfig:
    trait_overwrites: bool = False
    traits_config: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SavedIndex:
    bindings: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CacheWatch:
    cache_mtime_ns: int


class TraitRecord(TypedDict):
    description: str
    order: int | None
    config: dict[str, Any]
    skill_lookup: list[str]
    body: str
    source_sha256: str


class TraitIndex(TypedDict):
    schema_version: Literal[2]
    traits: dict[str, TraitRecord]


@dataclass(frozen=True, slots=True)
class CanonicalDirectory:
    display: Path
    resolved: Path
    key: str


@dataclass(frozen=True, slots=True)
class SavedBinding:
    name: str
    target: CanonicalDirectory


@dataclass(frozen=True, slots=True)
class AuthoredLayerPaths:
    root: Path
    config: Path
    triggers: Path
    traits: Path


@dataclass(frozen=True, slots=True)
class AuthoredLayerFile:
    relative_path: PurePosixPath
    content: bytes


@dataclass(frozen=True, slots=True)
class AuthoredLayerSnapshot:
    files: tuple[AuthoredLayerFile, ...]


@dataclass(frozen=True, slots=True)
class TraitCachePaths:
    root: Path
    index: Path
    watch: Path


@dataclass(frozen=True, slots=True)
class LayerRef:
    kind: Literal["global", "profile", "saved", "local"]
    root: Path
    name: str | None = None


@dataclass(frozen=True, slots=True)
class LayerInspection:
    state: Literal["absent", "complete", "partial", "invalid"]
    missing: tuple[Path, ...] = ()
    issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class CreationEntry:
    path: Path
    kind: Literal["directory", "text", "binary"]
    source: str | bytes | None = None


@dataclass(frozen=True, slots=True)
class CreationPlan:
    entries: tuple[CreationEntry, ...]


@dataclass(frozen=True, slots=True)
class LayerControls:
    triggers: tuple[TriggerRule, ...] = ()
    trait_overwrites: bool = False


AgentName = Literal["pi", "codex", "claude"]


@dataclass(frozen=True, slots=True)
class ConfirmedAgentSelection:
    agents: tuple[AgentName, ...]


@dataclass(frozen=True, slots=True)
class CancelledAgentSelection:
    pass


AgentSelection = ConfirmedAgentSelection | CancelledAgentSelection


class ManagedStateError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PackagedPiExtension:
    source: str
