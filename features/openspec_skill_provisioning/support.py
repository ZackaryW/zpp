"""Capability-local verification subjects for OpenSpec skill provisioning."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from typer.testing import CliRunner

from zpp.artifacts import packaged_companion_skills
from zpp.cli import app
from zpp.utils.openspec import OPENSPEC_CORE_SKILL_NAMES

CODEX_SKILLS = ".codex/skills"
GENERATED_SKILL = "openspec-apply-change"


def companion_names() -> list[str]:
    return [skill.name for skill in packaged_companion_skills()]


def expected_asset_count() -> int:
    return 2 + len(companion_names()) + len(OPENSPEC_CORE_SKILL_NAMES)


class Home:
    """A disposable user home with an isolated ZPP product home."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        root = Path(self._temporary.name)
        self.user_home = root / "user"
        self.user_home.mkdir(parents=True, exist_ok=True)
        self.product_home = root / "zpp-home"
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

    def skill_path(self, name: str) -> Path:
        return self.user_home / CODEX_SKILLS / name

    def generated_document(self) -> Path:
        return self.skill_path(GENERATED_SKILL) / "SKILL.md"

    def provenance(self) -> dict:
        path = self.skill_path(GENERATED_SKILL) / ".zpp-openspec.json"
        return json.loads(path.read_text(encoding="utf-8"))
