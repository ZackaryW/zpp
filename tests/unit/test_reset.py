from dataclasses import dataclass

import pytest

from zpp.cli.reset import _reset_state, _reset_summary, _ResetReport
from zpp.utils.lifecycle import LifecycleEntry as _ResetProjection


@dataclass
class Result:
    status: str
    label: str

    def to_dict(self):
        return {"status": self.status, "label": self.label}


class Prepared:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def replace(self) -> None:
        self.events.append("replace")

    def discard(self) -> None:
        self.events.append("discard")


def test_reset_summary_counts_removed_and_absent_once() -> None:
    report = _ResetReport(
        inspections=(
            {"status": "current"},
            {"status": "absent"},
        ),
        removals=(
            {"status": "removed"},
            {"status": "absent"},
        ),
        state="replaced",
    )

    assert _reset_summary(report) == (
        "Reset complete: 1 removed, 2 already absent; Bundler state replaced."
    )


def projection(
    agent: str,
    kind: str,
    status: str,
    events: list[str],
    *,
    removal_error: str | None = None,
) -> _ResetProjection:
    def inspect():
        events.append(f"inspect:{agent}:{kind}")
        return Result(status, f"{agent}:{kind}")

    def remove():
        events.append(f"remove:{agent}:{kind}")
        if removal_error is not None:
            raise OSError(removal_error)
        return Result("removed", f"{agent}:{kind}")

    return _ResetProjection(agent, kind, inspect, None, remove)


def forced_projection(
    agent: str,
    kind: str,
    status: str,
    events: list[str],
    *,
    removal_error: str | None = None,
) -> _ResetProjection:
    def remove():
        events.append(f"force-remove:{agent}:{kind}")
        if removal_error is not None:
            raise OSError(removal_error)
        return Result(status, f"{agent}:{kind}")

    return _ResetProjection(agent, kind, None, None, remove)


def test_reset_preflights_every_projection_before_preparation_and_removal() -> None:
    events: list[str] = []
    projections = (
        projection("codex", "hook", "current", events),
        projection("codex", "skill", "absent", events),
        projection("claude", "hook", "current", events),
    )

    report = _reset_state(
        projections,
        prepare=lambda: events.append("prepare") or Prepared(events),
    )

    assert events == [
        "inspect:codex:hook",
        "inspect:codex:skill",
        "inspect:claude:hook",
        "prepare",
        "remove:codex:hook",
        "remove:claude:hook",
        "replace",
    ]
    assert report.state == "replaced"
    assert [item["status"] for item in report.inspections] == [
        "current",
        "absent",
        "current",
    ]


def test_reset_conflict_aborts_after_complete_inspection_without_mutation() -> None:
    events: list[str] = []
    projections = (
        projection("codex", "hook", "conflict", events),
        projection("claude", "hook", "absent", events),
    )

    with pytest.raises(ValueError, match=r"codex.*hook.*conflict"):
        _reset_state(
            projections,
            prepare=lambda: events.append("prepare") or Prepared(events),
        )

    assert events == ["inspect:codex:hook", "inspect:claude:hook"]


def test_reset_inspection_failure_still_inspects_remaining_catalog() -> None:
    events: list[str] = []

    def fail():
        events.append("inspect:codex:hook")
        raise OSError("cannot inspect")

    projections = (
        _ResetProjection("codex", "hook", fail, None, lambda: None),
        projection("claude", "skill", "absent", events),
    )

    with pytest.raises(ValueError, match="cannot inspect"):
        _reset_state(projections, prepare=lambda: Prepared(events))

    assert events == ["inspect:codex:hook", "inspect:claude:skill"]


def test_reset_aggregates_removal_failures_discards_stage_and_preserves_state() -> None:
    events: list[str] = []
    projections = (
        projection(
            "codex",
            "hook",
            "current",
            events,
            removal_error="codex failed",
        ),
        projection("claude", "hook", "current", events),
    )

    with pytest.raises(ValueError, match="codex failed"):
        _reset_state(projections, prepare=lambda: Prepared(events))

    assert events[-3:] == [
        "remove:codex:hook",
        "remove:claude:hook",
        "discard",
    ]
    assert "replace" not in events


