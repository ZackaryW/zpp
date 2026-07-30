from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
