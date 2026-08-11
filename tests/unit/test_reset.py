from dataclasses import dataclass

import pytest

from zpp.cli.reset import _reset_state, _ResetProjection


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

    return _ResetProjection(agent, kind, inspect, remove)


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

    return _ResetProjection(agent, kind, None, remove)


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
        _ResetProjection("codex", "hook", fail, lambda: None),
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
