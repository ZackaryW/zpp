from __future__ import annotations

from pathlib import Path
from typing import Annotated

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
from zpp.utils.agent_router import project_workflow_hook, project_workflow_skill
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents


def initialize(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Set up one or more supported agents."),
    ] = None,
) -> None:
    """Set up the consolidated workflow for selected agents."""
    try:
        selection = select_many_agents(
            tuple(agent or ()),
            required=False,
            interactive=interactive_terminal(),
            prompt=prompt_agent_selection,
        )
    except AgentSelectionError as error:
        raise typer.BadParameter(str(error), param_hint="--agent") from error
    if selection.cancelled:
        abort_cancelled()
    root = Path.cwd().resolve()
    skill = packaged_workflow_skill()
    results = []
    for selected in selection.agents:
        router = agent_router(selected, root)
        hook = packaged_workflow_hook(selected)
        skill_result = user_action(
            lambda selected_router=router: project_workflow_skill(
                selected_router,
                skill,
                Scope.USER,
                None,
            )
        )
        hook_result = user_action(
            lambda selected_router=router, selected_hook=hook: project_workflow_hook(
                selected_router,
                selected_hook,
                Scope.USER,
                None,
            )
        )
        results.extend((skill_result.to_dict(), hook_result.to_dict()))
    emit_json(results)
