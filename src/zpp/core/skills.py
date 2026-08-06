from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from zpp import __version__
from zpp.core.errors import ZppDomainError
from zpp.utils.git_layers import git_worktree_root
from zpp.utils.agent_bootstrap import plan_agent_integrations
from zpp.utils.default_profile_upgrade import plan_persistent_default_upgrade_mutation
from zpp.utils.filesystem_mutation import (
    FilesystemMutationPlan,
    apply_mutation_plan,
    merge_mutation_plans,
)
from zpp.utils.models import AgentName, ManagedStateError
from zpp.utils.packaged_profiles import load_packaged_default_profile
from zpp.utils.openspec_projections import (
    OpenSpecProjectionInspection,
    inspect_openspec_projection,
    plan_openspec_projection,
)
from zpp.utils.openspec_skills import (
    detect_openspec_version,
    generate_openspec_skill_bundles,
)
from zpp.utils.paths import canonicalize_existing_directory
from zpp.utils.skill_bundles import SkillProjectionInspection, load_packaged_skill_bundle
from zpp.utils.skill_lifecycle import (
    SkillLifecycleActionKind,
    SkillVersionDifference,
    differing_managed_versions,
    mutation_plan_for_skill_lifecycle,
    plan_skill_install,
    plan_skill_remove,
    plan_skill_update,
)
from zpp.utils.skill_projections import (
    SkillProjection,
    inspect_skill_scopes,
    openspec_projection_roots,
    skill_projection_roots,
)


SkillOperation = Literal["install", "update", "remove"]
SkillScope = Literal["local", "global"]


@dataclass(frozen=True, slots=True)
class SkillLifecycleReport:
    actions: tuple[SkillLifecycleActionKind, ...]
    differences: tuple[SkillVersionDifference, ...]
    coexisting_agents: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class SelectedGlobalIntegrationPlan:
    mutation: FilesystemMutationPlan
    actions: tuple[SkillLifecycleActionKind, ...]


def plan_selected_global_integration(
    *,
    home: Path,
    agents: Iterable[AgentName],
    upgrade_default_profile: bool,
) -> SelectedGlobalIntegrationPlan:
    selected_agents = tuple(dict.fromkeys(agents))
    if not selected_agents:
        raise ZppDomainError("at least one agent must be selected")

    bundle = load_packaged_skill_bundle(__version__)
    selected = inspect_skill_scopes(
        skill_projection_roots(
            home=home,
            target=None,
            scope="global",
            agents=selected_agents,
        ),
        bundle,
    )
    lifecycle = plan_skill_install(bundle, selected, (), force=False)
    mutations = [
        mutation_plan_for_skill_lifecycle(bundle, lifecycle),
        plan_agent_integrations(home, selected_agents),
    ]
    if upgrade_default_profile:
        default_upgrade = plan_persistent_default_upgrade_mutation(
            home / ".zpp" / "profiles" / "default",
            load_packaged_default_profile(),
        )
        if default_upgrade is not None:
            mutations.append(default_upgrade)
    mutations.extend(
        _plan_openspec_mutations(
            home=home,
            target=None,
            scope="global",
            agents=selected_agents,
            operation="install",
            bootstrap_openspec=False,
        )
    )
    return SelectedGlobalIntegrationPlan(
        merge_mutation_plans(mutations),
        tuple(action.kind for action in lifecycle.actions),
    )


def manage_workflow_skills(
    *,
    home: Path,
    current_directory: Path,
    target: Path | None,
    scope: SkillScope,
    agents: Iterable[AgentName],
    operation: SkillOperation,
    force: bool = False,
    bootstrap_openspec: bool = False,
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

    if operation == "install" and scope == "global":
        global_install = plan_selected_global_integration(
            home=home,
            agents=selected_agents,
            upgrade_default_profile=True,
        )
        apply_mutation_plan(global_install.mutation)
        action_kinds = global_install.actions
    else:
        if operation == "install":
            plan = plan_skill_install(bundle, selected, global_state, force=force)
        elif operation == "update":
            plan = plan_skill_update(bundle, selected)
        else:
            plan = plan_skill_remove(selected)

        skill_mutation = mutation_plan_for_skill_lifecycle(bundle, plan)
        if operation == "remove":
            apply_mutation_plan(skill_mutation)
        else:
            mutations = [skill_mutation, plan_agent_integrations(home, selected_agents)]
            default_upgrade = (
                plan_persistent_default_upgrade_mutation(
                    home / ".zpp" / "profiles" / "default",
                    load_packaged_default_profile(),
                )
                if scope == "global"
                else None
            )
            if default_upgrade is not None:
                mutations.append(default_upgrade)
            mutations.extend(
                _plan_openspec_mutations(
                    home=home,
                    target=local_target,
                    scope=scope,
                    agents=selected_agents,
                    operation=operation,
                    bootstrap_openspec=bootstrap_openspec,
                )
            )
            apply_mutation_plan(merge_mutation_plans(mutations))
        action_kinds = tuple(action.kind for action in plan.actions)

    current = inspect_skill_scopes(comparison_projections, bundle)
    return SkillLifecycleReport(
        action_kinds,
        differing_managed_versions(current),
        _coexisting_agents(current),
    )

def _plan_openspec_mutations(
    *,
    home: Path,
    target: Path | None,
    scope: SkillScope,
    agents: tuple[AgentName, ...],
    operation: Literal["install", "update"],
    bootstrap_openspec: bool,
) -> tuple[FilesystemMutationPlan, ...]:
    if scope == "local" and operation == "install" and not bootstrap_openspec:
        return ()

    projections = openspec_projection_roots(
        home=home,
        target=target,
        scope=scope,
        agents=agents,
    )
    detected_version = detect_openspec_version()
    inspected: list[tuple[SkillProjection, OpenSpecProjectionInspection]] = []
    for projection in projections:
        agent = projection.agents[0]
        inspection = inspect_openspec_projection(
            projection.root,
            agent,
            detected_version,
        )
        if inspection.state == "conflict":
            raise ManagedStateError(
                f"conflicting OpenSpec skill projection: {projection.root}"
            )
        inspected.append((projection, inspection))

    needed = tuple(
        projection.agents[0]
        for projection, inspection in inspected
        if inspection.state == "outdated"
        or (inspection.state == "absent" and scope == "global")
        or (
            inspection.state == "absent"
            and scope == "local"
            and operation == "install"
            and bootstrap_openspec
        )
    )
    if not needed:
        return ()
    generated = {
        bundle.agent: bundle
        for bundle in generate_openspec_skill_bundles(
            needed,
            detected_version=detected_version,
        )
    }
    return tuple(
        plan_openspec_projection(
            projection.root,
            generated[projection.agents[0]],
            inspection,
        )
        for projection, inspection in inspected
        if projection.agents[0] in generated
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
