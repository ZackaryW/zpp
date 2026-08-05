from __future__ import annotations

import json
import shutil
from pathlib import Path

from features.support import zpp_support as support
from zpp.utils.openspec_skills import OPENSPEC_CORE_SKILL_NAMES


def request_update_help(context) -> None:
    support.invoke(context, ["init", "--help"])
    context.init_help = context.result.stdout
    support.invoke(context, ["update", "--help"])
    context.update_help = context.result.stdout


def assert_init_help(context) -> None:
    text = context.init_help.lower()
    assert "bootstrap missing global user state" in text
    assert "selected agent hooks" in text


def assert_update_help(context) -> None:
    text = context.update_help.lower()
    assert "initialized global zpp state" in text
    assert "installed integrations" in text


def assert_update_has_no_selection_options(context) -> None:
    text = context.update_help.lower()
    assert all(option not in text for option in ("--agent", "--scope", "--target", "--force", "--install"))


def assert_no_helper_self_upgrade_claim(context) -> None:
    assert "upgrade the running zpp executable" not in context.init_help.lower()
    assert "does not upgrade the running zpp executable" in context.update_help.lower()


def record_supported_integrations(context) -> None:
    context.supported_before = support.snapshot(context.home)


def run_update(context) -> None:
    support.invoke(context, ["update"])


def run_update_twice(context) -> None:
    first = support.invoke(context, ["update"])
    context.first_update_exit = first.exit_code
    context.after_first_update = support.snapshot(context.home)
    second = support.invoke(context, ["update"])
    context.second_update_exit = second.exit_code


def assert_uninitialized_rejection(context) -> None:
    assert context.result.exit_code == 1, context.result.output
    assert "user state is incomplete" in context.result.stderr.lower()


def assert_no_user_state_created(context) -> None:
    assert not (context.home / ".zpp").exists()


def assert_supported_integrations_unchanged(context) -> None:
    assert support.snapshot(context.home) == context.supported_before


def make_default_additive_fixture(context) -> None:
    root = context.home / ".zpp/profiles/default"
    missing = root / "traits/bdd-structure-python.md"
    missing.unlink()
    automatic = root / "traits/automatic-workflow.md"
    automatic.write_text(
        automatic.read_text(encoding="utf-8").replace(
            "Continue the complete workflow",
            "Continue the owner-custom workflow",
        ),
        encoding="utf-8",
    )
    config = root / "config.json"
    config.write_text(
        '{ "traitsConfig": {"owner": {"kept": true}}, "trait_overwrites": false }\n',
        encoding="utf-8",
    )
    triggers = root / "trait.json"
    document = json.loads(triggers.read_text(encoding="utf-8"))
    document[0]["which"] = "owner-tool"
    triggers.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    custom = support.write_trait(root, "owner-custom", body="owner custom\n")
    context.missing_default_trait = missing
    context.authored_default_bytes = {
        path: path.read_bytes() for path in (automatic, config, triggers, custom)
    }


def assert_authored_default_fixture(context) -> None:
    assert not context.missing_default_trait.exists()
    assert len(context.authored_default_bytes) == 4


def assert_no_owned_global_surfaces(context) -> None:
    for agent in ("pi", "codex", "claude"):
        assert not support.agent_path(context, agent).exists()
        assert not (
            support.workflow_skill_root(context, agent, scope="global")
            / ".zpp-workflow-skills.json"
        ).exists()
    context.agent_surfaces_before = support.snapshot(context.home)


def record_repository_local_state(context) -> None:
    support.write_layer(context.project / ".zpp")
    support.write_trait(context.project / ".zpp", "local-only")
    context.repository_before = support.snapshot(context.project)


