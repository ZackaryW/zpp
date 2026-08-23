"""Capability-local verification subjects for repository trait bootstrap."""

from __future__ import annotations

import importlib
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from openspec_bundler import InMemoryStoreProvider
from typer.testing import CliRunner

from zpp.cli import app
from zpp.utils.bundler import BundlerDocuments

COMMAND_NAMES = (
    "init",
    "sync",
    "open",
    "reset",
    "resolve",
    "behave",
    "trait",
    "lease",
    "workflow",
)
WORKFLOW_OPERATIONS = ("install", "update", "remove")


def root_command_names() -> set[str]:
    """Registered root command names."""
    names = {info.name for info in app.registered_commands if info.name}
    names.update(group.name for group in app.registered_groups if group.name)
    return names


def help_for(*arguments: str):
    return CliRunner().invoke(app, [*arguments, "--help"])


class Repository:
    """A disposable Git repository with exact Bundler trait attachments."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.root = self.base / "repository"
        self.root.mkdir()
        self.documents = BundlerDocuments(InMemoryStoreProvider(()))
        self.runner = CliRunner()
        self.init_git()
        self._resolution = importlib.import_module("zpp.cli.resolution")
        self._document_factory = self._resolution.BundlerDocuments
        self._resolution.BundlerDocuments = lambda: self.documents

    def close(self) -> None:
        self._resolution.BundlerDocuments = self._document_factory
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
            if path.is_file() and ".git" not in path.relative_to(self.root).parts
        )

    def run_in_root(self, *arguments: str):
        prior = Path.cwd()
        try:
            os.chdir(self.root)
            return self.runner.invoke(app, list(arguments))
        finally:
            os.chdir(prior)
