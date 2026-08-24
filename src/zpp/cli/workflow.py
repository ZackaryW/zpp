from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from agent_router import Agent, Scope

from zpp.artifacts import packaged_workflow_hook, packaged_workflow_skills
from zpp.cli.lifecycle import (
    inspect_installations,
    preflight_first_install,
    reconcile_installations,
)
from zpp.cli.shared import (
    abort_cancelled,
    agent_router,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    user_action,
)
from zpp.utils.agent_router import (
    remove_workflow_hook,
    remove_workflow_skill,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents

app = typer.Typer(
    help="Manage the packaged workflow family and hook through Agent Router.",
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
    skills = packaged_workflow_skills()
    results: list[dict[str, object]] = []
    if operation in {"install", "update"}:
        inspections = user_action(
            lambda: inspect_installations(
                selection.agents,
                target=project,
                scope=scope,
                project_root=project_root,
                include_companions=False,
                explicit_project_update=(
                    operation == "update" and scope is Scope.PROJECT
                ),
                migrate_former_hooks=operation == "update",
            )
        )
        if operation == "install":
            conflict = preflight_first_install(inspections)
            if conflict is not None:
                raise typer.BadParameter(
                    "workflow install blocked: "
                    f"agent={conflict['agent']} scope={conflict['scope']} "
                    f"project_root={conflict['project_root']} "
                    f"destination={conflict['destination']} "
                    f"asset={conflict['asset']} status={conflict['status']}: "
                    f"{conflict['reason']}"
                )
        results = user_action(
            lambda: reconcile_installations(
                inspections,
                force=operation == "update",
                absent="install",
                explicit_update=(operation == "update" and scope is Scope.PROJECT),
            )
        )
    else:
        for agent in selection.agents:
            router = agent_router(agent, project)
            hook = packaged_workflow_hook(agent)
            hook_result = user_action(
                lambda selected_router=router, selected_hook=hook: remove_workflow_hook(
                    selected_router, selected_hook.name, scope, project_root
                )
            )
            skill_results = [
                user_action(
                    lambda selected_router=router, selected_skill=skill: (
                        remove_workflow_skill(
                            selected_router,
                            selected_skill.name,
                            scope,
                            project_root,
                        )
                    )
                )
                for skill in reversed(skills)
            ]
            skill_results.reverse()
            for result in (*skill_results, hook_result):
                results.append(result.to_dict())
    for item in results:
        asset = str(item.get("asset", ""))
        if asset == "hook":
            item.setdefault("kind", "hook")
            item.setdefault("name", "zpp-traits")
        elif asset.startswith("skill:"):
            item.setdefault("kind", "skill")
            item.setdefault("name", asset.removeprefix("skill:"))
        elif asset.startswith("obsolete-skill:"):
            item.setdefault("kind", "skill")
            item.setdefault("name", asset.removeprefix("obsolete-skill:"))
        item["request"] = operation
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
    """Install the packaged workflow family and native trait hook."""
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
    """Update an Agent Router-owned workflow-family installation."""
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
    """Remove an intact Agent Router-owned workflow-family installation."""
    _manage("remove", *_options(agent, target, global_))
