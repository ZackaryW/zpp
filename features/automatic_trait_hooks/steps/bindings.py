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
