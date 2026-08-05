from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from zpp.cli.shared import AgentOption, interactive_terminal_available, run_domain
from zpp.core.agents import as_agent_names, configure_agents
from zpp.core.state import initialize_user_state
from zpp.utils.agent_selection import select_agents
from zpp.utils.models import CancelledAgentSelection


def init_command(
    agent: Annotated[
        list[AgentOption] | None,
        typer.Option("--agent", help="Configure a global agent lifecycle hook."),
    ] = None,
) -> None:
    """Bootstrap missing global user state and configure selected agent hooks."""
    def action() -> None:
        home = Path.home()
        initialize_user_state(home)
        selected = tuple(item.value for item in agent or ())
        if not selected and interactive_terminal_available():
            selection = select_agents(("pi", "codex", "claude"))
            if isinstance(selection, CancelledAgentSelection):
                typer.echo("Agent selection cancelled.", err=True)
                raise typer.Exit(1)
            selected = selection.agents
        if selected:
            configure_agents(home, as_agent_names(selected))

    run_domain(action)
