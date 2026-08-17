from __future__ import annotations

from pathlib import Path

import support
from agent_router import Agent
from behave import given, then, when

from zpp.cli.shared import agent_router
from zpp.utils.agent_selection import (
    AgentSelection,
    AgentSelectionError,
    normalize_agent_selection,
    select_many_agents,
    select_one_agent,
)
from zpp.utils.openlease import create_zpp_openlease


@given("a disposable repository")
def disposable_repository(context) -> None:
    context.repository = support.Repository()


@given("a disposable repository with a committed base")
def committed_repository(context) -> None:
    context.repository = support.Repository()
    context.repository.init_git()
    (context.repository.root / "tracked.txt").write_text("base\n", encoding="utf-8")
    context.repository.git("add", ".")
    context.repository.git("commit", "--quiet", "-m", "base")


@given("the public command help is available")
def public_help(context) -> None:
    context.root_help = support.help_for()
    context.workflow_help = support.help_for("workflow")
    context.trait_help = support.help_for("trait")


@given("an explicit agent selection repeating one agent")
def repeated_selection(context) -> None:
    context.selection = normalize_agent_selection((Agent.CODEX, Agent.PI, Agent.CODEX))


@given("no agent is supplied and the terminal is interactive")
def interactive_selection(context) -> None:
    context.interactive = True


@given("no agent is supplied and no interactive terminal is available")
def noninteractive_selection(context) -> None:
    try:
        select_many_agents(
            (),
            required=True,
            interactive=False,
            prompt=lambda: AgentSelection(()),
        )
    except AgentSelectionError as error:
        context.error = error
    else:
        context.error = None


@given("several invoking agents are supplied where one is required")
def several_invoking(context) -> None:
    try:
        select_one_agent((Agent.CODEX, Agent.PI), required=False)
    except AgentSelectionError as error:
        context.error = error
    else:
        context.error = None


@when("a caller explicitly initializes the repository context and a bdd trait")
def initialize_documents(context) -> None:
    repository = context.repository
    repository.documents.initialize_context(repository.root)
    repository.documents.initialize_trait(
        repository.root,
        "bdd",
        {
            "meta": {"selection": "first-win"},
            "trait": [{"content": {"body": "repository"}}],
        },
    )
    context.bound = repository.documents.read_repository(repository.root)


@when("the caller cancels the selection prompt")
def cancel_prompt(context) -> None:
    context.selection = select_many_agents(
        (),
        required=True,
        interactive=context.interactive,
        prompt=lambda: AgentSelection((), cancelled=True),
    )


@when("the caller initializes repository behavior verification")
def initialize_behavior(context) -> None:
    context.behavior_home = context.repository.base / "behavior-home"
    context.result = context.repository.run_in_root(
        "--path", str(context.behavior_home), "behave", "init"
    )


@when("the caller builds the codex agent router for that repository")
def build_router(context) -> None:
    context.router = agent_router(Agent.CODEX, context.repository.root)


@then("exactly the context document and that trait document exist")
def documents_exist(context) -> None:
    assert context.repository.tracked_files() == [
        ".zpp/traits/bdd.toml",
        ".zpp/zpp.toml",
    ]


@then("the bound repository source exposes only the bdd family")
def bound_families(context) -> None:
    assert context.bound.context is not None
    assert [item.family for item in context.bound.source.documents] == ["bdd"]


@then("every established root command is exposed")
def root_commands(context) -> None:
    assert context.root_help.exit_code == 0
    for name in support.COMMAND_NAMES:
        assert name in context.root_help.stdout, name


@then("the grouped workflow exposes install update and remove")
def workflow_operations(context) -> None:
    assert context.workflow_help.exit_code == 0
    for name in support.WORKFLOW_OPERATIONS:
        assert name in context.workflow_help.stdout, name


@then("no space or legacy install-workflow command is exposed")
def no_legacy_commands(context) -> None:
    assert "space" not in context.root_help.stdout
    assert "install-workflow" not in context.root_help.stdout


@then("the normalized selection keeps first-seen order without duplicates")
def normalized_order(context) -> None:
    assert context.selection.agents == (Agent.CODEX, Agent.PI)


@then("the selection reports cancellation rather than choosing an agent")
def selection_cancelled(context) -> None:
    assert context.selection.cancelled
    assert context.selection.agents == ()


@then("the selection is rejected rather than defaulting to every agent")
@then("the selection is rejected")
def selection_rejected(context) -> None:
    assert context.error is not None
    assert isinstance(context.error, AgentSelectionError)


@then("a repository behavior mapping exists")
def mapping_exists(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert (context.repository.root / "zpp.behave.yaml").is_file()


@then("no OpenLease space is created")
def no_space(context) -> None:
    snapshot = create_zpp_openlease(context.behavior_home / "openlease").snapshot()
    assert snapshot.spaces == ()


@then("the router resolves the user home and that repository as its project root")
def router_bound(context) -> None:
    assert context.router.environment.root == Path.home().resolve()
    assert context.router.environment.project_root == context.repository.root.resolve()
