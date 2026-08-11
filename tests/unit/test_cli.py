from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from agent_router import Agent
from typer.testing import CliRunner

import zpp.cli.shared
import zpp.cli.workflow
from zpp.cli import app

runner = CliRunner()


def test_public_cli_preserves_grouped_shape() -> None:
    root = runner.invoke(app, ["--help"])
    workflow = runner.invoke(app, ["workflow", "--help"])
    trait = runner.invoke(app, ["trait", "--help"])

    assert root.exit_code == workflow.exit_code == trait.exit_code == 0
    assert all(
        command in root.stdout for command in ("init", "resolve", "trait", "workflow")
    )
    assert all(
        command in workflow.stdout for command in ("install", "update", "remove")
    )
    assert "init" in trait.stdout
    assert "install-workflow" not in root.stdout
    assert "init-trait" not in root.stdout
    assert "explain" not in root.stdout
    assert "space" not in root.stdout


def test_prompt_uses_exact_agent_router_agent_order(monkeypatch) -> None:
    captured = {}

    class Prompt:
        def ask(self):
            return None

    def checkbox(message, *, choices):
        captured["message"] = message
        captured["choices"] = choices
        return Prompt()

    monkeypatch.setattr(zpp.cli.shared.questionary, "checkbox", checkbox)

    selection = zpp.cli.shared.prompt_agent_selection()

    assert selection.cancelled is True
    assert [choice.title for choice in captured["choices"]] == [
        "Codex",
        "Claude Code",
        "Pi",
        "Kimi",
    ]
    assert [choice.value for choice in captured["choices"]] == [
        Agent.CODEX,
        Agent.CLAUDE,
        Agent.PI,
        Agent.KIMI,
    ]


def test_workflow_cli_preserves_explicit_first_seen_agent_order(monkeypatch) -> None:
    calls = []

    class Result:
        def to_dict(self):
            return {"status": "installed"}

    monkeypatch.setattr(zpp.cli.workflow, "agent_router", lambda agent, target: agent)
    monkeypatch.setattr(
        zpp.cli.workflow,
        "packaged_workflow_skill",
        lambda: SimpleNamespace(name="zpp-workflow"),
    )
    monkeypatch.setattr(
        zpp.cli.workflow,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-session", agent=agent),
    )

    def project(router, skill, scope, project_root, *, replace_project=False):
        calls.append(("skill", router, replace_project))
        return Result()

    def project_hook(router, hook, scope, project_root):
        calls.append(("hook", router, False))
        return Result()

    monkeypatch.setattr(zpp.cli.workflow, "project_workflow_skill", project)
    monkeypatch.setattr(zpp.cli.workflow, "project_workflow_hook", project_hook)

    result = runner.invoke(
        app,
        [
            "workflow",
            "install",
            "--agent",
            "codex",
            "--agent",
            "pi",
            "--agent",
            "codex",
        ],
    )

    assert result.exit_code == 0
    assert calls == [
        ("skill", Agent.CODEX, False),
        ("hook", Agent.CODEX, False),
        ("skill", Agent.PI, False),
        ("hook", Agent.PI, False),
    ]


def test_workflow_project_update_requests_explicit_skill_replacement(
    monkeypatch,
) -> None:
    calls = []

    class Result:
        def to_dict(self):
            return {"status": "updated"}

    monkeypatch.setattr(zpp.cli.workflow, "agent_router", lambda agent, target: agent)
    monkeypatch.setattr(
        zpp.cli.workflow,
        "packaged_workflow_skill",
        lambda: SimpleNamespace(name="zpp-workflow"),
    )
    monkeypatch.setattr(
        zpp.cli.workflow,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-session"),
    )

    def project(router, skill, scope, project_root, *, replace_project=False):
        calls.append(("skill", replace_project))
        return Result()

    def project_hook(router, hook, scope, project_root):
        calls.append(("hook", False))
        return Result()

    monkeypatch.setattr(zpp.cli.workflow, "project_workflow_skill", project)
    monkeypatch.setattr(zpp.cli.workflow, "project_workflow_hook", project_hook)

    result = runner.invoke(
        app,
        ["workflow", "update", "--agent", "codex", "--target", "."],
    )

    assert result.exit_code == 0
    assert calls == [("skill", True), ("hook", False)]


def test_agent_router_uses_real_home_and_selected_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))

    router = zpp.cli.shared.agent_router(Agent.CODEX, project)

    assert router.home == home.resolve()
    assert router.environment.root == home.resolve()
    assert router.environment.project_root == project.resolve()


def test_resolve_rejects_more_than_one_agent_before_opening_repository() -> None:
    result = runner.invoke(
        app,
        ["resolve", ".", "--agent", "codex", "--agent", "pi"],
    )

    assert result.exit_code == 2
    assert "exactly one --agent" in result.output
