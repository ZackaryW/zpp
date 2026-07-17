import json

from zpp.core import governance, sidecar, worksets


def test_local_root_is_self_governed(tmp_path, fake_openspec):
    repo = tmp_path / "solo"
    (repo / "openspec").mkdir(parents=True)
    result = governance.resolve(repo)
    assert result["mode"] == "self-governed" and result["rule"] == 1


def test_committed_binding_beats_sidecar(tmp_path, fake_openspec, workspace_file):
    fake_openspec["stores"] = {"store-a": str(tmp_path / "sa"), "store-b": str(tmp_path / "sb")}
    repo = tmp_path / "repo-a"
    (repo / "zpp.toml").write_text('[governance]\nstore = "store-a"\n')
    worksets.do_import(workspace_file)
    worksets.bind("demo", "alpha", "store-b")  # personal view disagrees
    result = governance.resolve(repo)
    assert result["rule"] == 2 and result["store"] == "store-a"


def test_sidecar_binding_is_rule_three(tmp_path, fake_openspec, workspace_file):
    fake_openspec["stores"]["gov"] = str(tmp_path / "gov")
    worksets.do_import(workspace_file)
    worksets.bind("demo", "repo-b", "gov")
    result = governance.resolve(tmp_path / "repo-b")
    assert result["rule"] == 3 and result["binding"] == "personal"
    assert result["workset"] == "demo"


def test_ungoverned_is_explicit_and_dangling_store_warns(tmp_path, fake_openspec):
    assert governance.resolve(tmp_path / "nowhere")["mode"] == "ungoverned"
    repo = tmp_path / "dangling"
    repo.mkdir()
    (repo / "zpp.toml").write_text('[governance]\nstore = "gone"\n')
    result = governance.resolve(repo)
    assert result["store"] == "gone" and any("dangling" in w for w in result["warnings"])


def test_config_scalar_override_and_list_union(tmp_path, fake_openspec):
    store_root = tmp_path / "gov-store"
    store_root.mkdir()
    (store_root / "zpp.default.toml").write_text(
        '[zmem]\nmode = "present"\n[agent]\nshards = ["base"]\n'
    )
    fake_openspec["stores"]["gov"] = str(store_root)
    repo = tmp_path / "governed"
    repo.mkdir()
    (repo / "zpp.toml").write_text(
        '[governance]\nstore = "gov"\n[zmem]\nmode = "apply"\n[agent]\nshards = ["extra"]\n'
    )
    result = governance.resolve_config(repo)
    assert result["effective"]["zmem"]["mode"] == "apply"
    assert result["effective"]["agent"]["shards"] == ["base", "extra"]
    assert result["origins"]["zmem.mode"] == "repo"


def test_self_governed_repo_is_its_own_store_layer(tmp_path, fake_openspec):
    repo = tmp_path / "solo"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.default.toml").write_text('[zmem]\nmode = "present"\n')
    (repo / "zpp.toml").write_text('[zmem]\nmode = "apply"\n')
    result = governance.resolve_config(repo)
    assert result["mode"]["mode"] == "self-governed"
    assert result["effective"]["zmem"]["mode"] == "apply"
