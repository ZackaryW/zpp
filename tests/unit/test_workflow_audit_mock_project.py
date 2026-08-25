from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "src/zpp/artifacts/skills/companion/zpp-audit-workflows/scripts/mock_project.py"
)


def _run(*arguments: object) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *(str(argument) for argument in arguments)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert isinstance(value, dict)
    return value


def test_bootstrap_once_and_clone_fresh_mock_projects(tmp_path: Path) -> None:
    base = tmp_path / "base"
    first = tmp_path / "first"
    second = tmp_path / "second"

    bootstrapped = _run("bootstrap", "--base", base)
    first_clone = _run(
        "clone",
        "--base",
        base,
        "--destination",
        first,
        "--product-home",
        tmp_path / "home-first",
    )
    second_clone = _run(
        "clone",
        "--base",
        base,
        "--destination",
        second,
        "--product-home",
        tmp_path / "home-second",
    )

    assert bootstrapped["operation"] == "bootstrap"
    assert bootstrapped["root"] == str(base.resolve())
    assert first_clone["operation"] == second_clone["operation"] == "clone"
    assert first_clone["root"] == str(first.resolve())
    assert second_clone["root"] == str(second.resolve())
    assert first_clone["base_head"] == second_clone["base_head"]
    assert first_clone["product_home"] != second_clone["product_home"]
    assert (first / ".git").is_dir()
    assert (second / "openspec").is_dir()
