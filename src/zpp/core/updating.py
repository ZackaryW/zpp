from __future__ import annotations

from pathlib import Path

from zpp import __version__
from zpp.core.state import require_initialized_user_state
from zpp.utils.agent_bootstrap import (
    inspect_agent_integrations,
    plan_agent_integrations,
)
from zpp.utils.default_profile_upgrade import plan_persistent_default_upgrade_mutation
from zpp.utils.filesystem_mutation import (
    FilesystemMutationPlan,
    apply_mutation_plan,
    merge_mutation_plans,
)
from zpp.utils.models import AgentName, ManagedStateError
from zpp.utils.openspec_projections import (
    inspect_openspec_projection,
    plan_openspec_projection,
)
from zpp.utils.openspec_skills import (
    detect_openspec_version,
    generate_openspec_skill_bundles,
)
from zpp.utils.packaged_profiles import load_packaged_default_profile
from zpp.utils.skill_bundles import load_packaged_skill_bundle
from zpp.utils.skill_lifecycle import (
    mutation_plan_for_skill_lifecycle,
    plan_skill_update,
)
from zpp.utils.skill_projections import (
    inspect_skill_scopes,
    openspec_projection_roots,
    skill_projection_roots,
)


SUPPORTED_AGENTS: tuple[AgentName, ...] = ("pi", "codex", "claude")


def update_global_state(home: Path) -> tuple[AgentName, ...]:
    require_initialized_user_state(home)
    bundle = load_packaged_skill_bundle(__version__)
    default_plan = plan_persistent_default_upgrade_mutation(
        home / ".zpp" / "profiles" / "default",
        load_packaged_default_profile(),
    )

    workflow_projections = skill_projection_roots(
        home=home,
        target=None,
        scope="global",
        agents=SUPPORTED_AGENTS,
    )
    workflow_inspections = inspect_skill_scopes(workflow_projections, bundle)
    conflict = next(
        (item for item in workflow_inspections if item.state == "conflict"),
        None,
    )
    if conflict is not None:
        raise ManagedStateError(f"conflicting workflow skill projection: {conflict.root}")

    managed_workflows = tuple(
        item
        for item in workflow_inspections
        if item.state in {"compatible", "outdated"}
    )
    workflow_agents = tuple(
        agent
        for inspection in managed_workflows
        for agent in inspection.agents
    )

    hook_inspections = inspect_agent_integrations(home, SUPPORTED_AGENTS)
    hook_conflict = next(
        (item for item in hook_inspections if item.status == "conflict"),
        None,
    )
    if hook_conflict is not None:
        detail = f": {hook_conflict.reason}" if hook_conflict.reason else ""
        raise ManagedStateError(
            f"conflicting {hook_conflict.agent} integration at "
            f"{hook_conflict.destination}{detail}"
        )
    hook_agents = tuple(
        item.agent
        for item in hook_inspections
        if item.status in {"current", "refreshable"}
    )
    included_agents = tuple(
        agent
        for agent in SUPPORTED_AGENTS
        if agent in workflow_agents or agent in hook_agents
    )

    plans: list[FilesystemMutationPlan] = []
    if default_plan is not None:
        plans.append(default_plan)
    plans.append(
        mutation_plan_for_skill_lifecycle(
            bundle,
            plan_skill_update(bundle, managed_workflows),
        )
    )
    plans.append(plan_agent_integrations(home, included_agents))
    plans.extend(_plan_openspec_updates(home, workflow_agents))

    apply_mutation_plan(merge_mutation_plans(plans))
    return included_agents


def _plan_openspec_updates(
    home: Path,
    agents: tuple[AgentName, ...],
) -> tuple[FilesystemMutationPlan, ...]:
    if not agents:
        return ()
    detected_version = detect_openspec_version()
    projections = openspec_projection_roots(
        home=home,
        target=None,
        scope="global",
        agents=agents,
    )
    inspected = tuple(
        (
            projection,
            inspect_openspec_projection(
                projection.root,
                projection.agents[0],
                detected_version,
            ),
        )
        for projection in projections
    )
    conflict = next(
        (inspection for _, inspection in inspected if inspection.state == "conflict"),
        None,
    )
    if conflict is not None:
        raise ManagedStateError(f"conflicting OpenSpec skill projection: {conflict.root}")

    needed = tuple(
        projection.agents[0]
        for projection, inspection in inspected
        if inspection.state in {"absent", "outdated"}
    )
    if not needed:
        return ()
    generated = {
        item.agent: item
        for item in generate_openspec_skill_bundles(
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
