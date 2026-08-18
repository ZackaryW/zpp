"""Reusable lifecycle for capability roots that exercise ZPP coordination."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.cli import app


class CoordinationEnvironment:
    """An isolated ZPP home plus disposable Git worktrees."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.home = self.base / "home"
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def worktree(self, name: str = "project") -> Path:
        root = self.base / name
        root.mkdir(parents=True)
        self.git(root, "init", "--quiet")
        self.git(root, "config", "user.email", "test@example.com")
        self.git(root, "config", "user.name", "Test")
        (root / "tracked.txt").write_text("base\n", encoding="utf-8")
        self.git(root, "add", ".")
        self.git(root, "commit", "--quiet", "-m", "base")
        return root

    @staticmethod
    def git(root: Path, *arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)

    def run(self, *arguments: str):
        return self.runner.invoke(app, ["--path", str(self.home), *arguments])

    def workspace(self, *arguments: str):
        return self.run("workspace", *arguments)

    def workspace_json(self, *arguments: str) -> dict:
        result = self.workspace(*arguments)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def resolve_json(self, *arguments: str) -> dict:
        result = self.run("resolve", "--explain", *arguments)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def state(self) -> dict:
        return self.workspace_json("status")
