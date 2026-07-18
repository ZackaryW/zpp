from pathlib import Path

from zpp.core import toolchain


def _self_governed(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "openspec").mkdir(parents=True)
    return repo


def test_exclude_filters_the_effective_table(zpp_home, tmp_path):
    repo = _self_governed(tmp_path)
    (repo / "zpp.toml").write_text('[doctor]\nexclude = ["codegraph", "node"]\n')
    table, warning = toolchain.effective_tools(repo)
    cmds = {t["cmd"] for t in table}
    assert "codegraph" not in cmds and "node" not in cmds
    assert "jq" in cmds and warning is None


def test_more_entries_map_to_detect_only(zpp_home, tmp_path):
    repo = _self_governed(tmp_path)
    (repo / "zpp.toml").write_text(
        '[[doctor.more]]\nwhich = "gh"\nsuccessnote = "gh drives PRs"\n'
    )
    table, _ = toolchain.effective_tools(repo)
    entry = next(t for t in table if t["cmd"] == "gh")
    assert entry["detect_only"] and entry["note"] == "gh drives PRs"


def test_tiers_union_more_entries(zpp_home, tmp_path):
    repo = _self_governed(tmp_path)
    (repo / "zpp.toml").write_text(
        '[[doctor.more]]\nwhich = "gh"\nsuccessnote = "repo"\n'
        '[[profiles.default.doctor.more]]\nwhich = "git"\nsuccessnote = "store"\n'
    )
    table, _ = toolchain.effective_tools(repo)
    cmds = {t["cmd"] for t in table}
    assert {"git", "gh"} <= cmds


def test_degraded_resolution_falls_back_to_builtin(zpp_home, tmp_path):
    repo = _self_governed(tmp_path)
    (repo / "zpp.toml").write_text("[doctor\nbroken")
    table, warning = toolchain.effective_tools(repo)
    assert {t["cmd"] for t in table} >= {"node", "jq", "openspec"}
    assert warning and "builtin table" in warning
