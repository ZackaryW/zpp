"""`zpp config resolve` surface: the empty-config authoring hint (human only)."""

import json

from typer.testing import CliRunner

from zpp.cli import app

runner = CliRunner()


def test_empty_resolve_hints_authoring(zpp_home, tmp_path, fake_openspec):
    plain = tmp_path / "plain"
    plain.mkdir()
    result = runner.invoke(app, ["config", "resolve", str(plain)])
    assert result.exit_code == 0, result.output
    assert "zpp.toml" in result.output and "author" in result.output.lower()


def test_empty_resolve_json_stays_bare(zpp_home, tmp_path, fake_openspec):
    plain = tmp_path / "plain"
    plain.mkdir()
    result = runner.invoke(app, ["config", "resolve", str(plain), "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {}
    assert "author" not in result.output.lower()


def test_nonempty_resolve_has_no_hint(zpp_home, tmp_path, fake_openspec):
    repo = tmp_path / "repo"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.toml").write_text('[tdd]\nstack = "python"\n')
    result = runner.invoke(app, ["config", "resolve", str(repo)])
    assert result.exit_code == 0, result.output
    assert "author" not in result.output.lower()
    assert "tdd.stack" in result.output
