from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from agent_router import Agent, Scope

from zpp.artifacts import packaged_workflow_hook, packaged_workflow_skill
from zpp.cli.shared import (
    abort_cancelled,
    agent_router,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    user_action,
)
from zpp.utils.agent_router import (
    project_workflow_hook,
    project_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents

app = typer.Typer(
    help="Manage the consolidated workflow skill and hook through Agent Router.",
    no_args_is_help=True,
)


def _manage(
    operation: Literal["install", "update", "remove"],
    agents: list[Agent] | None,
    target: Path,
    global_: bool,
) -> None:
    if global_ and target != Path("."):
        raise typer.BadParameter(
            "--target and --global are mutually exclusive",
            param_hint="--target",
        )
    try:
        selection = select_many_agents(
            tuple(agents or ()),
            required=True,
            interactive=interactive_terminal(),
            prompt=prompt_agent_selection,
        )
    except AgentSelectionError as error:
        raise typer.BadParameter(str(error), param_hint="--agent") from error
    if selection.cancelled:
        abort_cancelled()

    project = target.resolve()
    scope = Scope.USER if global_ else Scope.PROJECT
    project_root = None if global_ else project
    skill = packaged_workflow_skill()
    results = []
    for agent in selection.agents:
        router = agent_router(agent, project)
        hook = packaged_workflow_hook(agent)
        if operation == "remove":
            hook_result = user_action(
                lambda selected_router=router, selected_hook=hook: (
                    remove_workflow_hook(
                        selected_router, selected_hook.name, scope, project_root
                    )
                )
            )
            skill_result = user_action(
                lambda selected_router=router: remove_workflow_skill(
                    selected_router, skill.name, scope, project_root
                )
            )
        else:
            skill_result = user_action(
                lambda selected_router=router: project_workflow_skill(
                    selected_router,
                    skill,
                    scope,
                    project_root,
                    replace_project=(
                        operation == "update" and scope is Scope.PROJECT
                    ),
                )
            )
            hook_result = user_action(
                lambda selected_router=router, selected_hook=hook: (
                    project_workflow_hook(
                        selected_router, selected_hook, scope, project_root
                    )
                )
            )
        for result in (skill_result, hook_result):
            item = result.to_dict()
            item["request"] = operation
            results.append(item)
    emit_json(results)


def _options(
    agent: list[Agent] | None,
    target: Path,
    global_: bool,
) -> tuple[list[Agent] | None, Path, bool]:
    return agent, target, global_


@app.command("install")
def install(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Supported agent; repeat to select several."),
    ] = None,
    target: Annotated[
        Path,
        typer.Option("--target", help="Project root for project scope."),
    ] = Path("."),
    global_: Annotated[
        bool,
        typer.Option("--global", help="Install in the user scope."),
    ] = False,
) -> None:
    """Install the consolidated workflow skill and native trait hook."""
    _manage("install", *_options(agent, target, global_))


@app.command("update")
def update(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Supported agent; repeat to select several."),
    ] = None,
    target: Annotated[
        Path,
        typer.Option("--target", help="Project root for project scope."),
    ] = Path("."),
    global_: Annotated[
        bool,
        typer.Option("--global", help="Update in the user scope."),
    ] = False,
) -> None:
    """Update an Agent Router-owned workflow installation."""
    _manage("update", *_options(agent, target, global_))


@app.command("remove")
def remove(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Supported agent; repeat to select several."),
    ] = None,
    target: Annotated[
        Path,
        typer.Option("--target", help="Project root for project scope."),
    ] = Path("."),
    global_: Annotated[
        bool,
        typer.Option("--global", help="Remove from the user scope."),
    ] = False,
) -> None:
    """Remove an intact Agent Router-owned workflow installation."""
    _manage("remove", *_options(agent, target, global_))
