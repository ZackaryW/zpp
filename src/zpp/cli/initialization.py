from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from agent_router import Agent, Scope

from zpp.cli.lifecycle import inspect_installations, reconcile_installations
from zpp.cli.shared import (
    abort_cancelled,
    emit_json,
    interactive_terminal,
    prompt_agent_selection,
    render_lifecycle_summary,
    user_action,
)
from zpp.utils.agent_selection import AgentSelectionError, select_many_agents


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
    inspections = user_action(
        lambda: inspect_installations(
            selection.agents,
            target=root,
            scope=Scope.USER,
            project_root=None,
            include_companions=True,
        )
    )
    selected = tuple(
        item for item in inspections if item.classification in {"absent", "old-only"}
    )
    blocked = tuple(
        item for item in inspections if item.classification == "obsolete-conflict"
    )
    rejected = [
        {
            "agent": item.agent.value,
            "asset": "-",
            "status": "already-initialized",
            "action": "run `zpp sync` for this agent",
        }
        for item in inspections
        if item.classification == "current"
    ]
    results = (
        user_action(lambda: reconcile_installations(selected, absent="install"))
        if selected
        else []
    )
    if blocked:
        results.extend(user_action(lambda: reconcile_installations(blocked)))
    results.extend(rejected)
    if json_output:
        emit_json(results)
        return
    typer.echo(render_lifecycle_summary("Initialized", len(selected), results))
    for record in rejected:
        typer.echo(
            f"{record['agent']} is already initialized; run `zpp sync` to update it."
        )
    for record in results:
        if record.get("asset") == "migration" and record.get("status") == "conflict":
            typer.echo(
                f"{record['agent']} migration blocked by obsolete conflicts: "
                + ", ".join(record.get("surviving_obsolete", []))
            )
