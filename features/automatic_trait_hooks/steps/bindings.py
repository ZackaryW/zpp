from __future__ import annotations

import support
from agent_router import Agent
from behave import given, then, when


@given("ZPP packages the {name} workflow integration")
def packaged_integration(context, name: str) -> None:
    context.agent_name = name
    context.hook = support.hook_for(name)


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


@when("the packaged native hook is inspected")
def inspect_hook(context) -> None:
    context.payload = support.hook_payload(context.hook)


@when("a user installs the codex workflow integration into that project")
def install_integration(context) -> None:
    context.records = context.project.run_json(
        "workflow",
        "install",
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


@then("the hook declares no guard and no prompt-submit event")
def hook_has_no_guard(context) -> None:
    assert "guard" not in context.payload
    assert "UserPromptSubmit" not in context.payload


@then("Agent Router projects exactly the workflow skill and the native hook")
def projected_pair(context) -> None:
    assert len(context.records) == 2, context.records
    assert {record["request"] for record in context.records} == {"install"}


@then("Agent Router removes exactly the workflow skill and the native hook")
def removed_pair(context) -> None:
    assert len(context.records) == 2, context.records
    assert {record["request"] for record in context.records} == {"remove"}


@given("a disposable repository with no established session")
def repository_without_session(context) -> None:
    from features.support.coordination import CoordinationEnvironment

    context.coordination = CoordinationEnvironment()
    context.worktree = context.coordination.worktree()


@given(
    "a disposable repository with an established session "
    "contributing a space-scoped trait source"
)
def repository_with_space_source(context) -> None:
    repository_without_session(context)
    context.session = context.coordination.workspace_json(
        "session", str(context.worktree)
    )
    context.expected_body = _bind_space_source(
        context.coordination, context.worktree, context.session["space"]
    )


def _bind_space_source(env, root, space) -> str:
    from openlease import ConfigurationLayout

    from zpp.utils.openlease import create_zpp_openlease

    document = root / "hook-tooling.toml"
    document.write_text(
        '[meta]\nselection = "all"\n\n[[trait]]\n[trait.content]\n'
        'body = "Hook space-scoped body."\n',
        encoding="utf-8",
    )
    create_zpp_openlease(env.home / "openlease").bind_configuration_source(
        "zpp.traits",
        "hook-tooling",
        document,
        "space",
        space,
        codec="toml",
        layout=ConfigurationLayout.DEDICATED.value,
    )
    return "Hook space-scoped body."


@when("the packaged hook resolution runs against that repository")
def hook_resolution(context) -> None:
    context.resolution = context.coordination.resolve_json(
        "--agent", "claude", str(context.worktree)
    )


@when(
    "the packaged hook resolution runs with no explicit space argument "
    "and no space environment value"
)
def hook_resolution_without_space(context) -> None:
    hook_resolution(context)


@then("the session for that repository is established")
def hook_established_session(context) -> None:
    assert context.resolution["session"]
    assert context.resolution["session_note"] is None


@then("the resolved sources include that space-scoped source")
def hook_space_source(context) -> None:
    bodies = [item["body"] for item in context.resolution["bodies"]]
    assert context.resolution["session"] == context.session["space"]
    assert context.expected_body in bodies


@then("no affected claim is declared and no permit is acquired")
def hook_no_permit(context) -> None:
    state = context.coordination.state()
    assert state["leases"] == []
    assert all(
        not item["affected_repository_ids"] and not item["affected_authority_ids"]
        for item in state["spaces"]
    )
