from __future__ import annotations

import support
from agent_router import Agent
from behave import given, then, when


@given("ZPP packages the {name} workflow integration")
def packaged_integration(context, name: str) -> None:
    context.agent_name = name
    context.hook = support.hook_for(name)


@given("ZPP packages every supported native trait hook")
def packaged_supported_hooks(context) -> None:
    context.supported_hooks = {agent: support.hook_for(agent.value) for agent in Agent}


@given("a disposable project root")
def disposable_project(context) -> None:
    context.project = support.Project()


@given("the codex workflow integration is installed into that project")
def preinstalled(context) -> None:
    context.project.run_json(
        "workflow",
        "install",
        "--agent",
        "codex",
        "--target",
        str(context.project.root),
    )


@given("only an owned obsolete workflow skill is installed into that project")
def old_only_project(context) -> None:
    context.obsolete = context.project.install_owned_obsolete("zpp-workflow")


@given("the codex workflow integration carries intact former hook ownership")
def former_project_hook(context) -> None:
    context.project.replace_current_hook_with_former()


@given("an unmanaged current workflow destination exists in that project")
def unmanaged_current_project(context) -> None:
    context.conflict = context.project.create_unmanaged_current("zpp-auto")


@when("the packaged native hook is inspected")
def inspect_hook(context) -> None:
    context.payload = support.hook_payload(context.hook)


@when("the post-compaction reinjection strategies are inspected")
def inspect_post_compaction_strategies(context) -> None:
    context.post_compaction_strategies = support.post_compaction_strategies(
        context.supported_hooks
    )


@when("a user installs the codex workflow integration into that project")
def install_integration(context) -> None:
    context.result = context.project.runner.invoke(
        support.app,
        [
            "workflow",
            "install",
            "--agent",
            "codex",
            "--target",
            str(context.project.root),
        ],
        terminal_width=300,
    )
    if context.result.exit_code == 0:
        context.records = support.json.loads(context.result.stdout)


@when("a user updates the codex workflow integration in that project")
def update_integration(context) -> None:
    context.records = context.project.run_json(
        "workflow",
        "update",
        "--agent",
        "codex",
        "--target",
        str(context.project.root),
    )


@when("a user removes that workflow integration")
def remove_integration(context) -> None:
    context.records = context.project.run_json(
        "workflow",
        "remove",
        "--agent",
        "codex",
        "--target",
        str(context.project.root),
    )


@then("the hook declares the {expected} native format")
def hook_format(context, expected: str) -> None:
    assert context.hook.format == expected, context.hook.format
    assert support.NATIVE_FORMATS[Agent(context.agent_name)] == expected


@then("the hook is compatible with only that agent")
def hook_compatibility(context) -> None:
    assert context.hook.compatible_agents == frozenset({Agent(context.agent_name)})


@then("the hook resolves the current repository with {name} as the invoking agent")
def hook_resolves_repository(context, name: str) -> None:
    assert support.resolves_current_repository(context.payload, name), context.payload


@then("every supported agent uses its context-bearing native strategy")
def post_compaction_strategies_match(context) -> None:
    assert context.post_compaction_strategies == {
        "codex": "session-start:compact",
        "claude": "session-start:compact",
        "kimi": "post-compact",
        "pi": "before-agent-start",
    }, context.post_compaction_strategies


@then("the hook declares no guard and no prompt-submit event")
def hook_has_no_guard(context) -> None:
    assert "guard" not in context.payload
    assert "UserPromptSubmit" not in context.payload


@then(
    "Agent Router projects the complete packaged workflow family and zpp-traits "
    "in deterministic order"
)
def projected_family(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert support.lifecycle_inventory(
        context.records
    ) == support.packaged_integration_inventory(Agent.CODEX)
    assert {record["request"] for record in context.records} == {"install"}


@then("the complete current workflow integration replaces the obsolete project skill")
def project_migrated(context) -> None:
    current = [
        record
        for record in context.records
        if not record["asset"].startswith("obsolete-skill:")
        and record["asset"] != "migration"
    ]
    assert len(current) == len(support.packaged_integration_inventory(Agent.CODEX)), (
        context.records
    )
    obsolete = [
        record
        for record in context.records
        if record["asset"] == "obsolete-skill:zpp-workflow"
    ]
    assert len(obsolete) == 1
    assert obsolete[0]["status"] == "removed"
    migration = [record for record in context.records if record["asset"] == "migration"]
    assert len(migration) == 1, context.records
    assert migration[0]["status"] == "complete"
    assert migration[0]["origin"] == "old-only"
    assert migration[0]["current"] == [
        f"{kind}:{name}"
        if kind == "skill" or name != "zpp-traits"
        else "hook"
        for kind, name in support.packaged_integration_inventory(Agent.CODEX)
    ]
    assert migration[0]["surviving_obsolete"] == []
    assert not context.obsolete.exists()


@then("current project hook ownership replaces the former identity")
def project_hook_migrated(context) -> None:
    assert context.project.hook_ownership_states() == ("current", "unmanaged")


@then(
    "installation reports the exact conflict without projecting another family member"
)
def install_conflict_safe(context) -> None:
    compact_output = "".join(context.result.output.replace("│", "").split())
    assert context.result.exit_code != 0, context.result.output
    selected_root = context.project.root.resolve()
    expected = (
        "agent=codex",
        "scope=project",
        f"project_root={selected_root}",
        f"destination={selected_root / '.agents' / 'skills'}",
        "asset=skill:zpp-auto",
    )
    missing = [item for item in expected if item not in compact_output]
    assert not missing, (missing, compact_output)
    assert context.conflict.read_text(encoding="utf-8") == "unmanaged current collision"
    for kind, name in support.packaged_integration_inventory(Agent.CODEX):
        if name == "zpp-auto":
            continue
        if kind == "skill":
            assert not (context.project.root / ".agents" / "skills" / name).exists(), (
                name
            )


@then(
    "Agent Router removes the complete packaged workflow family and zpp-traits "
    "in deterministic order"
)
def removed_family(context) -> None:
    assert support.lifecycle_inventory(
        context.records
    ) == support.packaged_integration_inventory(Agent.CODEX)
    assert {record["request"] for record in context.records} == {"remove"}


@given("a disposable repository with no Bundler lease state")
def repository_without_state(context) -> None:
    context.repository = support.HookRepository()


@when("the packaged hook resolution runs against that repository")
def hook_resolution(context) -> None:
    context.resolution = context.repository.resolve()


@then("the repository traits resolve")
def hook_repository_source(context) -> None:
    bodies = [item["body"] for item in context.resolution["bodies"]]
    assert "hook repository body" in bodies


@then("no session or Bundler lease state is created")
def no_coordination_state(context) -> None:
    assert "session" not in context.resolution
    assert not context.repository.environment.home.exists()


@then("the hook identity is zpp-traits")
def hook_identity(context) -> None:
    assert context.hook.name == "zpp-traits"


@then("no zpp-session compatibility hook is packaged")
def no_compatibility_hook(context) -> None:
    assert "zpp-session" not in context.hook.name
