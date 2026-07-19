from pathlib import Path

from typer.testing import CliRunner

from zpp.cli import app
from zpp.core import toolchain

runner = CliRunner()


def _self_governed(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "openspec").mkdir(parents=True)
    return repo


def test_doctor_exits_zero_when_only_optional_missing(zpp_home, tmp_path, monkeypatch):
    """An absent optional tool must not fail `zpp doctor` - it reports the row
    but the command still succeeds."""
    report = [
        {"tool": "node", "present": True, "version": "v20", "hint": None},
        {"tool": "saucepan", "present": False, "version": None, "hint": "h",
         "optional": True},
    ]
    monkeypatch.setattr(toolchain, "doctor", lambda path=Path("."): (report, None))
    result = runner.invoke(app, ["doctor", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "saucepan" in result.output


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
