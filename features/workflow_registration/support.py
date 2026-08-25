"""Public-system subjects for persistent workflow reminders."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_router import Agent
from typer.testing import CliRunner

import zpp.artifacts as artifacts
from zpp.cli import app


class Environment:
    def __init__(self) -> None:
        self._temporary = TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.root = self.base / "repository"
        self.root.mkdir()
        self.home = self.base / "home"
        self.runner = CliRunner()

    def close(self) -> None:
        self._temporary.cleanup()

    def invoke(self, *arguments: str):
        return self.runner.invoke(
            app,
            ["--path", str(self.home), *arguments],
            catch_exceptions=False,
        )

    def run(self, *arguments: str):
        return self.invoke("workflow", "run", *arguments)

    def start(self, workflow: str, *, change: str = "sample-change"):
        return self.run(
            "start",
            workflow,
            "--root",
            str(self.root),
            "--change",
            change,
        )

    def status(self):
        return self.run("status", "--root", str(self.root), "--change", "sample-change")

    def state_snapshot(self) -> dict[str, bytes]:
        if not self.home.exists():
            return {}
        return {
            path.relative_to(self.home).as_posix(): path.read_bytes()
            for path in self.home.rglob("*")
            if path.is_file()
        }


def result_json(result) -> dict:
    assert result.exit_code == 0, result.output
    value = json.loads(result.stdout)
    assert isinstance(value, dict), value
    return value


def packaged_contract_inventory():
    return artifacts.packaged_workflow_contracts()


def packaged_component_inventory():
    return artifacts.packaged_component_contracts()


def decode_workflow_contract(payload: dict):
    return artifacts.decode_workflow_contract(
        payload, source="bdd-invalid-workflow.json"
    )


def packaged_reminder_hook(agent: Agent):
    return artifacts.packaged_workflow_reminder_hook(agent)
