from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest
from agent_router import Agent, Scope

import zpp.cli.lifecycle as lifecycle
from zpp.cli.lifecycle import (
    InstallationInspection,
    classify_installation,
    migration_result_status,
    preflight_first_install,
    reconcile_installations,
)
from zpp.utils.lifecycle import InspectedEntry, LifecycleEntry


@dataclass(frozen=True)
class Result:
    status: str

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status}


@pytest.mark.parametrize(
    ("current", "obsolete", "expected"),
    [
        (("absent",), ("absent",), "absent"),
        (("current", "absent"), ("absent",), "current"),
        (("conflict", "absent"), ("absent",), "current"),
        (("absent",), ("outdated", "absent"), "old-only"),
        (("absent",), ("unmanaged",), "obsolete-conflict"),
        (("absent",), ("conflict",), "obsolete-conflict"),
        (("absent",), ("inspection-failed",), "obsolete-conflict"),
    ],
)
def test_current_plus_obsolete_classification_matrix(
    current: tuple[str, ...], obsolete: tuple[str, ...], expected: str
) -> None:
    assert classify_installation(current, obsolete) == expected


@pytest.mark.parametrize(
    ("verified", "surviving", "conflicts", "expected"),
    [
        (True, (), False, "complete"),
        (False, (), False, "partial"),
        (True, ("zpp-workflow",), False, "partial"),
        (True, (), True, "conflict"),
    ],
)
def test_truthful_migration_result_aggregation(
    verified: bool,
    surviving: tuple[str, ...],
    conflicts: bool,
    expected: str,
) -> None:
    assert (
        migration_result_status(
            current_verified=verified,
            surviving_obsolete=surviving,
            conflicts=conflicts,
        )
        == expected
    )


def test_inventory_propagates_exact_project_scope_and_root(
    tmp_path: Path, monkeypatch
) -> None:
    calls: list[tuple[str, Scope, Path | None]] = []
    skill = SimpleNamespace(name="zpp-auto")
    hook = SimpleNamespace(name="zpp-traits")
    monkeypatch.setattr(lifecycle, "agent_router", lambda agent, root: object())
    monkeypatch.setattr(lifecycle, "packaged_workflow_skills", lambda: (skill,))
    monkeypatch.setattr(lifecycle, "packaged_companion_skills", lambda: ())
    monkeypatch.setattr(lifecycle, "packaged_workflow_hook", lambda agent: hook)
    monkeypatch.setattr(
        lifecycle,
        "inspect_workflow_skill",
        lambda router, asset, scope, project_root: (
            calls.append((asset.name, scope, project_root)) or Result("absent")
        ),
    )
    monkeypatch.setattr(
        lifecycle,
        "inspect_workflow_hook",
        lambda router, asset, scope, project_root: (
            calls.append((asset.name, scope, project_root)) or Result("absent")
        ),
    )

    entries = lifecycle.packaged_entries(
        (Agent.CODEX,),
        target=tmp_path,
        scope=Scope.PROJECT,
        project_root=tmp_path,
        include_companions=False,
    )
    for entry in entries:
        assert entry.inspect is not None
        entry.inspect()

    assert calls == [
        ("zpp-auto", Scope.PROJECT, tmp_path),
        ("zpp-traits", Scope.PROJECT, tmp_path),
    ]


def test_obsolete_inventory_propagates_scope_to_inspection_and_retirement(
    tmp_path: Path, monkeypatch
) -> None:
    calls: list[tuple[str, str, Scope, Path | None]] = []
    monkeypatch.setattr(lifecycle, "agent_router", lambda agent, root: object())
    monkeypatch.setattr(
        lifecycle,
        "inspect_workflow_skill",
        lambda router, asset, scope, project_root: (
            calls.append(("inspect", asset.name, scope, project_root))
            or Result("outdated")
        ),
    )
    monkeypatch.setattr(
        lifecycle,
        "remove_workflow_skill",
        lambda router, name, scope, project_root, force: (
            calls.append(("remove", name, scope, project_root)) or Result("removed")
        ),
    )

    entry = lifecycle.obsolete_entries(
        (Agent.CODEX,),
        target=tmp_path,
        scope=Scope.PROJECT,
        project_root=tmp_path,
    )[0]
    assert entry.inspect is not None
    entry.inspect()
    entry.remove()

    assert calls == [
        ("inspect", "zpp-workflow", Scope.PROJECT, tmp_path),
        ("remove", "zpp-workflow", Scope.PROJECT, tmp_path),
    ]


