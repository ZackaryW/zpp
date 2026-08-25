from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from agent_router import Agent, Scope
from openspec_bundler import InMemoryStoreProvider, RegisteredStore
from typer.testing import CliRunner

import zpp.cli.shared
import zpp.cli.workflow
from zpp.cli import app
from zpp.utils.bundler import BundlerLeaseService
from zpp.utils.product_home import WorkflowIdentityRepository, ZppHome

runner = CliRunner()
open_cli = import_module("zpp.cli.open")
reset_cli = import_module("zpp.cli.reset")
initialization_cli = import_module("zpp.cli.initialization")
lifecycle_cli = import_module("zpp.cli.lifecycle")
sync_cli = import_module("zpp.cli.sync")


def test_public_cli_preserves_grouped_shape() -> None:
    root = runner.invoke(app, ["--help"])
    behavior = runner.invoke(app, ["behave", "--help"])
    workflow = runner.invoke(app, ["workflow", "--help"])
    trait = runner.invoke(app, ["trait", "--help"])
    lease = runner.invoke(app, ["lease", "--help"])

    assert (
        root.exit_code
        == behavior.exit_code
        == workflow.exit_code
        == trait.exit_code
        == lease.exit_code
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
            "lease",
            "bypass",
            "workflow",
        )
    )
    assert all(
        option in behavior.stdout
        for option in ("COMMAND", "--all", "--target", "--gate", "--base", "--head")
    )
    assert all(
        command in workflow.stdout
        for command in ("install", "update", "remove", "run")
    )
    assert "init" in trait.stdout
    assert "install-workflow" not in root.stdout
    assert "init-trait" not in root.stdout
    assert "explain" not in root.stdout
    assert "workspace" not in _root_command_names()
    assert all(
        operation in lease.stdout
        for operation in (
            "acquire",
            "status",
            "audit",
            "archive",
            "complete",
            "abandon",
        )
    )


def test_managed_owner_drives_archive_and_completion_when_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    store_uuid = UUID("4c6d971e-fd43-4015-926a-7284f0e061a0")
    store = tmp_path / "store"
    manifest = store / "openspec" / "bundler.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(f'version = 1\nuuid = "{store_uuid}"\n', encoding="utf-8")
    home = ZppHome(tmp_path / "home")
    owner = WorkflowIdentityRepository(home).resolve()
    service = BundlerLeaseService(
        home, InMemoryStoreProvider((RegisteredStore("store", store),))
    )
    acquired = service.acquire(owner, ((store_uuid, "managed-change"),))
    lease_cli = import_module("zpp.cli.lease")
    monkeypatch.setattr(lease_cli, "_service", lambda ctx: service)

    archived = runner.invoke(
        app,
        [
            "--path",
            str(home.path),
            "lease",
            "archive",
            "--bundle",
            str(acquired.bundle.bundle_uuid),
            "--member",
            f"{store_uuid}:managed-change",
        ],
    )
    completed = runner.invoke(
        app,
        [
            "--path",
            str(home.path),
            "lease",
            "complete",
            "--bundle",
            str(acquired.bundle.bundle_uuid),
        ],
    )

    assert archived.exit_code == 0, archived.output
    assert completed.exit_code == 0, completed.output
    assert service.status() == ()


def test_managed_owner_rejects_an_explicitly_owned_bundle(
    tmp_path: Path, monkeypatch
) -> None:
    store_uuid = UUID("4c6d971e-fd43-4015-926a-7284f0e061a0")
    store = tmp_path / "store"
    manifest = store / "openspec" / "bundler.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(f'version = 1\nuuid = "{store_uuid}"\n', encoding="utf-8")
    home = ZppHome(tmp_path / "home")
    WorkflowIdentityRepository(home).resolve()
    service = BundlerLeaseService(
        home, InMemoryStoreProvider((RegisteredStore("store", store),))
    )
    acquired = service.acquire("workflow:other", ((store_uuid, "owned-change"),))
    lease_cli = import_module("zpp.cli.lease")
    monkeypatch.setattr(lease_cli, "_service", lambda ctx: service)

    result = runner.invoke(
        app,
        [
            "--path",
            str(home.path),
            "lease",
            "archive",
            "--bundle",
            str(acquired.bundle.bundle_uuid),
            "--member",
            f"{store_uuid}:owned-change",
        ],
    )

    assert result.exit_code == 2
    assert service.status() == (acquired.bundle,)


