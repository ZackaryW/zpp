import json

from zpp.core import sidecar, snapshot, worksets


def test_auto_snapshot_before_sync_enables_recovery(fake_openspec, workspace_file, tmp_path):
    worksets.do_import(workspace_file)
    before = sidecar.load("demo")
    (tmp_path / "repo-c").mkdir()
    data = json.loads(workspace_file.read_text())
    data["folders"] = [{"path": "repo-c"}]  # unwanted rewrite
    workspace_file.write_text(json.dumps(data))
    worksets.sync_apply("demo", worksets.sync_plan("demo"))
    snaps = snapshot.list_snapshots("demo")
    assert snaps[-1]["trigger"] == "sync"
    snapshot.restore("demo", snaps[-1]["id"])
    assert sidecar.load("demo")["members"] == before["members"]


def test_restore_leaves_workspace_file_untouched_by_default(fake_openspec, workspace_file):
    worksets.do_import(workspace_file)
    snap_id = snapshot.take("demo", "manual")
    original = workspace_file.read_text()
    workspace_file.write_text("{mangled")
    written = snapshot.restore("demo", snap_id)
    assert workspace_file.read_text() == "{mangled"
    assert all(not p.endswith(".code-workspace") for p in written)
    written = snapshot.restore("demo", snap_id, workspace_file=True)
    assert workspace_file.read_text() == original


def test_snapshot_provenance(fake_openspec, workspace_file):
    worksets.do_import(workspace_file)
    snapshot.take("demo", "manual", note="before surgery")
    triggers = {s["trigger"] for s in snapshot.list_snapshots("demo")}
    assert "manual" in triggers
    assert snapshot.take("nonexistent", "manual") is None
