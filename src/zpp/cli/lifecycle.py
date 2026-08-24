"""Shared, scope-aware projection inventory and migration reconciliation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agent_router import Agent, Hook, Scope, Skill

from zpp.artifacts import (
    packaged_companion_skills,
    packaged_workflow_hook,
    packaged_workflow_skills,
)
from zpp.cli.shared import agent_router
from zpp.utils.agent_router import (
    inspect_migratable_workflow_hook,
    inspect_workflow_hook,
    inspect_workflow_skill,
    project_migratable_workflow_hook,
    project_workflow_hook,
    project_workflow_skill,
    remove_workflow_hook,
    remove_workflow_skill,
    reproject_workflow_hook,
    reproject_workflow_skill,
)
from zpp.utils.lifecycle import (
    InspectedEntry,
    LifecycleEntry,
    inspect_entries,
    select_projections,
)

SUPPORTED_AGENTS = (Agent.CODEX, Agent.CLAUDE, Agent.PI, Agent.KIMI)
OBSOLETE_WORKFLOW_SKILL_NAMES = (
    "zpp-workflow",
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-explore",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-update-change",
)


OWNED_OBSOLETE_STATES = frozenset({"current", "outdated"})
UNSAFE_OBSOLETE_STATES = frozenset({"conflict", "unmanaged", "inspection-failed"})


@dataclass(frozen=True, slots=True)
class InstallationInspection:
    """One agent's exact current and finite-obsolete observed states."""

    agent: Agent
    current: tuple[InspectedEntry, ...]
    obsolete: tuple[InspectedEntry, ...]
    scope: Scope = Scope.USER
    project_root: Path | None = None

    @property
    def classification(self) -> str:
        return classify_installation(
            tuple(item.status for item in self.current),
            tuple(item.status for item in self.obsolete),
        )


def classify_installation(
    current_statuses: Sequence[str], obsolete_statuses: Sequence[str]
) -> str:
    """Classify an exact current-plus-obsolete inventory without inference."""
    if any(status != "absent" for status in current_statuses):
        return "current"
    if any(status in UNSAFE_OBSOLETE_STATES for status in obsolete_statuses):
        return "obsolete-conflict"
    if any(status in OWNED_OBSOLETE_STATES for status in obsolete_statuses):
        return "old-only"
    return "absent"


def migration_result_status(
    *, current_verified: bool, surviving_obsolete: Sequence[str], conflicts: bool
) -> str:
    """Aggregate migration evidence into one truthful terminal status."""
    if conflicts:
        return "conflict"
    if not current_verified or surviving_obsolete:
        return "partial"
    return "complete"


def _skill_entry(
    router,
    skill: Skill,
    agent: str,
    kind: str,
    scope: Scope,
    project_root: Path | None,
    explicit_project_update: bool,
) -> LifecycleEntry:
    return LifecycleEntry(
        agent=agent,
        kind=kind,
        inspect=lambda: inspect_workflow_skill(router, skill, scope, project_root),
        project=lambda: project_workflow_skill(router, skill, scope, project_root),
        remove=lambda: remove_workflow_skill(router, skill.name, scope, project_root),
        reproject=(
            (
                lambda: project_workflow_skill(
                    router,
                    skill,
                    scope,
                    project_root,
                    replace_project=True,
                )
            )
            if explicit_project_update
            else (lambda: reproject_workflow_skill(router, skill, scope, project_root))
        ),
    )


def _hook_entry(
    router,
    hook: Hook,
    agent: str,
    scope: Scope,
    project_root: Path | None,
    migrate_former_hook: bool,
) -> LifecycleEntry:
    if not migrate_former_hook:
        return LifecycleEntry(
            agent=agent,
            kind="hook",
            inspect=lambda: inspect_workflow_hook(router, hook, scope, project_root),
            project=lambda: project_workflow_hook(router, hook, scope, project_root),
            remove=lambda: remove_workflow_hook(router, hook.name, scope, project_root),
            reproject=lambda: reproject_workflow_hook(
                router, hook, scope, project_root
            ),
        )

    def reproject():
        current = inspect_workflow_hook(router, hook, scope, project_root)
        if current.status == "current":
            return reproject_workflow_hook(router, hook, scope, project_root)
        return project_migratable_workflow_hook(router, hook, scope, project_root)

    return LifecycleEntry(
        agent=agent,
        kind="hook",
        inspect=lambda: inspect_migratable_workflow_hook(
            router, hook, scope, project_root
        ),
        project=lambda: project_migratable_workflow_hook(
            router, hook, scope, project_root
        ),
        remove=lambda: remove_workflow_hook(router, hook.name, scope, project_root),
        reproject=reproject,
    )


