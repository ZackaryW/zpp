"""Shared per-agent projection inventory for ZPP lifecycle commands."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

ABSENT_STATE = "absent"
CURRENT_STATE = "current"
CONFLICT_STATE = "conflict"
INSPECTION_FAILED_STATE = "inspection-failed"

#: ZPP never installed this target, so Agent Router refuses to replace it and
#: ZPP has no contract that could. Reported and preserved under every option.
PRESERVED_STATES = frozenset({"unmanaged"})


class LifecycleResult(Protocol):
    status: str

    def to_dict(self) -> dict[str, object]: ...


@dataclass(frozen=True, slots=True)
class LifecycleEntry:
    """One agent-owned projection with its lifecycle operations."""

    agent: str
    kind: str
    inspect: Callable[[], LifecycleResult] | None
    project: Callable[[], LifecycleResult] | None
    remove: Callable[[], LifecycleResult]
    #: Ownership-safe removal followed by projection, used to repair an owned
    #: target whose content no longer matches its ownership record.
    reproject: Callable[[], LifecycleResult] | None = None


@dataclass(frozen=True, slots=True)
class InspectedEntry:
    entry: LifecycleEntry
    status: str
    detail: str | None = None
    observed: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        record: dict[str, object] = {
            "agent": self.entry.agent,
            "asset": self.entry.kind,
            "status": self.status,
        }
        if self.detail is not None:
            record["error"] = self.detail
        if self.observed is not None:
            for key in ("scope", "destination"):
                if key in self.observed:
                    record[key] = self.observed[key]
        return record


@dataclass(frozen=True, slots=True)
class SelectedProjection:
    entry: LifecycleEntry
    status: str
    decision: str

    def to_dict(self) -> dict[str, object]:
        return {
            "agent": self.entry.agent,
            "asset": self.entry.kind,
            "status": self.status,
            "decision": self.decision,
        }


def inspect_entries(
    entries: Sequence[LifecycleEntry],
) -> tuple[InspectedEntry, ...]:
    """Observe each inspectable entry exactly once, recording failures."""
    inspected: list[InspectedEntry] = []
    for entry in entries:
        if entry.inspect is None:
            inspected.append(InspectedEntry(entry, "uninspectable"))
            continue
        try:
            result = entry.inspect()
            inspected.append(
                InspectedEntry(entry, result.status, observed=result.to_dict())
            )
        except Exception as error:
            inspected.append(InspectedEntry(entry, INSPECTION_FAILED_STATE, str(error)))
    return tuple(inspected)


def select_projections(
    inspected: Sequence[InspectedEntry],
    *,
    force: bool = False,
) -> tuple[SelectedProjection, ...]:
    """Decide which observed entries to reproject, preserve, or leave current."""
    selected: list[SelectedProjection] = []
    for item in inspected:
        if item.entry.project is None:
            continue
        if item.status in PRESERVED_STATES:
            decision = "preserve"
        elif item.status == CONFLICT_STATE:
            # Owned but modified. Repairable only by explicit force, because
            # silently overwriting a local edit is not synchronization.
            decision = "reproject" if force and item.entry.reproject else "conflict"
        elif item.status == CURRENT_STATE:
            decision = "project" if force else "current"
        else:
            decision = "project"
        selected.append(SelectedProjection(item.entry, item.status, decision))
    return tuple(selected)


def installed_agents(inspected: Sequence[InspectedEntry]) -> frozenset[str]:
    """Return agents carrying at least one present ZPP projection."""
    return frozenset(
        item.entry.agent
        for item in inspected
        if item.status not in {ABSENT_STATE, "uninspectable"}
    )


__all__ = [
    "ABSENT_STATE",
    "CONFLICT_STATE",
    "CURRENT_STATE",
    "INSPECTION_FAILED_STATE",
    "PRESERVED_STATES",
    "InspectedEntry",
    "LifecycleEntry",
    "LifecycleResult",
    "SelectedProjection",
    "inspect_entries",
    "installed_agents",
    "select_projections",
]
