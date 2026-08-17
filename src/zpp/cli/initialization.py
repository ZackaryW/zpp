from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent, Scope

from zpp.artifacts import (
    packaged_companion_skills,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
from zpp.cli.lifecycle import packaged_entries
from zpp.cli.shared import (
    abort_cancelled,
    agent_router,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    render_lifecycle_summary,
    user_action,
)
from zpp.utils.agent_router import (
    project_workflow_hook,
    project_workflow_skill,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents
from zpp.utils.lifecycle import inspect_entries, installed_agents
from zpp.utils.openspec import generated_openspec_skill_sets


def initialize(
    agent: Annotated[
        list[Agent] | None,
        typer.Option("--agent", help="Set up one or more supported agents."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit the complete lifecycle report as JSON."),
    ] = False,
) -> None:
    """Set up the consolidated workflow for agents that carry no ZPP projection."""
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
    installed = user_action(
        lambda: installed_agents(
            inspect_entries(packaged_entries(selection.agents, target=root))
        )
    )
    absent = tuple(item for item in selection.agents if item.value not in installed)
    rejected = [
        {
            "agent": item.value,
            "asset": "-",
            "status": "already-initialized",
            "action": "run `zpp sync` for this agent",
        }
        for item in selection.agents
        if item.value in installed
    ]
    results = user_action(lambda: _initialize_selected(absent, root)) if absent else []
    results.extend(rejected)
    if json_output:
        emit_json(results)
        return
    typer.echo(render_lifecycle_summary("Initialized", len(absent), results))
    for record in rejected:
        typer.echo(
            f"{record['agent']} is already initialized; run `zpp sync` to update it."
        )


def _initialize_selected(
    agents: tuple[Agent, ...],
    root: Path,
) -> list[dict]:
    skill = packaged_workflow_skill()
    companion_skills = packaged_companion_skills()
    results: list[dict] = []
    skill_projection = project_workflow_skill
    hook_projection = project_workflow_hook
    with generated_openspec_skill_sets(agents, cwd=root) as generated:
        generated_by_agent = dict(generated)
        for selected in agents:
            router = agent_router(selected, root)
            hook = packaged_workflow_hook(selected)
            skill_result = skill_projection(
                router,
                skill,
                Scope.USER,
                None,
            )
            hook_result = hook_projection(
                router,
                hook,
                Scope.USER,
                None,
            )
            results.extend((skill_result.to_dict(), hook_result.to_dict()))
            results.extend(
                skill_projection(
                    router,
                    companion_skill,
                    Scope.USER,
                    None,
                ).to_dict()
                for companion_skill in companion_skills
            )
            results.extend(
                skill_projection(
                    router,
                    generated_skill,
                    Scope.USER,
                    None,
                ).to_dict()
                for generated_skill in generated_by_agent[selected]
            )
    return results
