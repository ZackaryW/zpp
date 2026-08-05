from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from zpp.utils.agent_bootstrap import plan_agent_integrations
from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.models import AgentName


def configure_agents(home: Path, requested: Iterable[AgentName]) -> None:
    apply_mutation_plan(plan_agent_integrations(home, requested))


def as_agent_names(values: Iterable[str]) -> tuple[AgentName, ...]:
    return tuple(cast(AgentName, value) for value in values)
