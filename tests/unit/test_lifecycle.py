from __future__ import annotations

from dataclasses import dataclass

from zpp.utils.lifecycle import (
    LifecycleEntry,
    inspect_entries,
    installed_agents,
    select_projections,
)


@dataclass(frozen=True, slots=True)
class _Result:
    status: str

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status}


def _entry(
    agent: str,
    kind: str,
    status: str | None,
    *,
    projectable: bool = True,
) -> LifecycleEntry:
    return LifecycleEntry(
        agent=agent,
        kind=kind,
        inspect=(lambda: _Result(status)) if status is not None else None,
        project=(lambda: _Result("installed")) if projectable else None,
        remove=lambda: _Result("removed"),
        reproject=(lambda: _Result("updated")) if projectable else None,
    )


def test_inspect_entries_reports_status_without_reinspecting() -> None:
    calls: list[int] = []

    def counted() -> _Result:
        calls.append(1)
        return _Result("current")

    entry = LifecycleEntry("codex", "hook", counted, None, lambda: _Result("removed"))
    inspected = inspect_entries((entry,))

    assert [item.status for item in inspected] == ["current"]
    assert len(calls) == 1


def test_inspect_entries_records_failure_without_raising() -> None:
    def failing() -> _Result:
        raise OSError("unreadable")

    entry = LifecycleEntry("codex", "hook", failing, None, lambda: _Result("removed"))
    inspected = inspect_entries((entry,))

    assert inspected[0].status == "inspection-failed"
    assert "unreadable" in str(inspected[0].detail)


def test_select_projections_targets_only_drifted_entries() -> None:
    inspected = inspect_entries(
        (
            _entry("codex", "hook", "current"),
            _entry("codex", "skill", "outdated"),
            _entry("codex", "skill:a", "absent"),
        )
    )

    selected = select_projections(inspected)

    assert [item.entry.kind for item in selected if item.decision == "project"] == [
        "skill",
        "skill:a",
    ]
    assert [item.entry.kind for item in selected if item.decision == "current"] == [
        "hook"
    ]


def test_select_projections_under_force_targets_current_entries() -> None:
    inspected = inspect_entries((_entry("codex", "hook", "current"),))

    selected = select_projections(inspected, force=True)

    assert [item.decision for item in selected] == ["project"]


def test_select_projections_preserves_unmanaged_entries_under_force() -> None:
    inspected = inspect_entries((_entry("codex", "hook", "unmanaged"),))

    selected = select_projections(inspected, force=True)

    assert [item.decision for item in selected] == ["preserve"]


def test_select_projections_reports_a_modified_owned_entry_without_force() -> None:
    inspected = inspect_entries((_entry("codex", "skill", "conflict"),))

    selected = select_projections(inspected)

    assert [item.decision for item in selected] == ["conflict"]


def test_select_projections_repairs_a_modified_owned_entry_under_force() -> None:
    inspected = inspect_entries((_entry("codex", "skill", "conflict"),))

    selected = select_projections(inspected, force=True)

    assert [item.decision for item in selected] == ["reproject"]


def test_select_projections_reports_conflict_when_repair_is_unavailable() -> None:
    entry = LifecycleEntry(
        agent="codex",
        kind="skill",
        inspect=lambda: _Result("conflict"),
        project=lambda: _Result("installed"),
        remove=lambda: _Result("removed"),
        reproject=None,
    )

    selected = select_projections(inspect_entries((entry,)), force=True)

    assert [item.decision for item in selected] == ["conflict"]


def test_select_projections_omits_entries_without_a_projection() -> None:
    inspected = inspect_entries(
        (_entry("codex", "hook", "outdated", projectable=False),)
    )

    assert select_projections(inspected) == ()


def test_installed_agents_treats_any_present_projection_as_installed() -> None:
    inspected = inspect_entries(
        (
            _entry("codex", "hook", "absent"),
            _entry("codex", "skill", "current"),
            _entry("claude", "hook", "absent"),
            _entry("claude", "skill", "absent"),
        )
    )

    assert installed_agents(inspected) == frozenset({"codex"})


def test_installed_agents_counts_an_unmanaged_projection_as_present() -> None:
    inspected = inspect_entries((_entry("pi", "skill", "unmanaged"),))

    assert installed_agents(inspected) == frozenset({"pi"})
