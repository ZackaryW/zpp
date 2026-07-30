from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from zpp.utils.agent_bootstrap import (
    bootstrap_claude_code,
    bootstrap_codex,
    bootstrap_pi,
    load_packaged_pi_extension,
    preflight_claude_code,
    preflight_codex,
    preflight_pi,
)
from zpp.utils.models import AgentName, ManagedStateError


def configure_agents(home: Path, requested: Iterable[AgentName]) -> None:
    agents = tuple(dict.fromkeys(requested))
    artifact = load_packaged_pi_extension() if "pi" in agents else None

    for agent in agents:
        try:
            if agent == "pi":
                assert artifact is not None
                preflight_pi(home, artifact)
            elif agent == "codex":
                preflight_codex(home)
            else:
                preflight_claude_code(home)
        except ManagedStateError as error:
            raise ManagedStateError(f"{_agent_destination(home, agent)}: {error}") from error

    for agent in agents:
        try:
            if agent == "pi":
                assert artifact is not None
                bootstrap_pi(home, artifact)
            elif agent == "codex":
                bootstrap_codex(home)
            else:
                bootstrap_claude_code(home)
        except ManagedStateError as error:
            raise ManagedStateError(f"{_agent_destination(home, agent)}: {error}") from error


def as_agent_names(values: Iterable[str]) -> tuple[AgentName, ...]:
    return tuple(cast(AgentName, value) for value in values)


def _agent_destination(home: Path, agent: AgentName) -> Path:
    if agent == "pi":
        return home / ".pi" / "agent" / "extensions" / "zpp" / "index.ts"
    if agent == "codex":
        return home / ".codex" / "hooks.json"
    return home / ".claude" / "settings.json"
