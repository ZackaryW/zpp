"""Capability-local verification subjects for the ZPP integration lifecycle."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from typer.testing import CliRunner

from zpp.artifacts import packaged_companion_skills
from zpp.cli import app

CODEX_SKILLS = ".codex/skills"
WORKFLOW_SKILL = "zpp-workflow"


def expected_entry_count() -> int:
    """Hook, workflow skill, every companion skill, and six OpenSpec skills."""
    return 2 + len(packaged_companion_skills()) + 6


class Environment:
    """A disposable user home with an isolated ZPP home."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        root = Path(self._temporary.name)
        self.user_home = root / "user"
        self.user_home.mkdir()
        self.zpp_home = root / "zpp-home"
        self._patch = patch.object(
            Path, "home", classmethod(lambda cls: self.user_home)
        )
        self._patch.start()
        self.runner = CliRunner()

    def close(self) -> None:
        self._patch.stop()
        self._temporary.cleanup()

    def run(self, *arguments: str):
        return self.runner.invoke(app, list(arguments))

    def run_json(self, *arguments: str):
        result = self.run(*arguments)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    def workflow_skill_document(self) -> Path:
        return self.user_home / CODEX_SKILLS / WORKFLOW_SKILL / "SKILL.md"