def assert_only_missing_default_added(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.missing_default_trait.is_file()


def assert_authored_default_preserved(context) -> None:
    assert all(path.read_bytes() == content for path, content in context.authored_default_bytes.items())


def assert_no_agent_surface_installed(context) -> None:
    for agent in ("pi", "codex", "claude"):
        assert not support.agent_path(context, agent).exists()
        workflow = support.workflow_skill_root(context, agent, scope="global")
        openspec = support.openspec_skill_root(context, agent, scope="global")
        assert not (workflow / ".zpp-workflow-skills.json").exists()
        assert not (openspec / ".zpp-openspec-skills.json").exists()


def assert_repository_unchanged(context) -> None:
    assert support.snapshot(context.project) == context.repository_before


def assert_no_resolution_or_cache(context) -> None:
    cached = context.home / ".zpp/cached"
    assert not any(path.is_file() for path in cached.rglob("*"))


def historical_claude_hook_only(context) -> None:
    support.step_exact_historical_claude_hook(context)
    assert not (
        support.workflow_skill_root(context, "claude", scope="global")
        / ".zpp-workflow-skills.json"
    ).exists()


def record_absent_pi_codex(context) -> None:
    context.pi_codex_before = {
        context.home / ".pi": support.snapshot(context.home / ".pi"),
        context.home / ".codex": support.snapshot(context.home / ".codex"),
        context.home / ".agents": support.snapshot(context.home / ".agents"),
    }


def record_unrelated_native_configuration(context) -> None:
    document = json.loads(support.agent_path(context, "claude").read_text(encoding="utf-8"))
    context.unrelated_native_value = document["theme"]


def assert_current_claude_hook(context) -> None:
    assert context.first_update_exit == context.second_update_exit == 0
    support.assert_current_agent_integration(context, "claude")


def assert_claude_has_no_skill_projection(context) -> None:
    assert not (
        support.workflow_skill_root(context, "claude", scope="global")
        / ".zpp-workflow-skills.json"
    ).exists()
    assert not (
        support.openspec_skill_root(context, "claude", scope="global")
        / ".zpp-openspec-skills.json"
    ).exists()


def assert_pi_codex_unchanged(context) -> None:
    for root, before in context.pi_codex_before.items():
        assert support.snapshot(root) == before


def assert_unrelated_native_unchanged(context) -> None:
    document = json.loads(support.agent_path(context, "claude").read_text(encoding="utf-8"))
    assert document["theme"] == context.unrelated_native_value


def assert_second_update_unchanged(context) -> None:
    assert support.snapshot(context.home) == context.after_first_update


def install_outdated_pi_without_openspec(context) -> None:
    result = support.invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    root = support.workflow_skill_root(context, "pi", scope="global")
    support.make_workflow_projection_outdated(root)
    openspec = support.openspec_skill_root(context, "pi", scope="global")
    for name in OPENSPEC_CORE_SKILL_NAMES:
        shutil.rmtree(openspec / name)
    (openspec / ".zpp-openspec-skills.json").unlink()
    context.results.clear()
    context.openspec_generation_calls.clear()


def install_current_codex_with_historical_hook(context) -> None:
    result = support.invoke(context, ["workflow", "install", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    destination = support.agent_path(context, "codex")
    destination.write_text(
        destination.read_text(encoding="utf-8").replace(
            "zpp resolve --agent codex",
            "zpp resolve",
        ),
        encoding="utf-8",
    )
    context.results.clear()
    context.openspec_generation_calls.clear()


def assert_no_claude_workflow(context) -> None:
    assert not support.workflow_skill_root(context, "claude", scope="global").exists()


def surround_global_surfaces(context) -> None:
    paths = (
        context.home / ".pi/agent/skills/third-party/SKILL.md",
        context.home / ".pi/agent/extensions/neighbor.ts",
        context.home / ".agents/skills/third-party/SKILL.md",
        context.home / ".codex/skills/third-party/SKILL.md",
        context.home / ".claude/unrelated.txt",
    )
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"keep:{path.name}\n", encoding="utf-8")
    context.unrelated_global_bytes = {path: path.read_bytes() for path in paths}


def assert_pi_codex_workflows_current(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    for agent in ("pi", "codex"):
        support.assert_workflow_projection(
            context,
            support.workflow_skill_root(context, agent, scope="global"),
        )


def assert_pi_openspec_generated(context) -> None:
    support.assert_openspec_projection(
        support.openspec_skill_root(context, "pi", scope="global"),
        agent="pi",
        version="1.7.0",
    )


def assert_installed_hooks_current(context) -> None:
    for agent in ("pi", "codex"):
        support.assert_current_agent_integration(context, agent)


def assert_claude_untouched(context) -> None:
    assert not support.agent_path(context, "claude").exists()
    assert not support.workflow_skill_root(context, "claude", scope="global").exists()
    assert not support.openspec_skill_root(context, "claude", scope="global").exists()


def assert_unrelated_global_unchanged(context) -> None:
    assert all(path.read_bytes() == content for path, content in context.unrelated_global_bytes.items())


def install_pi_claude_integrations(context) -> None:
    result = support.invoke(
        context,
        ["workflow", "install", "--agent", "pi", "--agent", "claude"],
    )
    assert result.exit_code == 0, result.output
    context.results.clear()
    context.openspec_generation_calls.clear()


def record_pi_current_projection(context) -> None:
    context.pi_openspec_root = support.openspec_skill_root(context, "pi", scope="global")
    context.pi_openspec_before = support.snapshot(context.pi_openspec_root)


def make_claude_projection_outdated(context) -> None:
    root = support.openspec_skill_root(context, "claude", scope="global")
    manifest = root / ".zpp-openspec-skills.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["openspec_version"] = "0.1.0"
    manifest.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    context.claude_openspec_root = root


def assert_pi_openspec_unchanged(context) -> None:
    assert support.snapshot(context.pi_openspec_root) == context.pi_openspec_before


def assert_claude_openspec_regenerated(context) -> None:
    assert context.openspec_generation_calls == [(('claude',), '1.7.0')]
    support.assert_openspec_projection(
        context.claude_openspec_root,
        agent="claude",
        version="1.7.0",
    )


def assert_claude_detected_version(context) -> None:
    manifest = json.loads(
        (context.claude_openspec_root / ".zpp-openspec-skills.json").read_text(encoding="utf-8")
    )
    assert manifest["openspec_version"] == "1.7.0"


def assert_pi_claude_workflows_current(context) -> None:
    for agent in ("pi", "claude"):
        support.assert_workflow_projection(
            context,
            support.workflow_skill_root(context, agent, scope="global"),
        )


def initialize_with_missing_default(context) -> None:
    support.initialize(context)
    context.missing_default_trait = context.home / ".zpp/profiles/default/traits/bdd-structure-python.md"
    context.missing_default_trait.unlink()


def install_outdated_pi_integration(context) -> None:
    result = support.invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    support.make_workflow_projection_outdated(
        support.workflow_skill_root(context, "pi", scope="global")
    )
    context.results.clear()


def create_modified_claude_workflow(context) -> None:
    result = support.invoke(context, ["workflow", "install", "--agent", "claude"])
    assert result.exit_code == 0, result.output
    root = support.workflow_skill_root(context, "claude", scope="global")
    skill = root / context.workflow_skill_names[0] / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "modified\n", encoding="utf-8")
    context.results.clear()


def record_included_global_surfaces(context) -> None:
    if context.missing_default_trait.exists():
        context.missing_default_trait.unlink()
    context.included_global_before = support.snapshot(context.home)


def assert_conflict_identifies_claude(context) -> None:
    assert context.result.exit_code == 1, context.result.output
    assert ".claude" in context.result.stderr.lower()


def assert_default_unchanged_after_conflict(context) -> None:
    assert not context.missing_default_trait.exists()


def assert_included_global_unchanged(context) -> None:
    assert support.snapshot(context.home) == context.included_global_before


def install_all_global_integrations(context) -> None:
    support.initialize(context)
    result = support.invoke(
        context,
        [
            "workflow",
            "install",
            "--agent",
            "pi",
            "--agent",
            "codex",
            "--agent",
            "claude",
        ],
    )
    assert result.exit_code == 0, result.output
    context.results.clear()
    context.openspec_generation_calls.clear()


def assert_all_openspec_current(context) -> None:
    for agent in ("pi", "codex", "claude"):
        support.assert_openspec_projection(
            support.openspec_skill_root(context, agent, scope="global"),
            agent=agent,
            version="1.7.0",
        )


def assert_default_complete(context) -> None:
    assert (context.home / ".zpp/profiles/default/traits/bdd-structure-python.md").is_file()


def create_local_compatible_and_conflicting_projections(context) -> None:
    support.git_init(context.project)
    result = support.invoke(
        context,
        ["workflow", "install", "--local", "--force", "--agent", "codex"],
    )
    assert result.exit_code == 0, result.output
    conflict = (
        support.workflow_skill_root(context, "claude", scope="local")
        / context.workflow_skill_names[0]
        / "SKILL.md"
    )
    conflict.parent.mkdir(parents=True)
    conflict.write_text("local user content\n", encoding="utf-8")
    context.local_projections_before = support.snapshot(context.project)
    context.global_before = support.snapshot(context.home)
    context.results.clear()
    context.openspec_generation_calls.clear()


def assert_two_updates_no_rewrite(context) -> None:
    assert context.first_update_exit == context.second_update_exit == 0
    assert support.snapshot(context.home) == context.global_before


def assert_no_openspec_regeneration(context) -> None:
    assert context.openspec_generation_calls == []


def assert_local_projections_unchanged(context) -> None:
    assert support.snapshot(context.project) == context.local_projections_before
