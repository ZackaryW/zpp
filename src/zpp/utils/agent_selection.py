from __future__ import annotations

from collections.abc import Sequence
from typing import cast

import questionary

from zpp.utils.models import (
    AgentName,
    AgentSelection,
    CancelledAgentSelection,
    ConfirmedAgentSelection,
)


def select_agents(choices: Sequence[AgentName]) -> AgentSelection:
    try:
        answer = questionary.checkbox(
            "Configure agent applications",
            choices=list(choices),
        ).ask()
    except KeyboardInterrupt:
        return CancelledAgentSelection()
    if answer is None:
        return CancelledAgentSelection()
    if not isinstance(answer, list) or any(item not in choices for item in answer):
        raise ValueError("agent selector returned an invalid result")
    if len(set(answer)) != len(answer):
        raise ValueError("agent selector returned duplicate agents")
    return ConfirmedAgentSelection(cast(tuple[AgentName, ...], tuple(answer)))
