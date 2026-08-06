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
    relatives = {
        "codex": Path(".codex/skills") if scope == "global" else Path(".agents/skills"),
        "pi": Path(".pi/agent/skills") if scope == "global" else Path(".pi/skills"),
        "claude": Path(".claude/skills"),
    }
    return _projection_roots(base, scope, agents, relatives)


def openspec_projection_roots(
    *,
    home: Path,
    target: Path | None,
    scope: SkillScope,
    agents: Iterable[AgentName],
) -> tuple[SkillProjection, ...]:
    if scope == "local" and target is None:
        raise ValueError("local OpenSpec projection requires a target")
    if scope == "global" and target is not None:
        raise ValueError("global OpenSpec projection does not accept a target")

    base = home if scope == "global" else target
    assert base is not None
    relatives = {
        "codex": Path(".codex/skills"),
        "pi": Path(".pi/agent/skills") if scope == "global" else Path(".pi/skills"),
        "claude": Path(".claude/skills"),
    }
    return _projection_roots(base, scope, agents, relatives)


def _projection_roots(
    base: Path,
    scope: SkillScope,
    agents: Iterable[AgentName],
    relatives: dict[AgentName, Path],
) -> tuple[SkillProjection, ...]:
    projections: list[SkillProjection] = []
    indexes: dict[Path, int] = {}
    for agent in dict.fromkeys(agents):
        root = base / relatives[agent]
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
