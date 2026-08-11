from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

import questionary
import typer
from agent_router import Agent, AgentEnvironment, AgentRouter, AgentRouterError
from openlease import OpenLeaseError

from zpp.utils.agent_router import ZppTraitArtifactExtension
from zpp.utils.agent_selection import AgentSelection, AgentSelectionError
from zpp.utils.product_home import ZppHome

AGENT_CHOICES = (
    ("Codex", Agent.CODEX),
    ("Claude Code", Agent.CLAUDE),
    ("Pi", Agent.PI),
    ("Kimi", Agent.KIMI),
)


@dataclass(frozen=True, slots=True)
class Runtime:
    home: ZppHome

    @property
    def state_root(self) -> Path:
        return self.home.state_root


def runtime(ctx: typer.Context) -> Runtime:
    value = ctx.ensure_object(Runtime)
    return value


def agent_router(agent: Agent, target: Path) -> AgentRouter:
    resolved = target.resolve()
    home = Path.home().resolve()
    return AgentRouter(
        agent,
        home=home,
        environment=AgentEnvironment(home, resolved),
        extensions=(ZppTraitArtifactExtension(),),
    )


def interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def prompt_agent_selection() -> AgentSelection:
    try:
        answer = questionary.checkbox(
            "Configure agent applications",
            choices=[
                questionary.Choice(title=label, value=agent)
                for label, agent in AGENT_CHOICES
            ],
        ).ask()
    except (EOFError, KeyboardInterrupt):
        return AgentSelection((), cancelled=True)
    if answer is None:
        return AgentSelection((), cancelled=True)
    if not isinstance(answer, list) or any(
        not isinstance(item, Agent) for item in answer
    ):
        raise AgentSelectionError("agent selector returned an invalid result")
    return AgentSelection(tuple(answer))


def abort_cancelled() -> NoReturn:
    typer.echo("Agent selection cancelled.", err=True)
    raise typer.Abort()


def emit_json(value: object) -> None:
    typer.echo(json.dumps(value, ensure_ascii=False, sort_keys=True))


def user_action[T](action: Callable[[], T]) -> T:
    try:
        return action()
    except (AgentRouterError, OpenLeaseError, OSError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error
