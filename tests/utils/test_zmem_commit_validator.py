from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).parents[2]
SCRIPTS = ROOT / "src" / "zpp" / "artifacts" / "skills" / "zpp-commit-zmem" / "scripts"


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _bash() -> str | None:
    if sys.platform == "win32":
        git_bash = (
            Path.home() / "scoop" / "apps" / "git" / "current" / "bin" / "bash.exe"
        )
        if git_bash.is_file():
            return str(git_bash)
    return shutil.which("bash")


def _run_validator(
    runner: str,
    message: Path,
    *,
    require_zmem: bool,
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    option = ["--require-zmem"] if require_zmem else []
    if runner == "powershell":
        executable = _powershell()
        if executable is None:
            pytest.skip("PowerShell is unavailable")
        command = [
            executable,
            "-NoProfile",
            "-File",
            str(SCRIPTS / "check-commit-msg.ps1"),
            *option,
            "--file",
            str(message),
        ]
    else:
        executable = _bash()
        if executable is None:
            pytest.skip("a POSIX shell is unavailable")
        command = [
            executable,
            "--noprofile",
            "--norc",
            str(SCRIPTS / "check-commit-msg.sh"),
            *option,
            "--file",
            str(message),
        ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed, json.loads(completed.stdout)


@pytest.mark.parametrize("runner", ("powershell", "posix"))
def test_ordinary_conventional_commit_does_not_require_zmem(
    tmp_path: Path,
    runner: str,
) -> None:
    message = tmp_path / "message.txt"
    message.write_text("fix(workflow): allow ordinary commit\n", encoding="utf-8")

    completed, result = _run_validator(runner, message, require_zmem=False)

    assert completed.returncode == 0
    assert result["ok"] is True
    assert result["annotations"] == 0


@pytest.mark.parametrize("runner", ("powershell", "posix"))
def test_memory_bearing_validation_requires_zmem(
    tmp_path: Path,
    runner: str,
) -> None:
    message = tmp_path / "message.txt"
    message.write_text("fix(workflow): allow ordinary commit\n", encoding="utf-8")

    completed, result = _run_validator(runner, message, require_zmem=True)

    assert completed.returncode == 23
    assert result["ok"] is False
    assert result["code"] == 23
    assert result["annotations"] == 0


@pytest.mark.parametrize("runner", ("powershell", "posix"))
def test_memory_bearing_validation_accepts_canonical_annotation(
    tmp_path: Path,
    runner: str,
) -> None:
    message = tmp_path / "message.txt"
    message.write_text(
        "fix(workflow): preserve a decision\n\n"
        "zmem(DECISION): Record the changed direction and why.\n",
        encoding="utf-8",
    )

    completed, result = _run_validator(runner, message, require_zmem=True)

    assert completed.returncode == 0
    assert result["ok"] is True
    assert result["annotations"] == 1
