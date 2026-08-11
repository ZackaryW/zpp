from __future__ import annotations

import pytest
from agent_router import Agent

from zpp.utils.agent_selection import (
    AgentSelection,
    AgentSelectionError,
    normalize_agent_selection,
    select_many_agents,
    select_one_agent,
)


def test_normalize_agents_deduplicates_in_first_seen_order() -> None:
    selection = normalize_agent_selection((Agent.CODEX, Agent.PI, Agent.CODEX))

    assert selection == AgentSelection((Agent.CODEX, Agent.PI))


def test_required_interactive_selection_preserves_prompt_cancellation() -> None:
    selection = select_many_agents(
        (),
        required=True,
        interactive=True,
        prompt=lambda: AgentSelection((), cancelled=True),
    )

    assert selection.cancelled is True
    assert selection.agents == ()


def test_required_noninteractive_selection_rejects_omission() -> None:
    with pytest.raises(AgentSelectionError, match="one or more --agent"):
        select_many_agents(
            (),
            required=True,
            interactive=False,
            prompt=lambda: AgentSelection(()),
        )


def test_one_agent_selection_rejects_several_values() -> None:
    with pytest.raises(AgentSelectionError, match="exactly one --agent"):
        select_one_agent((Agent.CODEX, Agent.PI), required=False)
