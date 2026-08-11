from __future__ import annotations

import json
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest
from agent_router import Agent
from typer.testing import CliRunner

import zpp.cli.shared
import zpp.cli.workflow
from zpp.cli import app

runner = CliRunner()
open_cli = import_module("zpp.cli.open")
reset_cli = import_module("zpp.cli.reset")
initialization_cli = import_module("zpp.cli.initialization")


def test_public_cli_preserves_grouped_shape() -> None:
    root = runner.invoke(app, ["--help"])
    behavior = runner.invoke(app, ["behave", "--help"])
    workflow = runner.invoke(app, ["workflow", "--help"])
    trait = runner.invoke(app, ["trait", "--help"])

    assert (
        root.exit_code
        == behavior.exit_code
        == workflow.exit_code
        == trait.exit_code
        == 0
    )
    assert all(
        command in root.stdout
        for command in (
            "init",
            "open",
            "reset",
            "resolve",
            "behave",
            "trait",
            "workflow",
        )
    )
    assert all(
        option in behavior.stdout
        for option in ("COMMAND", "--all", "--target", "--gate", "--base", "--head")
    )
    assert all(
        command in workflow.stdout for command in ("install", "update", "remove")
    )
    assert "init" in trait.stdout
    assert "install-workflow" not in root.stdout
    assert "init-trait" not in root.stdout
    assert "explain" not in root.stdout
    assert "space" not in root.stdout


def test_workflow_lifecycle_exposes_no_openspec_control() -> None:
    for operation in ("install", "update", "remove"):
        result = runner.invoke(app, ["workflow", operation, "--help"])

        assert result.exit_code == 0
        assert "openspec" not in result.stdout.casefold()


def test_init_preflights_every_generated_inventory_before_projection(
    monkeypatch,
) -> None:
    events: list[str] = []

    class Result:
        def __init__(self, name: str) -> None:
            self.name = name

        def to_dict(self):
            return {"name": self.name, "status": "installed"}

    @contextmanager
    def generated(agents, *, cwd):
        selected = tuple(agents)
        events.append("generated:" + ",".join(agent.value for agent in selected))
        yield tuple(
            (
                agent,
                tuple(
                    SimpleNamespace(name=f"openspec-{index}")
                    for index in range(6)
                ),
            )
            for agent in selected
        )
        events.append("generation-cleanup")

    monkeypatch.setattr(
        initialization_cli,
        "generated_openspec_skill_sets",
        generated,
    )
    monkeypatch.setattr(
        initialization_cli,
        "agent_router",
        lambda agent, root: agent,
    )
    monkeypatch.setattr(
        initialization_cli,
        "packaged_workflow_skill",
        lambda: SimpleNamespace(name="zpp-workflow"),
    )
    monkeypatch.setattr(
        initialization_cli,
        "packaged_authoring_skills",
        lambda: (
            SimpleNamespace(name="zpp-configure-behave"),
            SimpleNamespace(name="zpp-author-trait"),
        ),
        raising=False,
    )
    monkeypatch.setattr(
        initialization_cli,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-session", agent=agent),
    )

    def project(router, skill, scope, project_root):
        events.append(f"skill:{router.value}:{skill.name}")
        return Result(skill.name)

    def project_hook(router, hook, scope, project_root):
        events.append(f"hook:{router.value}:{hook.name}")
        return Result(hook.name)

    monkeypatch.setattr(initialization_cli, "project_workflow_skill", project)
    monkeypatch.setattr(initialization_cli, "project_workflow_hook", project_hook)

    result = runner.invoke(
        app,
        ["init", "--agent", "codex", "--agent", "pi", "--json"],
    )

    assert result.exit_code == 0, result.output
    assert events[0] == "generated:codex,pi"
    assert events[-1] == "generation-cleanup"
    assert len(json.loads(result.stdout)) == 20
    assert events[1:11] == [
        "skill:codex:zpp-workflow",
        "hook:codex:zpp-session",
        "skill:codex:zpp-configure-behave",
        "skill:codex:zpp-author-trait",
        *(f"skill:codex:openspec-{index}" for index in range(6)),
    ]


