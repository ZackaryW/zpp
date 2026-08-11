from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from zpp.cli import app

runner = CliRunner()


def test_no_space_repository_resolution_selects_python_and_flutter(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    local = repository / ".zpp"
    local.mkdir()
    (local / "zpp.toml").write_text(
        "[facet]\nlanguage=['python', 'flutter']\nbuild_tool='uv'\n"
    )
    before = sorted(path.relative_to(repository) for path in repository.rglob("*"))

    result = runner.invoke(
        app,
        [
            "--path",
            str(tmp_path / "state"),
            "resolve",
            str(repository),
            "--stage",
            "wire",
            "--explain",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    selected = [(item["family"], item["body"]) for item in payload["bodies"]]
    bdd = [body for family, body in selected if family == "bdd"]
    assert any("Behave" in body for body in bdd)
    assert any("Gherkin" in body for body in bdd)
    assert len(bdd) == 2
    context = json.loads(payload["ZPP_CONTEXT"])
    assert context["facets"]["language"] == ["python", "flutter"]
    assert context["facets"]["stage"] == "wire"
    assert payload["explanation"]["families"]
    after = sorted(path.relative_to(repository) for path in repository.rglob("*"))
    assert after == before


def test_invalid_repository_trait_reports_clean_cli_error(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    traits = repository / ".zpp" / "traits"
    traits.mkdir(parents=True)
    (traits / "bdd.toml").write_text("[meta]\nselection='first-win'\n[[trait]]\n")

    result = runner.invoke(
        app,
        ["--path", str(tmp_path / "state"), "resolve", str(repository)],
    )

    assert result.exit_code == 2
    assert "invalid trait document" in result.output
    assert "Traceback" not in result.output
