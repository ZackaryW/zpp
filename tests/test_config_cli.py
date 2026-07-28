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


def test_scoped_sources_json_has_one_consistent_ordered_shape(
    zpp_home, tmp_path, fake_openspec
):
    repo = tmp_path / "repo"
    scope = repo / "sdk" / "python"
    (repo / "openspec").mkdir(parents=True)
    scope.mkdir(parents=True)
    (repo / "zpp.toml").write_text('[tdd]\nstack = "rust"\n')
    (scope / "zpp.toml").write_text('[tdd]\nstack = "python"\n')

    result = runner.invoke(
        app,
        ["config", "resolve", str(scope), "--sources", "--json"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    source = str((scope / "zpp.toml").resolve())
    assert data["scoped_layers"] == [
        {"source": source, "config": {"tdd": {"stack": "python"}}}
    ]
    assert data["origins"]["tdd.stack"] == source
    assert data["effective"]["tdd"]["stack"] == "python"


def test_nested_authority_cli_failure_is_compact_and_precise(
    zpp_home, tmp_path, fake_openspec
):
    repo = tmp_path / "repo"
    scope = repo / "sdk" / "python"
    (repo / "openspec").mkdir(parents=True)
    scope.mkdir(parents=True)
    config = scope / "zpp.toml"
    config.write_text(
        '[governance]\nstore = "other"\n[profiles.default]\nname = "nested"\n'
    )

    result = runner.invoke(app, ["config", "resolve", str(scope), "--json"])

    assert result.exit_code == 1
    assert str(config.resolve()) in result.output
    assert "[governance]" in result.output
    assert "[profiles]" in result.output
    assert "Traceback" not in result.output