def _entry(
    kind: str,
    state: dict[str, str],
    events: list[str],
    *,
    obsolete: bool = False,
    project_failure: bool = False,
    remove_failure: bool = False,
) -> LifecycleEntry:
    def inspect() -> Result:
        events.append(f"inspect:{kind}:{state[kind]}")
        return Result(state[kind])

    def project() -> Result:
        events.append(f"project:{kind}")
        if project_failure:
            raise RuntimeError("projection failed")
        state[kind] = "current"
        return Result("installed")

    def remove() -> Result:
        events.append(f"remove:{kind}")
        if remove_failure:
            raise RuntimeError("retirement failed")
        state[kind] = "absent"
        return Result("removed")

    return LifecycleEntry(
        "codex",
        kind,
        inspect,
        None if obsolete else project,
        remove,
        None if obsolete else project,
    )


def _inspection(
    current: LifecycleEntry, obsolete: LifecycleEntry
) -> InstallationInspection:
    return InstallationInspection(
        Agent.CODEX,
        (InspectedEntry(current, current.inspect().status),),
        (InspectedEntry(obsolete, obsolete.inspect().status),),
    )


def test_reconciliation_verifies_current_family_before_retiring_obsolete() -> None:
    events: list[str] = []
    state = {"skill:zpp-auto": "absent", "obsolete-skill:zpp-workflow": "outdated"}
    current = _entry("skill:zpp-auto", state, events)
    obsolete = _entry("obsolete-skill:zpp-workflow", state, events, obsolete=True)
    inspection = _inspection(current, obsolete)
    events.clear()

    records = reconcile_installations((inspection,), absent="install")

    assert events == [
        "project:skill:zpp-auto",
        "inspect:skill:zpp-auto:current",
        "remove:obsolete-skill:zpp-workflow",
        "inspect:obsolete-skill:zpp-workflow:absent",
    ]
    assert [record["status"] for record in records] == [
        "installed",
        "removed",
        "complete",
    ]
    assert records[-1]["current"] == ["skill:zpp-auto"]
    assert records[-1]["surviving_obsolete"] == []


def test_current_projection_failure_preserves_every_obsolete_entry() -> None:
    events: list[str] = []
    state = {"skill:zpp-auto": "absent", "obsolete-skill:zpp-workflow": "outdated"}
    current = _entry("skill:zpp-auto", state, events, project_failure=True)
    obsolete = _entry("obsolete-skill:zpp-workflow", state, events, obsolete=True)
    inspection = _inspection(current, obsolete)
    events.clear()

    records = reconcile_installations((inspection,), absent="install")

    assert "remove:obsolete-skill:zpp-workflow" not in events
    assert records[-2]["decision"] == "preserve"
    assert records[-2]["reason"] == "current-family-not-verified"
    assert records[-1]["status"] == "partial"
    assert records[-1]["surviving_obsolete"] == ["obsolete-skill:zpp-workflow"]


def test_retirement_failure_reports_exact_surviving_obsolete_identity() -> None:
    events: list[str] = []
    state = {"skill:zpp-auto": "current", "obsolete-skill:zpp-workflow": "outdated"}
    current = _entry("skill:zpp-auto", state, events)
    obsolete = _entry(
        "obsolete-skill:zpp-workflow",
        state,
        events,
        obsolete=True,
        remove_failure=True,
    )
    inspection = _inspection(current, obsolete)

    records = reconcile_installations((inspection,))

    assert records[-2]["asset"] == "obsolete-skill:zpp-workflow"
    assert records[-2]["status"] == "retirement-failed"
    assert records[-2]["decision"] == "preserve"
    assert records[-1] == {
        "agent": "codex",
        "asset": "migration",
        "status": "partial",
        "decision": "migrate",
        "origin": "current",
        "current": ["skill:zpp-auto"],
        "surviving_obsolete": ["obsolete-skill:zpp-workflow"],
        "failures": ["obsolete-skill:zpp-workflow"],
    }


