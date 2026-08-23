"""Capability-local verification subjects for repository behavior verification.

Mapping validation, impact selection, and provider adapter case matrices live in
`tests/unit/test_behavior_*.py`. These subjects drive the public `zpp behave`
boundary, proving that declared targets, gates, and selection modes reach a
provider invocation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.cli import app

ECHO_ARGV = json.dumps(sys.executable)

MAPPING = (
    "version: 1\n"
    "commands:\n"
    "  bdd:\n"
    "    provider:\n"
    "      kind: argv\n"
    f"      argv: [{ECHO_ARGV}, -c, "
    '"import sys; print(\'|\'.join(sys.argv[1:]))", "{targets}"]\n'
    "    targets:\n"
    "      core: {value: features/core, paths: [src/core/**]}\n"
    "      workflow: {value: features/workflow, paths: [src/workflow/**]}\n"
    "    gates:\n"
    "      zpps-workflow-kernel: [workflow, core]\n"
)


class Repository:
    """A committed Git repository with a declared behavior mapping."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.root = self.base / "repository"
        self.root.mkdir()
        self.product_home = self.base / "home"
        self.runner = CliRunner()
        self._git("init", "--quiet")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "Test")
        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "--quiet", "-m", "base")

    def close(self) -> None:
        self._temporary.cleanup()

    def _git(self, *arguments: str) -> None:
        subprocess.run(
            ("git", *arguments), cwd=self.root, check=True, capture_output=True
        )

    def run(self, *arguments: str):
        prior = Path.cwd()
        try:
            os.chdir(self.root)
            return self.runner.invoke(app, list(arguments))
        finally:
            os.chdir(prior)

    def behave(self, *arguments: str):
        return self.run("--path", str(self.product_home), "behave", *arguments)

    def declare_mapping(self) -> None:
        (self.root / "zpp.behave.yaml").write_text(MAPPING, encoding="utf-8")
        self._git("add", "zpp.behave.yaml")
        self._git("commit", "--quiet", "-m", "behavior")

    def change(self, relative: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("changed\n", encoding="utf-8")

    def has_lease_state(self) -> bool:
        return (self.product_home / "bundler").exists()
