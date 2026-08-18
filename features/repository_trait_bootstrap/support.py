"""Capability-local verification subjects for repository trait bootstrap."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from zpp.cli import app
from zpp.utils.openlease import create_trait_documents

COMMAND_NAMES = (
    "init",
    "sync",
    "open",
    "reset",
    "resolve",
    "behave",
    "trait",
    "workflow",
)
WORKFLOW_OPERATIONS = ("install", "update", "remove")


def root_command_names() -> set[str]:
    """Registered root command names, so `workspace` cannot mask a bare `space`."""
    names = {info.name for info in app.registered_commands if info.name}
    names.update(group.name for group in app.registered_groups if group.name)
    return names


def help_for(*arguments: str):
    return CliRunner().invoke(app, [*arguments, "--help"])


class Repository:
    """A disposable Git repository with isolated OpenLease trait state."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.root = self.base / "repository"
        self.root.mkdir()
        self.state = self.base / "state"
        self.documents = create_trait_documents(self.state)
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def git(self, *arguments: str) -> None:
        subprocess.run(
            ("git", *arguments), cwd=self.root, check=True, capture_output=True
        )

    def init_git(self) -> None:
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")

    def tracked_files(self) -> list[str]:
        return sorted(
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file()
        )

    def run_in_root(self, *arguments: str):
        prior = Path.cwd()
        try:
            os.chdir(self.root)
            return self.runner.invoke(app, list(arguments))
        finally:
            os.chdir(prior)