def test_forced_removals_run_only_after_complete_standard_preflight() -> None:
    events: list[str] = []
    projections = (
        projection("codex", "hook", "current", events),
        forced_projection(
            "codex",
            "skill:openspec-apply-change",
            "removed",
            events,
        ),
        projection("claude", "skill", "absent", events),
        forced_projection(
            "claude",
            "skill:openspec-apply-change",
            "absent",
            events,
        ),
    )

    report = _reset_state(
        projections,
        prepare=lambda: events.append("prepare") or Prepared(events),
    )

    assert events == [
        "inspect:codex:hook",
        "inspect:claude:skill",
        "prepare",
        "remove:codex:hook",
        "force-remove:codex:skill:openspec-apply-change",
        "force-remove:claude:skill:openspec-apply-change",
        "replace",
    ]
    assert len(report.inspections) == 2
    assert [item["status"] for item in report.removals] == [
        "removed",
        "removed",
        "absent",
    ]


def test_forced_removal_failure_is_aggregated_and_preserves_state() -> None:
    events: list[str] = []
    projections = (
        projection("codex", "hook", "current", events),
        forced_projection(
            "codex",
            "skill:openspec-apply-change",
            "removed",
            events,
            removal_error="unmanaged skill",
        ),
        forced_projection(
            "pi",
            "skill:openspec-apply-change",
            "removed",
            events,
        ),
    )

    with pytest.raises(ValueError, match="unmanaged skill"):
        _reset_state(projections, prepare=lambda: Prepared(events))

    assert events[-3:] == [
        "force-remove:codex:skill:openspec-apply-change",
        "force-remove:pi:skill:openspec-apply-change",
        "discard",
    ]
    assert "replace" not in events


def test_reset_removes_an_owned_obsolete_tombstone_after_preflight() -> None:
    events: list[str] = []
    obsolete = projection(
        "codex",
        "obsolete-skill:zpp-workflow",
        "outdated",
        events,
    )

    report = _reset_state(
        (obsolete,),
        prepare=lambda: events.append("prepare") or Prepared(events),
    )

    assert events == [
        "inspect:codex:obsolete-skill:zpp-workflow",
        "prepare",
        "remove:codex:obsolete-skill:zpp-workflow",
        "replace",
    ]
    assert report.removals[0]["status"] == "removed"


def test_reset_preserves_an_unmanaged_obsolete_identity() -> None:
    events: list[str] = []
    obsolete = projection(
        "codex",
        "obsolete-skill:openspec-apply-change",
        "unmanaged",
        events,
    )

    report = _reset_state(
        (obsolete,),
        prepare=lambda: events.append("prepare") or Prepared(events),
    )

    assert events == [
        "inspect:codex:obsolete-skill:openspec-apply-change",
        "prepare",
        "replace",
    ]
    assert report.removals == (
        {
            "status": "unmanaged",
            "label": "codex:obsolete-skill:openspec-apply-change",
            "agent": "codex",
            "asset": "obsolete-skill:openspec-apply-change",
            "decision": "preserve",
        },
    )


def test_reset_preserves_an_ownership_unsafe_obsolete_identity() -> None:
    events: list[str] = []
    obsolete = projection(
        "codex",
        "obsolete-skill:zpp-workflow",
        "conflict",
        events,
        removal_error="mismatched ownership",
    )

    report = _reset_state(
        (obsolete,),
        prepare=lambda: events.append("prepare") or Prepared(events),
    )

    assert events[-2:] == [
        "remove:codex:obsolete-skill:zpp-workflow",
        "replace",
    ]
    assert report.removals[0]["status"] == "conflict"
    assert report.removals[0]["decision"] == "preserve"
    assert "mismatched ownership" in str(report.removals[0]["error"])
