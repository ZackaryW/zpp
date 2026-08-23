"""Capability-local verification subjects for agent-native trait hooks."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_router import Agent
from openspec_bundler import InMemoryStoreProvider
from typer.testing import CliRunner

from zpp.artifacts import packaged_workflow_hook
from zpp.cli import app
from zpp.utils.bundler import BundlerDocuments

NATIVE_FORMATS = {
    Agent.CODEX: "json",
    Agent.CLAUDE: "json",
    Agent.KIMI: "toml",
    Agent.PI: "pi-file",
}


def hook_for(name: str):
    return packaged_workflow_hook(Agent(name))


def hook_payload(hook) -> str:
    return repr(hook.fragment) + "".join(
        item.content.decode("utf-8") for item in hook.files
    )


def resolves_current_repository(payload: str, name: str) -> bool:
    return f"--agent {name} ." in payload or f'"--agent", "{name}"' in payload


class Project:
    """A disposable project root for scoped workflow projection."""

    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def run_json(self, *arguments: str) -> list[dict]:
        result = self.runner.invoke(app, list(arguments))
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)


class HookRepository:
    def __init__(self) -> None:
        from features.support.repository import RepositoryEnvironment

        self.environment = RepositoryEnvironment()
        self.root = self.environment.worktree()
        trait = self.root / ".zpp" / "traits" / "hook-policy.toml"
        trait.parent.mkdir(parents=True)
        trait.write_text(
            '[meta]\nselection = "all"\n\n[[trait]]\n'
            '[trait.content]\nbody = "hook repository body"\n',
            encoding="utf-8",
        )
        self._module = importlib.import_module("zpp.cli.resolution")
        self._documents = self._module.BundlerDocuments
        self._module.BundlerDocuments = lambda: BundlerDocuments(
            InMemoryStoreProvider(())
        )

    def close(self) -> None:
        self._module.BundlerDocuments = self._documents
        self.environment.close()

    def resolve(self) -> dict:
        return self.environment.resolve_json("--agent", "claude", str(self.root))
