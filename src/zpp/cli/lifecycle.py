"""Shared projection inventory used by every ZPP lifecycle command."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from agent_router import Agent, Scope, Skill

from zpp.artifacts import (
    packaged_companion_skills,
    packaged_workflow_hook,
    packaged_workflow_skill,
)
from zpp.cli.shared import agent_router
from zpp.utils.agent_router import (
    inspect_workflow_hook,
    inspect_workflow_skill,
    project_workflow_hook,
    project_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
    reproject_workflow_hook,
    reproject_workflow_skill,
)
from zpp.utils.lifecycle import LifecycleEntry

SUPPORTED_AGENTS = (Agent.CODEX, Agent.CLAUDE, Agent.PI, Agent.KIMI)


def _skill_entry(router, skill: Skill, agent: str, kind: str) -> LifecycleEntry:
    return LifecycleEntry(
        agent=agent,
        kind=kind,
        inspect=lambda: inspect_workflow_skill(router, skill, Scope.USER, None),
        project=lambda: project_workflow_skill(router, skill, Scope.USER, None),
        remove=lambda: remove_workflow_skill(router, skill.name, Scope.USER, None),
        reproject=lambda: reproject_workflow_skill(router, skill, Scope.USER, None),
    )


def packaged_entries(
    agents: Sequence[Agent] = SUPPORTED_AGENTS,
    *,
    target: Path | None = None,
) -> tuple[LifecycleEntry, ...]:
    """Build the packaged hook, workflow skill, and companion skill entries.

    These are inspectable without generating anything, so initialization can
    decide whether an agent is already installed without invoking OpenSpec.
    """
    resolved = (target or Path.cwd()).resolve()
    skill = packaged_workflow_skill()
    companions = packaged_companion_skills()
    entries: list[LifecycleEntry] = []
    for agent in agents:
        router = agent_router(agent, resolved)
        hook = packaged_workflow_hook(agent)
        entries.append(
            LifecycleEntry(
                agent=agent.value,
                kind="hook",
                inspect=(
                    lambda bound_router=router, bound_hook=hook: inspect_workflow_hook(
                        bound_router, bound_hook, Scope.USER, None
                    )
                ),
                project=(
                    lambda bound_router=router, bound_hook=hook: project_workflow_hook(
                        bound_router, bound_hook, Scope.USER, None
                    )
                ),
                remove=(
                    lambda bound_router=router, bound_hook=hook: remove_workflow_hook(
                        bound_router, bound_hook.name, Scope.USER, None
                    )
                ),
                reproject=(
                    lambda bound_router=router, bound_hook=hook: (
                        reproject_workflow_hook(
                            bound_router, bound_hook, Scope.USER, None
                        )
                    )
                ),
            )
        )
        entries.append(_skill_entry(router, skill, agent.value, "skill"))
        entries.extend(
            _skill_entry(router, companion, agent.value, f"skill:{companion.name}")
            for companion in companions
        )
    return tuple(entries)


def generated_entries(
    generated: Sequence[tuple[Agent, Sequence[Skill]]],
    *,
    target: Path | None = None,
) -> tuple[LifecycleEntry, ...]:
    """Build entries for already-generated OpenSpec operation skills."""
    resolved = (target or Path.cwd()).resolve()
    entries: list[LifecycleEntry] = []
    for agent, skills in generated:
        router = agent_router(agent, resolved)
        entries.extend(
            _skill_entry(router, skill, agent.value, f"skill:{skill.name}")
            for skill in skills
        )
    return tuple(entries)


__all__ = [
    "SUPPORTED_AGENTS",
    "generated_entries",
    "packaged_entries",
]
