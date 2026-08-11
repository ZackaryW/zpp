from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

from agent_router import Agent


class AgentSelectionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AgentSelection:
    agents: tuple[Agent, ...]
    cancelled: bool = False


def normalize_agent_selection(values: Iterable[Agent]) -> AgentSelection:
    selected: list[Agent] = []
    seen: set[Agent] = set()
    for value in values:
        agent = Agent(value)
        if agent in seen:
            continue
        seen.add(agent)
        selected.append(agent)
    return AgentSelection(tuple(selected))


def select_many_agents(
    values: Sequence[Agent],
    *,
    required: bool,
    interactive: bool,
    prompt: Callable[[], AgentSelection],
) -> AgentSelection:
    if values:
        return normalize_agent_selection(values)
    if interactive:
        selection = prompt()
        if selection.cancelled:
            return selection
        normalized = normalize_agent_selection(selection.agents)
        if len(normalized.agents) != len(selection.agents):
            raise AgentSelectionError("agent selector returned duplicate agents")
        if required and not normalized.agents:
            raise AgentSelectionError("one or more --agent values are required")
        return normalized
    if required:
        raise AgentSelectionError(
            "one or more --agent values are required without an interactive terminal"
        )
    return AgentSelection(())


def select_one_agent(
    values: Sequence[Agent],
    *,
    required: bool,
) -> Agent | None:
    if len(values) > 1:
        raise AgentSelectionError("exactly one --agent may be selected")
    if not values:
        if required:
            raise AgentSelectionError("exactly one --agent is required")
        return None
    return Agent(values[0])
