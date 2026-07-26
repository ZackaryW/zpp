"""Reference stores: durable per-workset assignment of read-only corpora.

Assignment records relevance; it never grants governance. These tests pin both
halves - that an assignment is durable and reportable, and that it changes no
resolution outcome.
"""

import pytest

from zpp.core import adapter, governance, sidecar, worksets


@pytest.fixture
def demo(fake_openspec, workspace_file, tmp_path):
    """An imported two-member workset plus a registered store outside it."""
    worksets.do_import(workspace_file)
    prod = tmp_path / "prod-env"
    prod.mkdir()
    fake_openspec["stores"]["prod-env"] = str(prod)
    return {"name": "demo", "prod": prod, "member": tmp_path / "repo-b"}


def test_assign_records_a_durable_reference_store(demo):
    worksets.assign_reference_store("demo", "prod-env")

    assert sidecar.load("demo")["reference_stores"] == ["prod-env"]


def test_assign_is_idempotent(demo):
    worksets.assign_reference_store("demo", "prod-env")
    worksets.assign_reference_store("demo", "prod-env")

    assert sidecar.load("demo")["reference_stores"] == ["prod-env"]


def test_assign_does_not_require_workspace_membership(demo):
    """The store sits outside the .code-workspace - the one-store member rule
    is never consulted."""
    worksets.assign_reference_store("demo", "prod-env")

    members = sidecar.load("demo")["members"]
    assert str(demo["prod"]) not in [m["path"] for m in members.values()]


def test_assign_unregistered_id_is_refused(demo):
    with pytest.raises(worksets.WorksetError, match="not registered"):
        worksets.assign_reference_store("demo", "ghost")

    assert sidecar.load("demo").get("reference_stores", []) == []


def test_unassign_removes_the_assignment(demo):
    worksets.assign_reference_store("demo", "prod-env")
    worksets.unassign_reference_store("demo", "prod-env")

    assert sidecar.load("demo")["reference_stores"] == []


def test_unassign_unknown_assignment_is_refused(demo):
    with pytest.raises(worksets.WorksetError, match="not assigned"):
        worksets.unassign_reference_store("demo", "prod-env")


def test_resolution_reports_assigned_reference_stores(demo):
    worksets.assign_reference_store("demo", "prod-env")

    result = governance.resolve(demo["member"])

    assert result["reference_stores"] == [
        {"id": "prod-env", "root": str(demo["prod"])}
    ]


def test_resolution_reports_empty_set_without_assignments(demo):
    result = governance.resolve(demo["member"])

    assert result["reference_stores"] == []


def test_resolution_reports_empty_set_outside_any_workset(fake_openspec, tmp_path):
    loose = tmp_path / "loose"
    loose.mkdir()

    result = governance.resolve(loose)

    assert result["reference_stores"] == []


def test_assignment_changes_no_resolution_outcome(demo):
    before = governance.resolve(demo["member"])
    worksets.assign_reference_store("demo", "prod-env")
    after = governance.resolve(demo["member"])

    governing = ("mode", "rule", "store", "binding", "root", "isolation")
    assert {k: before.get(k) for k in governing} == {k: after.get(k) for k in governing}


def test_no_registry_read_without_assignments(demo, monkeypatch):
    """Least privilege: an unassigned workset never reaches for the registry
    on the self-governed path."""
    (demo["member"] / "openspec").mkdir()
    monkeypatch.setattr(
        adapter, "store_list", lambda: pytest.fail("registry read without assignments")
    )

    result = governance.resolve(demo["member"])

    assert result["mode"] == "self-governed" and result["reference_stores"] == []


def test_assign_requires_an_existing_workset(fake_openspec):
    with pytest.raises(worksets.WorksetError, match="no sidecar"):
        worksets.assign_reference_store("ghost-workset", "prod-env")


def test_self_governed_member_still_resolves_reference_roots(demo):
    """Rule 1 skips the registry entirely, so an assignment there must reach
    for it on its own rather than report a rootless entry."""
    (demo["member"] / "openspec").mkdir()
    worksets.assign_reference_store("demo", "prod-env")

    result = governance.resolve(demo["member"])

    assert result["mode"] == "self-governed"
    assert result["reference_stores"] == [{"id": "prod-env", "root": str(demo["prod"])}]


def test_unregistered_assignment_resolves_with_a_null_root(demo, fake_openspec):
    worksets.assign_reference_store("demo", "prod-env")
    del fake_openspec["stores"]["prod-env"]

    result = governance.resolve(demo["member"])

    assert result["reference_stores"] == [{"id": "prod-env", "root": None}]


def test_status_reports_reference_stores(demo):
    worksets.assign_reference_store("demo", "prod-env")

    assert worksets.status("demo")["reference_stores"] == [
        {"id": "prod-env", "root": str(demo["prod"])}
    ]


def test_doctor_reports_an_unregistered_assignment(demo, fake_openspec):
    worksets.assign_reference_store("demo", "prod-env")
    del fake_openspec["stores"]["prod-env"]

    problems = [f["problem"] for f in worksets.doctor()]

    assert any("prod-env" in p and "not registered" in p for p in problems)


def test_doctor_reports_a_missing_assignment_root(demo):
    worksets.assign_reference_store("demo", "prod-env")
    demo["prod"].rmdir()

    problems = [f["problem"] for f in worksets.doctor()]

    assert any("prod-env" in p and "missing" in p for p in problems)


def test_doctor_is_silent_about_healthy_assignments(demo):
    worksets.assign_reference_store("demo", "prod-env")

    assert not [f for f in worksets.doctor() if "prod-env" in f["problem"]]
