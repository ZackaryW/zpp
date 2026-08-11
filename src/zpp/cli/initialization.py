from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent, Scope

from zpp.artifacts import (
    packaged_authoring_skills,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
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
from zpp.utils.openspec import generated_openspec_skill_sets


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
    results = user_action(
        lambda: _initialize_selected(selection.agents, root)
    )
    emit_json(results)


def _initialize_selected(agents: tuple[Agent, ...], root: Path) -> list[dict]:
    skill = packaged_workflow_skill()
    authoring_skills = packaged_authoring_skills()
    results: list[dict] = []
    with generated_openspec_skill_sets(agents, cwd=root) as generated:
        generated_by_agent = dict(generated)
        for selected in agents:
            router = agent_router(selected, root)
            hook = packaged_workflow_hook(selected)
            skill_result = project_workflow_skill(
                router,
                skill,
                Scope.USER,
                None,
            )
            hook_result = project_workflow_hook(
                router,
                hook,
                Scope.USER,
                None,
            )
            results.extend((skill_result.to_dict(), hook_result.to_dict()))
            results.extend(
                project_workflow_skill(
                    router,
                    authoring_skill,
                    Scope.USER,
                    None,
                ).to_dict()
                for authoring_skill in authoring_skills
            )
            results.extend(
                project_workflow_skill(
                    router,
                    generated_skill,
                    Scope.USER,
                    None,
                ).to_dict()
                for generated_skill in generated_by_agent[selected]
            )
    return results
