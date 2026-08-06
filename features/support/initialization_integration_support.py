from __future__ import annotations

import json
import shutil

from features.support import zpp_support as support
from zpp.utils.openspec_skills import OPENSPEC_CORE_SKILL_NAMES
from zpp.utils.skill_bundles import WORKFLOW_SKILL_NAMES


def _prepare_workflow_inventory(context) -> None:
    context.workflow_skill_names = WORKFLOW_SKILL_NAMES


def _assert_complete_global_integration(context, agent: str) -> None:
    _prepare_workflow_inventory(context)
    support.assert_workflow_projection(
        context,
        support.workflow_skill_root(context, agent, scope="global"),
    )
    support.assert_openspec_projection(
        support.openspec_skill_root(context, agent, scope="global"),
        agent=agent,
        version=getattr(context, "openspec_version", "1.7.0"),
    )
    support.assert_current_agent_integration(context, agent)


def _assert_no_global_integration(context, agent: str) -> None:
    workflow = support.workflow_skill_root(context, agent, scope="global")
    openspec = support.openspec_skill_root(context, agent, scope="global")
    assert not (workflow / ".zpp-workflow-skills.json").exists()
    assert not (openspec / ".zpp-openspec-skills.json").exists()
    assert all(not (workflow / name).exists() for name in WORKFLOW_SKILL_NAMES)
    assert all(not (openspec / name).exists() for name in OPENSPEC_CORE_SKILL_NAMES)
    assert not support.agent_path(context, agent).exists()


def no_global_integrations(context) -> None:
    _prepare_workflow_inventory(context)
    for agent in ("pi", "codex", "claude"):
        _assert_no_global_integration(context, agent)


def no_skill_projection_exists(context) -> None:
    for agent in ("pi", "codex", "claude"):
        for scope in ("global", "local"):
            workflow = support.workflow_skill_root(context, agent, scope=scope)
            openspec = support.openspec_skill_root(context, agent, scope=scope)
            assert not (workflow / ".zpp-workflow-skills.json").exists()
            assert not (openspec / ".zpp-openspec-skills.json").exists()


def no_selected_surface_changed(context) -> None:
    assert support.snapshot(context.home) == context.agents_before


def assert_pi_complete(context) -> None:
    _assert_complete_global_integration(context, "pi")


def assert_codex_complete(context) -> None:
    _assert_complete_global_integration(context, "codex")


def assert_claude_complete(context) -> None:
    _assert_complete_global_integration(context, "claude")


def assert_codex_complete_native_roots(context) -> None:
    assert support.workflow_skill_root(
        context, "codex", scope="global"
    ) == context.home / ".codex" / "skills"
    _assert_complete_global_integration(context, "codex")


def assert_generated_versions(context) -> None:
    selected = tuple(
        agent
        for agent in ("pi", "codex", "claude")
        if (
            support.openspec_skill_root(context, agent, scope="global")
            / ".zpp-openspec-skills.json"
        ).exists()
    )
    assert selected
    for agent in selected:
        support.assert_openspec_projection(
            support.openspec_skill_root(context, agent, scope="global"),
            agent=agent,
            version=getattr(context, "openspec_version", "1.7.0"),
        )


def assert_generation_boundary(context) -> None:
    assert context.openspec_generation_calls == [(('pi', 'codex'), '1.7.0')]
    support.step_no_generation_temporary_project(context)


def assert_no_instruction_paragraphs(context) -> None:
    for agent in ("pi", "codex"):
        source = support.agent_path(context, agent).read_text(encoding="utf-8")
        assert "instruction paragraph" not in source.lower()


def assert_claude_no_instruction_paragraph(context) -> None:
    source = support.agent_path(context, "claude").read_text(encoding="utf-8")
    assert "instruction paragraph" not in source.lower()


