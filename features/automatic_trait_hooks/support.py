"""Capability-local verification subjects for agent-native trait hooks."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_router import Agent, AgentEnvironment, AgentRouter, Scope, Skill
from openspec_bundler import InMemoryStoreProvider
from typer.testing import CliRunner

from features.support.lifecycle import (
    hook_ownership_states,
    replace_current_hook_with_former,
)
from zpp.artifacts import (
    packaged_workflow_hook,
    packaged_workflow_reminder_hook,
    packaged_workflow_skills,
)
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


def post_compaction_strategy(hook, agent: Agent) -> str:
    if agent in {Agent.CODEX, Agent.CLAUDE}:
        groups = hook.fragment.get("SessionStart", [])
        if any(group.get("matcher") in {None, "compact"} for group in groups):
            return "session-start:compact"
    if agent is Agent.KIMI and any(
        entry.get("event") == "PostCompact" for entry in hook.fragment
    ):
        return "post-compact"
    if agent is Agent.PI and "before_agent_start" in hook_payload(hook):
        return "before-agent-start"
    return "missing"


def post_compaction_strategies(hooks: dict[Agent, object]) -> dict[str, str]:
    return {
        agent.value: post_compaction_strategy(hook, agent)
        for agent, hook in hooks.items()
    }


def packaged_integration_inventory(agent: Agent) -> tuple[tuple[str, str], ...]:
    inventory = [
        *(("skill", skill.name) for skill in packaged_workflow_skills()),
        ("hook", packaged_workflow_hook(agent).name),
    ]
    reminder = packaged_workflow_reminder_hook(agent)
    if reminder is not None:
        inventory.append(("hook", reminder.name))
    return tuple(inventory)


def lifecycle_inventory(records: list[dict]) -> tuple[tuple[str, str], ...]:
    return tuple((record["kind"], record["name"]) for record in records)


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

    def install_owned_obsolete(self, name: str) -> Path:
        source = self.root / "obsolete-source" / name
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: obsolete test asset\n---\nold\n",
            encoding="utf-8",
        )
        router = AgentRouter(
            Agent.CODEX,
            home=self.root / "user-home",
            environment=AgentEnvironment(self.root / "user-home", self.root),
        )
        result = router.install_skill(
            Skill.from_path(source), scope=Scope.PROJECT, project_root=self.root
        )
        assert result.status == "installed"
        return result.destination / name / "SKILL.md"

    def replace_current_hook_with_former(self) -> None:
        self.run_json(
            "workflow",
            "install",
            "--agent",
            "codex",
            "--target",
            str(self.root),
        )
        router = AgentRouter(
            Agent.CODEX,
            home=self.root / "user-home",
            environment=AgentEnvironment(self.root / "user-home", self.root),
        )
        replace_current_hook_with_former(
            router,
            Agent.CODEX,
            scope=Scope.PROJECT,
            project_root=self.root,
        )

    def hook_ownership_states(self) -> tuple[str, str]:
        router = AgentRouter(
            Agent.CODEX,
            home=self.root / "user-home",
            environment=AgentEnvironment(self.root / "user-home", self.root),
        )
        return hook_ownership_states(
            router,
            Agent.CODEX,
            scope=Scope.PROJECT,
            project_root=self.root,
        )

    def create_unmanaged_current(self, name: str) -> Path:
        document = self.root / ".agents" / "skills" / name / "SKILL.md"
        document.parent.mkdir(parents=True)
        document.write_text("unmanaged current collision", encoding="utf-8")
        return document


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
