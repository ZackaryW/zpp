from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from zpp import __version__
from zpp.core.errors import ZppDomainError
from zpp.utils.git_layers import git_worktree_root
from zpp.utils.models import AgentName
from zpp.utils.paths import canonicalize_existing_directory
from zpp.utils.skill_bundles import SkillProjectionInspection, load_packaged_skill_bundle
from zpp.utils.skill_lifecycle import (
    SkillLifecycleActionKind,
    SkillVersionDifference,
    apply_skill_lifecycle,
    differing_managed_versions,
    plan_skill_install,
    plan_skill_remove,
    plan_skill_update,
)
from zpp.utils.skill_projections import inspect_skill_scopes, skill_projection_roots


SkillOperation = Literal["install", "update", "remove"]
SkillScope = Literal["local", "global"]


@dataclass(frozen=True, slots=True)
class SkillLifecycleReport:
    actions: tuple[SkillLifecycleActionKind, ...]
    differences: tuple[SkillVersionDifference, ...]
    coexisting_agents: tuple[tuple[str, ...], ...]


def manage_workflow_skills(
    *,
    home: Path,
    current_directory: Path,
    target: Path | None,
    scope: SkillScope,
    agents: Iterable[AgentName],
    operation: SkillOperation,
    force: bool = False,
) -> SkillLifecycleReport:
    bundle = load_packaged_skill_bundle(__version__)
    selected_agents = tuple(dict.fromkeys(agents))
    if not selected_agents:
        raise ZppDomainError("at least one agent must be selected")

    local_target = _local_target(target or current_directory) if scope == "local" else None
    selected_projections = skill_projection_roots(
        home=home,
        target=local_target,
        scope=scope,
        agents=selected_agents,
    )
    selected = inspect_skill_scopes(selected_projections, bundle)

    if scope == "local":
        global_projections = skill_projection_roots(
            home=home,
            target=None,
            scope="global",
            agents=selected_agents,
        )
        global_state = inspect_skill_scopes(global_projections, bundle)
        comparison_projections = (*global_projections, *selected_projections)
    else:
        global_state = ()
        local_comparison = _comparison_local_target(current_directory)
        local_projections = (
            skill_projection_roots(
                home=home,
                target=local_comparison,
                scope="local",
                agents=selected_agents,
            )
            if local_comparison is not None
            else ()
        )
        comparison_projections = (*selected_projections, *local_projections)

    if operation == "install":
        plan = plan_skill_install(bundle, selected, global_state, force=force)
    elif operation == "update":
        plan = plan_skill_update(bundle, selected)
    else:
        plan = plan_skill_remove(selected)
    apply_skill_lifecycle(bundle, plan)

    current = inspect_skill_scopes(comparison_projections, bundle)
    return SkillLifecycleReport(
        tuple(action.kind for action in plan.actions),
        differing_managed_versions(current),
        _coexisting_agents(current),
    )


def _local_target(target: Path) -> Path:
    try:
        canonical = canonicalize_existing_directory(target)
    except (FileNotFoundError, NotADirectoryError, OSError) as error:
        raise ZppDomainError(f"invalid local skill target: {target}") from error
    if git_worktree_root(canonical.resolved) is None:
        raise ZppDomainError(f"local skill target is outside a Git worktree: {target}")
    return canonical.resolved


def _comparison_local_target(current_directory: Path) -> Path | None:
    try:
        canonical = canonicalize_existing_directory(current_directory)
    except (FileNotFoundError, NotADirectoryError, OSError):
        return None
    return canonical.resolved if git_worktree_root(canonical.resolved) is not None else None


def _coexisting_agents(
    inspections: tuple[SkillProjectionInspection, ...],
) -> tuple[tuple[str, ...], ...]:
    managed = tuple(
        item for item in inspections if item.state in {"compatible", "outdated"}
    )
    global_items = tuple(item for item in managed if item.scope == "global")
    local_items = tuple(item for item in managed if item.scope == "local")
    result: list[tuple[str, ...]] = []
    for global_item in global_items:
        for local_item in local_items:
            shared = tuple(
                agent for agent in local_item.agents if agent in global_item.agents
            )
            if shared and shared not in result:
                result.append(shared)
    return tuple(result)