def packaged_entries(
    agents: Sequence[Agent] = SUPPORTED_AGENTS,
    *,
    target: Path | None = None,
    scope: Scope = Scope.USER,
    project_root: Path | None = None,
    include_companions: bool = True,
    explicit_project_update: bool = False,
    migrate_former_hooks: bool = False,
) -> tuple[LifecycleEntry, ...]:
    """Build the shared packaged workflow, hook, and companion inventory.

    These are inspectable without generating anything, so initialization can
    decide whether an agent is already installed without invoking OpenSpec.
    """
    resolved = (target or Path.cwd()).resolve()
    workflow_skills = packaged_workflow_skills()
    companions = packaged_companion_skills() if include_companions else ()
    entries: list[LifecycleEntry] = []
    for agent in agents:
        router = agent_router(agent, resolved)
        hook = packaged_workflow_hook(agent)
        entries.extend(
            _skill_entry(
                router,
                skill,
                agent.value,
                f"skill:{skill.name}",
                scope,
                project_root,
                explicit_project_update,
            )
            for skill in workflow_skills
        )
        entries.append(
            _hook_entry(
                router,
                hook,
                agent.value,
                scope,
                project_root,
                migrate_former_hooks,
            )
        )
        entries.extend(
            _skill_entry(
                router,
                companion,
                agent.value,
                f"skill:{companion.name}",
                scope,
                project_root,
                explicit_project_update,
            )
            for companion in companions
        )
    return tuple(entries)


def obsolete_entries(
    agents: Sequence[Agent] = SUPPORTED_AGENTS,
    *,
    target: Path | None = None,
    scope: Scope = Scope.USER,
    project_root: Path | None = None,
) -> tuple[LifecycleEntry, ...]:
    """Build removal-only entries for former ZPP-owned skill identities.

    The synthetic skills carry no files or executable behavior. Their only
    purpose is to ask Agent Router whether an obsolete native identity has
    ownership evidence before lifecycle code requests forced removal.
    """
    resolved = (target or Path.cwd()).resolve()
    entries: list[LifecycleEntry] = []
    compatible_agents = frozenset(SUPPORTED_AGENTS)
    for agent in agents:
        router = agent_router(agent, resolved)
        for name in OBSOLETE_WORKFLOW_SKILL_NAMES:
            tombstone = Skill(
                path=Path(),
                name=name,
                files=(),
                fingerprint=f"obsolete:{name}",
                compatible_agents=compatible_agents,
            )
            entries.append(
                LifecycleEntry(
                    agent=agent.value,
                    kind=f"obsolete-skill:{name}",
                    inspect=(
                        lambda bound_router=router, bound_skill=tombstone: (
                            inspect_workflow_skill(
                                bound_router, bound_skill, scope, project_root
                            )
                        )
                    ),
                    project=None,
                    remove=(
                        lambda bound_router=router, bound_name=name: (
                            remove_workflow_skill(
                                bound_router,
                                bound_name,
                                scope,
                                project_root,
                                force=True,
                            )
                        )
                    ),
                )
            )
    return tuple(entries)


def inspect_installations(
    agents: Sequence[Agent],
    *,
    target: Path,
    scope: Scope,
    project_root: Path | None,
    include_companions: bool,
    explicit_project_update: bool = False,
    migrate_former_hooks: bool = True,
) -> tuple[InstallationInspection, ...]:
    """Inspect current and exact obsolete entries once in the selected scope."""
    current = inspect_entries(
        packaged_entries(
            agents,
            target=target,
            scope=scope,
            project_root=project_root,
            include_companions=include_companions,
            explicit_project_update=explicit_project_update,
            migrate_former_hooks=migrate_former_hooks,
        )
    )
    obsolete = inspect_entries(
        obsolete_entries(
            agents,
            target=target,
            scope=scope,
            project_root=project_root,
        )
    )
    return tuple(
        InstallationInspection(
            agent,
            tuple(item for item in current if item.entry.agent == agent.value),
            tuple(item for item in obsolete if item.entry.agent == agent.value),
            scope,
            project_root,
        )
        for agent in agents
    )