def test_lifecycle_summary_aggregates_stable_human_statuses() -> None:
    summary = zpp.cli.shared.render_lifecycle_summary(
        "Initialized",
        2,
        (
            {"status": "no-op"},
            {"status": "updated"},
            {"status": "installed"},
            {"status": "no-op"},
        ),
    )

    assert summary == "Initialized 2 agents: 1 installed, 1 updated, 2 unchanged."


def test_forced_init_reprojects_every_prepared_asset(monkeypatch, tmp_path) -> None:
    events: list[str] = []

    class Result:
        def __init__(self, name: str) -> None:
            self.name = name

        def to_dict(self):
            return {"name": self.name, "status": "updated"}

    @contextmanager
    def generated(agents, *, cwd):
        del cwd
        yield tuple(
            (
                agent,
                tuple(SimpleNamespace(name=f"openspec-{index}") for index in range(6)),
            )
            for agent in agents
        )

    monkeypatch.setattr(initialization_cli, "generated_openspec_skill_sets", generated)
    monkeypatch.setattr(initialization_cli, "agent_router", lambda agent, root: agent)
    monkeypatch.setattr(
        initialization_cli,
        "packaged_workflow_skill",
        lambda: SimpleNamespace(name="zpp-workflow"),
    )
    monkeypatch.setattr(
        initialization_cli,
        "packaged_authoring_skills",
        lambda: (
            SimpleNamespace(name="zpp-configure-behave"),
            SimpleNamespace(name="zpp-author-trait"),
        ),
    )
    monkeypatch.setattr(
        initialization_cli,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-session", agent=agent),
    )

    def reproject_skill(router, skill, scope, project_root):
        events.append(f"skill:{router.value}:{skill.name}")
        return Result(skill.name)

    def reproject_hook(router, hook, scope, project_root):
        events.append(f"hook:{router.value}:{hook.name}")
        return Result(hook.name)

    monkeypatch.setattr(
        initialization_cli,
        "reproject_workflow_skill",
        reproject_skill,
    )
    monkeypatch.setattr(
        initialization_cli,
        "reproject_workflow_hook",
        reproject_hook,
    )

    results = initialization_cli._initialize_selected(
        (Agent.CODEX,),
        tmp_path,
        force=True,
    )

    assert len(results) == 10
    assert events == [
        "skill:codex:zpp-workflow",
        "hook:codex:zpp-session",
        "skill:codex:zpp-configure-behave",
        "skill:codex:zpp-author-trait",
        *(f"skill:codex:openspec-{index}" for index in range(6)),
    ]


def test_init_generation_failure_precedes_every_projection(monkeypatch) -> None:
    @contextmanager
    def fail_generation(agents, *, cwd):
        del agents, cwd
        raise ValueError("generation failed")
        yield ()

    monkeypatch.setattr(
        initialization_cli,
        "generated_openspec_skill_sets",
        fail_generation,
    )
    monkeypatch.setattr(
        initialization_cli,
        "agent_router",
        lambda agent, root: pytest.fail(f"projected {agent} in {root}"),
    )

    result = runner.invoke(app, ["init", "--agent", "codex"])

    assert result.exit_code == 2
    assert "generation failed" in result.output


def test_init_packaged_authoring_failure_precedes_generation(monkeypatch) -> None:
    def fail_packaged():
        raise ValueError("invalid authoring skill")

    monkeypatch.setattr(
        initialization_cli,
        "packaged_authoring_skills",
        fail_packaged,
        raising=False,
    )
    monkeypatch.setattr(
        initialization_cli,
        "generated_openspec_skill_sets",
        lambda *args, **kwargs: pytest.fail(
            f"generated after invalid package: {args} {kwargs}"
        ),
    )

    result = runner.invoke(app, ["init", "--agent", "codex"])

    assert result.exit_code == 2
    assert "invalid authoring skill" in result.output


