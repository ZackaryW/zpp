"""Capability-local verification subjects for agent-native trait hooks."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_router import Agent
from typer.testing import CliRunner

from zpp.artifacts import packaged_workflow_hook
from zpp.cli import app

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
