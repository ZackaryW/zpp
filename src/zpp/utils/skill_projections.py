from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from zpp.utils.models import AgentName
from zpp.utils.skill_bundles import (
    SkillBundle,
    SkillProjectionInspection,
    inspect_skill_projection,
)


SkillScope = Literal["local", "global"]


@dataclass(frozen=True, slots=True)
class SkillProjection:
    root: Path
    scope: SkillScope
    agents: tuple[AgentName, ...]


def skill_projection_roots(
    *,
    home: Path,
    target: Path | None,
    scope: SkillScope,
    agents: Iterable[AgentName],
) -> tuple[SkillProjection, ...]:
    if scope == "local" and target is None:
        raise ValueError("local skill projection requires a target")
    if scope == "global" and target is not None:
        raise ValueError("global skill projection does not accept a target")

    base = home if scope == "global" else target
    assert base is not None
    projections: list[SkillProjection] = []
    indexes: dict[Path, int] = {}
    for agent in dict.fromkeys(agents):
        relative = Path(".claude/skills") if agent == "claude" else Path(".agents/skills")
        root = base / relative
        if root not in indexes:
            indexes[root] = len(projections)
            projections.append(SkillProjection(root, scope, (agent,)))
        else:
            index = indexes[root]
            current = projections[index]
            projections[index] = replace(current, agents=(*current.agents, agent))
    return tuple(projections)


def inspect_skill_scopes(
    projections: Iterable[SkillProjection],
    bundle: SkillBundle,
) -> tuple[SkillProjectionInspection, ...]:
    return tuple(
        replace(
            inspect_skill_projection(projection.root, bundle),
            scope=projection.scope,
            agents=projection.agents,
        )
        for projection in projections
    )
