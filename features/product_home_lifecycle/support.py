"""Capability-local verification subjects for the ZPP integration lifecycle."""

from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from agent_router import Agent, Scope, Skill
from openspec_bundler import InMemoryStoreProvider, RegisteredStore
from typer.testing import CliRunner

from features.support.lifecycle import (
    hook_ownership_states,
    replace_current_hook_with_former,
)
from zpp.artifacts import packaged_companion_skills, packaged_workflow_skills
from zpp.cli import app
from zpp.cli.shared import agent_router
from zpp.utils.bundler import BundlerLeaseService

STORE_UUID = "8f85ef9f-d18a-4787-903e-1ecb920acb77"

CODEX_SKILLS = ".codex/skills"
WORKFLOW_SKILL = "zpp-auto"


def expected_entry_count() -> int:
    """The workflow family, hook, and every current companion skill."""
    return len(packaged_workflow_skills()) + len(packaged_companion_skills()) + 1


class Environment:
    """A disposable user home with an isolated ZPP home."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.user_home = self.root / "user"
        self.user_home.mkdir()
        self.zpp_home = self.root / "zpp-home"
        self._patch = patch.object(
            Path, "home", classmethod(lambda cls: self.user_home)
        )
        self._patch.start()
        self._lease_patch = None
        self.runner = CliRunner()

    def close(self) -> None:
        if self._lease_patch is not None:
            self._lease_patch.stop()
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

    def replace_current_hook_with_former(self) -> None:
        initialized = self.run("init", "--agent", "codex")
        assert initialized.exit_code == 0, initialized.output
        router = agent_router(Agent.CODEX, self.root)
        replace_current_hook_with_former(
            router,
            Agent.CODEX,
            scope=Scope.USER,
        )

    def hook_ownership_states(self) -> tuple[str, str]:
        return hook_ownership_states(
            agent_router(Agent.CODEX, self.root),
            Agent.CODEX,
            scope=Scope.USER,
        )

    def install_owned_obsolete(self, name: str) -> Path:
        source = self.root / "obsolete-source" / name
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: obsolete test asset\n---\n",
            encoding="utf-8",
        )
        skill = Skill.from_path(source)
        router = agent_router(Agent.CODEX, self.root)
        result = router.install_skill(skill, scope=Scope.USER)
        assert result.status == "installed"
        return self.user_home / CODEX_SKILLS / name / "SKILL.md"

    def create_unowned_obsolete(self, name: str) -> Path:
        document = self.user_home / CODEX_SKILLS / name / "SKILL.md"
        document.parent.mkdir(parents=True)
        document.write_text("unowned obsolete", encoding="utf-8")
        return document

    def configure_store(self) -> Path:
        worktree = self.root / "worktree"
        worktree.mkdir()
        subprocess.run(["git", "init", "--quiet", str(worktree)], check=True)
        manifest = worktree / "openspec" / "bundler.toml"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(f'version = 1\nuuid = "{STORE_UUID}"\n', encoding="utf-8")
        provider = InMemoryStoreProvider((RegisteredStore("store", worktree),))
        module = importlib.import_module("zpp.cli.lease")
        self._lease_patch = patch.object(
            module,
            "_service",
            lambda ctx: BundlerLeaseService(ctx.obj.home, provider),
        )
        self._lease_patch.start()
        return worktree
