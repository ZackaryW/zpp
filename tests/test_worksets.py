import json

import pytest

from zpp.core import sidecar, snapshot, worksets


def test_import_creates_workset_and_sidecar(fake_openspec, workspace_file):
    name, members = worksets.do_import(workspace_file)
    assert name == "demo" and len(members) == 2
    assert "demo" in fake_openspec["worksets"]
    side = sidecar.load("demo")
    assert side["workspace"] == str(workspace_file)
    assert set(side["members"]) == {"alpha", "repo-b"}


def test_import_missing_folder_fails_without_partial(fake_openspec, workspace_file, tmp_path):
    (tmp_path / "repo-b").rmdir()
    with pytest.raises(worksets.WorksetError, match="missing member folders"):
        worksets.do_import(workspace_file)
    assert fake_openspec["worksets"] == {}  # no partial workset created
    name, members = worksets.do_import(workspace_file, partial=True)
    assert [m["name"] for m in members] == ["alpha"]


def test_import_name_collision_refuses(fake_openspec, workspace_file):
    worksets.do_import(workspace_file)
    with pytest.raises(worksets.WorksetError, match="already exists"):
        worksets.do_import(workspace_file)


def test_import_starts_with_no_profiles(fake_openspec, workspace_file):
    worksets.do_import(workspace_file)
    side = sidecar.load("demo")
    assert side.get("profiles", {}) == {}
    assert all("profile" not in m for m in side["members"].values())


def test_sync_folder_added(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    (tmp_path / "repo-c").mkdir()
    data = json.loads(workspace_file.read_text())
    data["folders"].append({"path": "repo-c"})
    workspace_file.write_text(json.dumps(data))
    plan = worksets.sync_plan("demo")
    assert [m["name"] for m in plan["added"]] == ["repo-c"]
    assert not plan["destructive"]
    worksets.sync_apply("demo", plan)
    assert "repo-c" in sidecar.load("demo")["members"]
    assert len(fake_openspec["worksets"]["demo"]) == 3


def test_sync_labeled_rename_preserves_profile_pointer(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    side = sidecar.load("demo")
    side["members"]["alpha"]["profile"] = "webapp"
    sidecar.save("demo", side)
    (tmp_path / "repo-a").rename(tmp_path / "repo-a2")
    data = json.loads(workspace_file.read_text())
    data["folders"][0]["path"] = "repo-a2"  # label 'alpha' unchanged
    workspace_file.write_text(json.dumps(data))
    plan = worksets.sync_plan("demo")
    assert [m["name"] for m in plan["moved"]] == ["alpha"]
    assert not plan["destructive"]
    worksets.sync_apply("demo", plan)
    member = sidecar.load("demo")["members"]["alpha"]
    assert member["profile"] == "webapp" and member["path"].endswith("repo-a2")


def test_sync_unlabeled_replace_dropping_pointer_is_destructive(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    side = sidecar.load("demo")
    side["members"]["repo-b"]["profile"] = "special"
    sidecar.save("demo", side)
    (tmp_path / "repo-c").mkdir()
    data = json.loads(workspace_file.read_text())
    data["folders"][1] = {"path": "repo-c"}  # unlabeled repo-b replaced
    workspace_file.write_text(json.dumps(data))
    plan = worksets.sync_plan("demo")
    assert "repo-b" in plan["destructive"]  # dropping a profile pointer needs confirmation


def test_sync_source_file_missing(fake_openspec, workspace_file):
    worksets.do_import(workspace_file)
    workspace_file.unlink()
    with pytest.raises(worksets.WorksetError, match="moved or deleted"):
        worksets.sync_plan("demo")


def test_doctor_flags_drift(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    fake_openspec["worksets"].pop("demo")  # removed behind zpp's back
    problems = [f["problem"] for f in worksets.doctor()]
    assert any("no openspec workset" in p for p in problems)


def test_status_detects_store_member(fake_openspec, workspace_file, tmp_path):
    store_marker = tmp_path / "repo-a" / ".openspec-store"
    store_marker.mkdir()
    (store_marker / "store.yaml").write_text("version: 1\nid: alpha\n")
    worksets.do_import(workspace_file)
    data = worksets.status("demo")
    roles = {m["name"]: m["is_store"] for m in data["members"]}
    assert roles == {"alpha": True, "repo-b": False}


def test_doctor_flags_shared_file_phantom_member(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    shared = workspace_file.parent / "demo.zpp-workset"
    shared.write_text('[profiles.default]\n[members.ghost]\nprofile = "default"\n')
    problems = [f["problem"] for f in worksets.doctor()]
    assert any("ghost" in p and "not a member" in p for p in problems)