def test_open_creates_and_opens_selected_home_without_openlease(
    tmp_path: Path,
    monkeypatch,
) -> None:
    selected = tmp_path / "custom-home"
    opened = []
    monkeypatch.setattr(
        open_cli,
        "open_directory",
        lambda path: opened.append(path),
    )

    result = runner.invoke(app, ["--path", str(selected), "open"])

    assert result.exit_code == 0
    assert selected.is_dir()
    assert not (selected / "openlease").exists()
    assert opened == [selected]
    assert str(selected) in result.stdout


def test_open_rejects_a_symlinked_home_without_launching_opener(
    tmp_path: Path,
    monkeypatch,
) -> None:
    real = tmp_path / "real"
    real.mkdir()
    selected = tmp_path / "linked-home"
    selected.symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(
        open_cli,
        "open_directory",
        lambda path: pytest.fail(f"opened unsafe home {path}"),
    )

    result = runner.invoke(app, ["--path", str(selected), "open"])

    assert result.exit_code == 2
    assert "cannot be a symlink" in result.output


def test_reset_requires_confirmation_before_building_projection_catalog(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        reset_cli,
        "reset_projections",
        lambda: pytest.fail("reset inspected projections without --yes"),
    )

    result = runner.invoke(app, ["reset"])

    assert result.exit_code == 2
    assert "--yes" in result.output


def test_confirmed_reset_replaces_only_selected_home_state(
    tmp_path: Path,
    monkeypatch,
) -> None:
    selected = tmp_path / "custom-home"
    state = selected / "openlease"
    state.mkdir(parents=True)
    (state / "old.json").write_text("old")
    sibling = selected / "notes.txt"
    sibling.write_text("keep")
    monkeypatch.setattr(reset_cli, "reset_projections", lambda: ())

    result = runner.invoke(app, ["--path", str(selected), "reset", "--yes"])

    assert result.exit_code == 0, result.output
    assert list(state.iterdir()) == []
    assert sibling.read_text() == "keep"
    assert "replaced" in result.stdout


def test_reset_help_omits_obsolete_global_trait_overwrite_option() -> None:
    result = runner.invoke(app, ["reset", "--help"])

    assert result.exit_code == 0
    assert "--yes" in result.stdout
    assert "overwrite-global-traits" not in result.stdout


def test_reset_catalog_preflights_packaged_authoring_skills_before_generated(
    monkeypatch,
) -> None:
    monkeypatch.setattr(reset_cli, "agent_router", lambda agent, target: agent)
    monkeypatch.setattr(
        reset_cli,
        "packaged_workflow_skill",
        lambda: SimpleNamespace(name="zpp-workflow"),
    )
    monkeypatch.setattr(
        reset_cli,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-session", agent=agent),
    )
    monkeypatch.setattr(
        reset_cli,
        "packaged_authoring_skills",
        lambda: (
            SimpleNamespace(name="zpp-configure-behave"),
            SimpleNamespace(name="zpp-author-trait"),
        ),
        raising=False,
    )

    projections = reset_cli.reset_projections()

    for position, agent in enumerate(reset_cli.SUPPORTED_AGENTS):
        selected = projections[position * 10 : (position + 1) * 10]
        assert [item.agent for item in selected] == [agent.value] * 10
        assert [item.kind for item in selected] == [
            "hook",
            "skill",
            "skill:zpp-configure-behave",
            "skill:zpp-author-trait",
            *(f"skill:{name}" for name in reset_cli.OPENSPEC_CORE_SKILL_NAMES),
        ]
        assert all(item.inspect is not None for item in selected[:4])
        assert all(item.inspect is None for item in selected[4:])


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
