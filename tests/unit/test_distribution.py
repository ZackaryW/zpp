from __future__ import annotations

import tomllib
from pathlib import Path

from typer.testing import CliRunner

from zpp import __version__
from zpp.cli import app

REPOSITORY_ROOT = Path(__file__).parents[2]


def test_public_versions_match_project_distribution_metadata() -> None:
    project = tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0, result.output
    assert __version__ == project["version"]
    assert result.stdout.strip() == f"ZPP version {project['version']}"


def test_project_exposes_only_the_zpp_console_command() -> None:
    project = tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    assert project["scripts"] == {"zpp": "zpp.cli:app"}
    assert (
        sum(
            dependency.startswith("openspec-bundler ")
            for dependency in project["dependencies"]
        )
        == 1
    )