def _apply_current(
    inspected: Sequence[InspectedEntry], *, force: bool, explicit_update: bool
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in select_projections(inspected, force=force):
        record = item.to_dict()
        operation = {
            "project": item.entry.project,
            "reproject": item.entry.reproject,
        }.get(item.decision)
        if (
            explicit_update
            and item.status in {"current", "outdated", "conflict"}
            and item.entry.reproject is not None
        ):
            record["decision"] = "update"
            operation = item.entry.reproject
        if operation is not None:
            try:
                record["status"] = operation().status
            except Exception as error:
                record["status"] = "projection-failed"
                record["error"] = str(error)
        records.append(record)
    return records


def _preserved_obsolete(
    inspected: Sequence[InspectedEntry], *, reason: str = "ownership-unsafe"
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in inspected:
        if item.status == "absent":
            continue
        record = item.to_dict()
        record["decision"] = "preserve"
        record["reason"] = reason
        records.append(record)
    return records


def _retire_owned_obsolete(
    inspected: Sequence[InspectedEntry],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in inspected:
        if item.status == "absent":
            continue
        if item.status not in OWNED_OBSOLETE_STATES:
            records.extend(_preserved_obsolete((item,)))
            continue
        record = item.to_dict()
        record["decision"] = "remove"
        try:
            record["status"] = item.entry.remove().status
        except Exception as error:
            record["status"] = "retirement-failed"
            record["decision"] = "preserve"
            record["error"] = str(error)
        records.append(record)
    return records


def reconcile_installations(
    inspections: Sequence[InstallationInspection],
    *,
    force: bool = False,
    absent: Literal["install", "skip"] = "skip",
    explicit_update: bool = False,
) -> list[dict[str, object]]:
    """Install and verify current entries before retiring owned tombstones."""
    records: list[dict[str, object]] = []
    for installation in inspections:
        classification = installation.classification
        migration_observed = tuple(
            item for item in installation.obsolete if item.status != "absent"
        )
        if classification == "absent" and absent == "skip":
            records.append(
                {
                    "agent": installation.agent.value,
                    "asset": "-",
                    "status": "uninitialized",
                    "decision": "skip",
                }
            )
            continue
        if classification == "obsolete-conflict":
            records.extend(_preserved_obsolete(installation.obsolete))
            records.append(
                _migration_record(
                    installation,
                    current=(),
                    surviving=migration_observed,
                    current_verified=False,
                    conflicts=True,
                )
            )
            continue

        records.extend(
            _apply_current(
                installation.current,
                force=force,
                explicit_update=explicit_update,
            )
        )
        verified = inspect_entries(tuple(item.entry for item in installation.current))
        current_verified = bool(verified) and all(
            item.status == "current" for item in verified
        )
        if not current_verified:
            records.extend(
                _preserved_obsolete(
                    installation.obsolete, reason="current-family-not-verified"
                )
            )
            if migration_observed:
                records.append(
                    _migration_record(
                        installation,
                        current=tuple(
                            item for item in verified if item.status == "current"
                        ),
                        surviving=migration_observed,
                        current_verified=False,
                        conflicts=False,
                    )
                )
            continue
        retirement = _retire_owned_obsolete(installation.obsolete)
        records.extend(retirement)
        if migration_observed:
            surviving = tuple(
                item
                for item in inspect_entries(
                    tuple(item.entry for item in migration_observed)
                )
                if item.status != "absent"
            )
            conflicts = any(item.status in UNSAFE_OBSOLETE_STATES for item in surviving)
            records.append(
                _migration_record(
                    installation,
                    current=verified,
                    surviving=surviving,
                    current_verified=True,
                    conflicts=conflicts,
                    failures=tuple(
                        str(record["asset"])
                        for record in retirement
                        if record.get("status") == "retirement-failed"
                    ),
                )
            )
    return records


def _migration_record(
    installation: InstallationInspection,
    *,
    current: Sequence[InspectedEntry],
    surviving: Sequence[InspectedEntry],
    current_verified: bool,
    conflicts: bool,
    failures: Sequence[str] = (),
) -> dict[str, object]:
    surviving_identities = [item.entry.kind for item in surviving]
    record: dict[str, object] = {
        "agent": installation.agent.value,
        "asset": "migration",
        "status": migration_result_status(
            current_verified=current_verified,
            surviving_obsolete=surviving_identities,
            conflicts=conflicts,
        ),
        "decision": "migrate",
        "origin": installation.classification,
        "current": [item.entry.kind for item in current],
        "surviving_obsolete": surviving_identities,
    }
    if failures:
        record["failures"] = list(failures)
    return record


def preflight_first_install(
    inspections: Sequence[InstallationInspection],
) -> dict[str, object] | None:
    """Return the first exact destination that blocks first installation."""
    for installation in inspections:
        for item in (*installation.current, *installation.obsolete):
            if item.status == "absent":
                continue
            if item.status in OWNED_OBSOLETE_STATES or (
                item in installation.current and item.status in {"current", "outdated"}
            ):
                reason = "already-installed; run `zpp workflow update`"
            else:
                reason = f"conflicting destination ({item.status})"
            observed = item.observed or {}
            return {
                "agent": installation.agent.value,
                "asset": item.entry.kind,
                "scope": observed.get("scope", "unknown"),
                "project_root": (
                    str(installation.project_root)
                    if installation.project_root is not None
                    else "-"
                ),
                "destination": observed.get("destination", "unknown"),
                "status": item.status,
                "reason": reason,
            }
    return None


__all__ = [
    "OBSOLETE_WORKFLOW_SKILL_NAMES",
    "SUPPORTED_AGENTS",
    "InstallationInspection",
    "classify_installation",
    "inspect_installations",
    "migration_result_status",
    "obsolete_entries",
    "packaged_entries",
    "preflight_first_install",
    "reconcile_installations",
]