def distinct_authored_default(context) -> None:
    root = context.home / ".zpp" / "profiles" / "default"
    config = root / "config.json"
    document = json.loads(config.read_text(encoding="utf-8"))
    document["traitsConfig"]["owner-distinctive"] = {"kept": True}
    config.write_text(
        json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    context.default_before = support.snapshot(root)
    context.existing_user_state = support.snapshot(context.home / ".zpp")


def assert_default_unchanged(context) -> None:
    assert support.snapshot(
        context.home / ".zpp" / "profiles" / "default"
    ) == context.default_before


def compatible_pi_surrounded(context) -> None:
    _prepare_workflow_inventory(context)
    result = support.invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    skill_neighbor = (
        support.workflow_skill_root(context, "pi", scope="global")
        / "owner-skill"
        / "SKILL.md"
    )
    skill_neighbor.parent.mkdir()
    skill_neighbor.write_text("owner skill\n", encoding="utf-8")
    hook_neighbor = context.home / ".pi" / "agent" / "extensions" / "owner.ts"
    hook_neighbor.write_text("owner extension\n", encoding="utf-8")
    context.pi_unmanaged = {
        skill_neighbor: skill_neighbor.read_bytes(),
        hook_neighbor: hook_neighbor.read_bytes(),
    }
    context.results.clear()
    context.openspec_generation_calls.clear()


def record_pi_complete(context) -> None:
    context.pi_complete_before = support.snapshot(context.home / ".pi")


def assert_pi_complete_unchanged(context) -> None:
    assert support.snapshot(context.home / ".pi") == context.pi_complete_before


def partial_codex_openspec_only(context) -> None:
    _prepare_workflow_inventory(context)
    result = support.invoke(context, ["workflow", "install", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    global_root = support.workflow_skill_root(context, "codex", scope="global")
    for name in WORKFLOW_SKILL_NAMES:
        shutil.rmtree(global_root / name)
    (global_root / ".zpp-workflow-skills.json").unlink()
    support.agent_path(context, "codex").unlink()

    support.git_init(context.project)
    result = support.invoke(
        context,
        ["workflow", "install", "--local", "--with-openspec", "--agent", "codex"],
    )
    assert result.exit_code == 0, result.output
    support.agent_path(context, "codex").unlink()
    context.results.clear()
    context.openspec_generation_calls.clear()


def record_codex_openspec_and_local(context) -> None:
    context.codex_openspec_before = support.snapshot(
        support.openspec_skill_root(context, "codex", scope="global")
    )
    context.codex_local_before = support.snapshot(context.project)


def assert_codex_openspec_unchanged(context) -> None:
    root = support.openspec_skill_root(context, "codex", scope="global")
    current = support.snapshot(root)
    for name in WORKFLOW_SKILL_NAMES:
        current.pop(name, None)
        for path in tuple(current):
            if path.startswith(f"{name}/"):
                current.pop(path)
    current.pop(".zpp-workflow-skills.json", None)

    expected = dict(context.codex_openspec_before)
    for name in WORKFLOW_SKILL_NAMES:
        expected.pop(name, None)
        for path in tuple(expected):
            if path.startswith(f"{name}/"):
                expected.pop(path)
    expected.pop(".zpp-workflow-skills.json", None)
    assert current == expected


def assert_codex_local_unchanged(context) -> None:
    assert support.snapshot(context.project) == context.codex_local_before


def outdated_pi_integration(context) -> None:
    _prepare_workflow_inventory(context)
    result = support.invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    support.make_workflow_projection_outdated(
        support.workflow_skill_root(context, "pi", scope="global")
    )
    context.openspec_version = "1.8.0"
    context.results.clear()
    context.openspec_generation_calls.clear()


def assert_pi_openspec_is_outdated(context) -> None:
    manifest = json.loads(
        (
            support.openspec_skill_root(context, "pi", scope="global")
            / ".zpp-openspec-skills.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["openspec_version"] != context.openspec_version


def record_unrelated_pi(context) -> None:
    path = context.home / ".pi" / "agent" / "skills" / "owner-skill" / "SKILL.md"
    path.parent.mkdir()
    path.write_text("owner skill\n", encoding="utf-8")
    context.unrelated_pi = {path: path.read_bytes()}


def run_init_codex(context) -> None:
    support.invoke(context, ["init", "--agent", "codex"])


def run_init_pi(context) -> None:
    support.invoke(context, ["init", "--agent", "pi"])


def assert_pi_new_openspec_version(context) -> None:
    support.assert_openspec_projection(
        support.openspec_skill_root(context, "pi", scope="global"),
        agent="pi",
        version="1.8.0",
    )


def assert_unrelated_pi_unchanged(context) -> None:
    assert all(path.read_bytes() == content for path, content in context.unrelated_pi.items())


def record_all_claude_destinations(context) -> None:
    context.claude_global_before = support.snapshot(context.home / ".claude")


def assert_all_claude_destinations_unchanged(context) -> None:
    assert support.snapshot(context.home / ".claude") == context.claude_global_before


def pi_has_no_global_integration(context) -> None:
    _assert_no_global_integration(context, "pi")


def codex_openspec_conflict(context) -> None:
    path = (
        support.openspec_skill_root(context, "codex", scope="global")
        / OPENSPEC_CORE_SKILL_NAMES[0]
        / "SKILL.md"
    )
    path.parent.mkdir(parents=True)
    path.write_text("owner conflict\n", encoding="utf-8")
    context.conflicting_path = path


def record_selected_destinations(context) -> None:
    context.selected_global_before = {
        context.home / ".pi": support.snapshot(context.home / ".pi"),
        context.home / ".codex": support.snapshot(context.home / ".codex"),
    }


def assert_selected_destinations_unchanged(context) -> None:
    for root, before in context.selected_global_before.items():
        assert support.snapshot(root) == before


def assert_init_help(context) -> None:
    text = context.init_help.lower()
    assert "bootstrap missing global user state" in text
    assert "completely set up selected agents" in text
    assert "complete global integration" in text