def test_bypass_warns_and_propagates_child_exit_code() -> None:
    result = runner.invoke(
        app,
        [
            "bypass",
            "--reason",
            "owner approved test",
            "--acknowledge",
            "--",
            sys.executable,
            "-c",
            "import sys; sys.exit(7)",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 7
    assert "WARNING" in result.stderr
    assert "owner approved test" in result.stderr


@pytest.mark.parametrize(
    "lease_arguments, operation",
    [
        (
            [
                "acquire",
                "--member",
                "4c6d971e-fd43-4015-926a-7284f0e061a0:change",
            ],
            "acquire",
        ),
        (
            [
                "archive",
                "--bundle",
                "ee26f09b-3bf1-4de8-820c-6b098353258c",
                "--member",
                "4c6d971e-fd43-4015-926a-7284f0e061a0:change",
            ],
            "archive",
        ),
        (
            [
                "complete",
                "--bundle",
                "ee26f09b-3bf1-4de8-820c-6b098353258c",
            ],
            "complete",
        ),
        (
            [
                "abandon",
                "--bundle",
                "ee26f09b-3bf1-4de8-820c-6b098353258c",
            ],
            "abandon",
        ),
    ],
)
def test_bypass_reports_every_mutating_lease_entry_without_state(
    tmp_path: Path, lease_arguments: list[str], operation: str
) -> None:
    home = tmp_path / "home"
    child = [
        sys.executable,
        "-c",
        "from zpp.cli import app; app()",
        "--path",
        str(home),
        "lease",
        *lease_arguments,
    ]

    result = runner.invoke(
        app,
        [
            "bypass",
            "--reason",
            "owner approved operation",
            "--acknowledge",
            "--",
            *child,
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["operation"] == operation
    assert json.loads(result.stdout)["coordination"] == "bypassed"
    assert not home.exists()


def _root_command_names() -> set[str]:
    """Registered root command names."""
    names = {info.name for info in app.registered_commands if info.name}
    names.update(group.name for group in app.registered_groups if group.name)
    return names


def test_workflow_lifecycle_exposes_no_openspec_control() -> None:
    for operation in ("install", "update", "remove"):
        result = runner.invoke(app, ["workflow", operation, "--help"])

        assert result.exit_code == 0
        assert "openspec" not in result.stdout.casefold()


def test_init_projects_complete_packaged_family_without_generated_inventory(
    monkeypatch,
) -> None:
    calls = []
    inspections = tuple(
        SimpleNamespace(agent=agent, classification="absent")
        for agent in (Agent.CODEX, Agent.PI)
    )

    def inspect(agents, *, target, scope, project_root, include_companions):
        calls.append(("inspect", agents, scope, project_root, include_companions))
        return inspections

    def reconcile(selected, *, absent):
        calls.append(("reconcile", selected, absent))
        return [
            {
                "agent": item.agent.value,
                "asset": "skill:zpp-auto",
                "status": "installed",
            }
            for item in selected
        ]

    monkeypatch.setattr(initialization_cli, "inspect_installations", inspect)
    monkeypatch.setattr(initialization_cli, "reconcile_installations", reconcile)

    result = runner.invoke(
        app,
        ["init", "--agent", "codex", "--agent", "pi", "--json"],
    )

    assert result.exit_code == 0, result.output
    assert len(json.loads(result.stdout)) == 2
    assert calls[0][1:] == (
        (Agent.CODEX, Agent.PI),
        Scope.USER,
        None,
        True,
    )
    assert calls[1] == ("reconcile", inspections, "install")


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


def test_sync_summary_names_partial_migration_and_failed_retirement() -> None:
    summary = sync_cli._sync_summary(
        (
            {
                "agent": "codex",
                "asset": "obsolete-skill:zpp-workflow",
                "status": "retirement-failed",
                "decision": "preserve",
            },
            {
                "agent": "codex",
                "asset": "migration",
                "status": "partial",
                "decision": "migrate",
                "current": ["skill:zpp-auto"],
                "surviving_obsolete": ["obsolete-skill:zpp-workflow"],
                "failures": ["obsolete-skill:zpp-workflow"],
            },
        )
    )

    assert "codex migration partial" in summary
    assert "surviving obsolete: obsolete-skill:zpp-workflow" in summary
    assert "retirement failed: obsolete-skill:zpp-workflow" in summary


def test_init_rejects_an_installed_agent_and_directs_it_to_sync(monkeypatch) -> None:
    monkeypatch.setattr(
        initialization_cli,
        "inspect_installations",
        lambda *args, **kwargs: (
            SimpleNamespace(agent=Agent.CODEX, classification="current"),
        ),
    )
    monkeypatch.setattr(
        initialization_cli,
        "reconcile_installations",
        lambda *args, **kwargs: pytest.fail("reconciled current integration"),
    )

    result = runner.invoke(app, ["init", "--agent", "codex", "--json"])

    assert result.exit_code == 0, result.output
    records = json.loads(result.stdout)
    assert [item["status"] for item in records] == ["already-initialized"]
    assert records[0]["agent"] == "codex"


def test_init_initializes_absent_agents_alongside_a_rejected_one(monkeypatch) -> None:
    monkeypatch.setattr(
        initialization_cli,
        "inspect_installations",
        lambda *args, **kwargs: (
            SimpleNamespace(agent=Agent.CODEX, classification="current"),
            SimpleNamespace(agent=Agent.PI, classification="absent"),
        ),
    )
    monkeypatch.setattr(
        initialization_cli,
        "reconcile_installations",
        lambda selected, absent: [
            {"agent": item.agent.value, "status": "installed"} for item in selected
        ],
    )

    result = runner.invoke(
        app,
        ["init", "--agent", "codex", "--agent", "pi", "--json"],
    )

    assert result.exit_code == 0, result.output
    records = json.loads(result.stdout)
    assert [(item["agent"], item["status"]) for item in records] == [
        ("pi", "installed"),
        ("codex", "already-initialized"),
    ]


def test_init_exposes_no_force_option() -> None:
    assert "--force" not in runner.invoke(app, ["init", "--help"]).stdout
    assert runner.invoke(app, ["init", "--force"]).exit_code != 0


def test_init_has_no_openspec_generation_surface(monkeypatch) -> None:
    assert not hasattr(initialization_cli, "generated_openspec_skill_sets")


def test_init_invalid_packaged_family_precedes_projection(monkeypatch) -> None:
    def fail_inspection(*args, **kwargs):
        raise ValueError("invalid workflow family")

    monkeypatch.setattr(
        initialization_cli,
        "inspect_installations",
        fail_inspection,
    )
    monkeypatch.setattr(
        initialization_cli,
        "reconcile_installations",
        lambda *args, **kwargs: pytest.fail("projected invalid family"),
    )

    result = runner.invoke(app, ["init", "--agent", "codex"])

    assert result.exit_code == 2
    assert "invalid workflow family" in result.output


def test_open_creates_and_opens_selected_home_without_bundler_state(
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
    assert not (selected / "bundler").exists()
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
    state = selected / "bundler"
    state.mkdir(parents=True)
    (state / "old.json").write_text("old")
    sibling = selected / "notes.txt"
    sibling.write_text("keep")
    monkeypatch.setattr(reset_cli, "reset_projections", lambda: ())

    result = runner.invoke(app, ["--path", str(selected), "reset", "--yes"])

    assert result.exit_code == 0, result.output
    assert not (state / "old.json").exists()
    assert sibling.read_text() == "keep"
    assert "replaced" in result.stdout


def test_reset_help_omits_obsolete_global_trait_overwrite_option() -> None:
    result = runner.invoke(app, ["reset", "--help"])

    assert result.exit_code == 0
    assert "--yes" in result.stdout
    assert "overwrite-global-traits" not in result.stdout


def test_reset_catalog_contains_current_inventory_before_obsolete_tombstones(
    monkeypatch,
) -> None:
    monkeypatch.setattr(lifecycle_cli, "agent_router", lambda agent, target: agent)
    monkeypatch.setattr(
        lifecycle_cli,
        "packaged_workflow_skills",
        lambda: (
            SimpleNamespace(name="zpp-auto"),
            SimpleNamespace(name="zpps-workflow-kernel"),
        ),
    )
    monkeypatch.setattr(
        lifecycle_cli,
        "packaged_workflow_hook",
        lambda agent: SimpleNamespace(name="zpp-traits", agent=agent),
    )
    monkeypatch.setattr(
        lifecycle_cli,
        "packaged_workflow_reminder_hook",
        lambda agent: (
            SimpleNamespace(name="zpp-workflow-reminder", agent=agent)
            if agent in (Agent.CODEX, Agent.CLAUDE)
            else None
        ),
    )
    monkeypatch.setattr(
        lifecycle_cli,
        "packaged_companion_skills",
        lambda: (
            SimpleNamespace(name="zpp-configure-behave"),
            SimpleNamespace(name="zpp-author-trait"),
        ),
    )

    projections = reset_cli.reset_projections()

    offset = 0
    for agent in reset_cli.SUPPORTED_AGENTS:
        has_reminder = agent in (Agent.CODEX, Agent.CLAUDE)
        per_agent = (
            2
            + 1
            + int(has_reminder)
            + 2
            + len(lifecycle_cli.OBSOLETE_WORKFLOW_SKILL_NAMES)
        )
        selected = projections[offset : offset + per_agent]
        offset += per_agent
        assert [item.agent for item in selected] == [agent.value] * per_agent
        assert [item.kind for item in selected] == [
            "skill:zpp-auto",
            "skill:zpps-workflow-kernel",
            "hook",
            *(["hook:zpp-workflow-reminder"] if has_reminder else []),
            "skill:zpp-configure-behave",
            "skill:zpp-author-trait",
            *(
                f"obsolete-skill:{name}"
                for name in lifecycle_cli.OBSOLETE_WORKFLOW_SKILL_NAMES
            ),
        ]
        assert all(item.inspect is not None for item in selected)
        tombstone_start = 5 + int(has_reminder)
        assert all(item.project is None for item in selected[tombstone_start:])

    assert offset == len(projections)


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
    inspections = (
        SimpleNamespace(agent=Agent.CODEX, classification="absent"),
        SimpleNamespace(agent=Agent.PI, classification="absent"),
    )

    def inspect(agents, **kwargs):
        calls.append(("inspect", agents, kwargs))
        return inspections

    def reconcile(selected, **kwargs):
        calls.append(("reconcile", selected, kwargs))
        return [
            {
                "agent": item.agent.value,
                "asset": "skill:zpp-auto",
                "status": "installed",
            }
            for item in selected
        ]

    monkeypatch.setattr(zpp.cli.workflow, "inspect_installations", inspect)
    monkeypatch.setattr(zpp.cli.workflow, "preflight_first_install", lambda items: None)
    monkeypatch.setattr(zpp.cli.workflow, "reconcile_installations", reconcile)

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
    assert calls[0][1] == (Agent.CODEX, Agent.PI)
    assert calls[1][1] == inspections


def test_workflow_project_update_requests_explicit_skill_replacement(
    monkeypatch,
) -> None:
    calls = []
    inspection = SimpleNamespace(agent=Agent.CODEX, classification="current")

    def inspect(agents, **kwargs):
        calls.append(("inspect", agents, kwargs))
        return (inspection,)

    def reconcile(selected, **kwargs):
        calls.append(("reconcile", selected, kwargs))
        return []

    monkeypatch.setattr(zpp.cli.workflow, "inspect_installations", inspect)
    monkeypatch.setattr(zpp.cli.workflow, "reconcile_installations", reconcile)

    result = runner.invoke(
        app,
        ["workflow", "update", "--agent", "codex", "--target", "."],
    )

    assert result.exit_code == 0
    assert calls[0][2]["scope"] is Scope.PROJECT
    assert calls[0][2]["project_root"] == Path.cwd().resolve()
    assert calls[1] == (
        "reconcile",
        (inspection,),
        {"force": True, "absent": "install", "explicit_update": True},
    )


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
