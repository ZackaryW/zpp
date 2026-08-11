from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent, Scope

from zpp.artifacts import packaged_workflow_skill
from zpp.cli.shared import (
    abort_cancelled,
    agent_router,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    user_action,
)
from zpp.utils.agent_router import project_workflow_skill
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
        result = user_action(
            lambda selected_agent=selected: project_workflow_skill(
                agent_router(selected_agent, root),
                skill,
                Scope.USER,
                None,
            )
        )
        results.append(result.to_dict())
    emit_json(results)