@pytest.mark.parametrize("status", ["current", "outdated"])
def test_first_install_directs_owned_existing_projection_to_update(status: str) -> None:
    state = {"skill:zpp-auto": status, "obsolete-skill:zpp-workflow": "absent"}
    events: list[str] = []
    inspection = _inspection(
        _entry("skill:zpp-auto", state, events),
        _entry("obsolete-skill:zpp-workflow", state, events, obsolete=True),
    )

    assert preflight_first_install((inspection,)) == {
        "agent": "codex",
        "asset": "skill:zpp-auto",
        "scope": "unknown",
        "project_root": "-",
        "destination": "unknown",
        "status": status,
        "reason": "already-installed; run `zpp workflow update`",
    }


def test_first_install_reports_exact_unmanaged_conflict() -> None:
    state = {"skill:zpp-auto": "unmanaged", "obsolete-skill:zpp-workflow": "absent"}
    events: list[str] = []
    inspection = _inspection(
        _entry("skill:zpp-auto", state, events),
        _entry("obsolete-skill:zpp-workflow", state, events, obsolete=True),
    )

    assert preflight_first_install((inspection,)) == {
        "agent": "codex",
        "asset": "skill:zpp-auto",
        "scope": "unknown",
        "project_root": "-",
        "destination": "unknown",
        "status": "unmanaged",
        "reason": "conflicting destination (unmanaged)",
    }


def test_first_install_conflict_carries_exact_agent_scope_root_and_destination(
    tmp_path: Path,
) -> None:
    entry = _entry(
        "skill:zpp-auto",
        {"skill:zpp-auto": "unmanaged"},
        [],
    )
    destination = tmp_path / ".agents" / "skills"
    inspection = InstallationInspection(
        Agent.CODEX,
        (
            InspectedEntry(
                entry,
                "unmanaged",
                observed={
                    "status": "unmanaged",
                    "scope": "project",
                    "destination": str(destination),
                },
            ),
        ),
        (),
        Scope.PROJECT,
        tmp_path,
    )

    assert preflight_first_install((inspection,)) == {
        "agent": "codex",
        "asset": "skill:zpp-auto",
        "scope": "project",
        "project_root": str(tmp_path),
        "destination": str(destination),
        "status": "unmanaged",
        "reason": "conflicting destination (unmanaged)",
    }


def test_project_update_uses_explicit_agent_router_update_for_present_skills(
    tmp_path: Path, monkeypatch
) -> None:
    calls = []
    skill = SimpleNamespace(name="zpp-auto")
    hook = SimpleNamespace(name="zpp-traits")
    monkeypatch.setattr(lifecycle, "agent_router", lambda agent, root: object())
    monkeypatch.setattr(lifecycle, "packaged_workflow_skills", lambda: (skill,))
    monkeypatch.setattr(lifecycle, "packaged_companion_skills", lambda: ())
    monkeypatch.setattr(lifecycle, "packaged_workflow_hook", lambda agent: hook)
    monkeypatch.setattr(
        lifecycle,
        "project_workflow_skill",
        lambda router, asset, scope, project_root, replace_project=False: (
            calls.append((asset.name, scope, project_root, replace_project))
            or Result("updated")
        ),
    )

    entry = lifecycle.packaged_entries(
        (Agent.CODEX,),
        target=tmp_path,
        scope=Scope.PROJECT,
        project_root=tmp_path,
        include_companions=False,
        explicit_project_update=True,
    )[0]
    assert entry.reproject is not None
    entry.reproject()

    assert calls == [("zpp-auto", Scope.PROJECT, tmp_path, True)]
