from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal

from zpp.utils.models import CreationEntry, CreationPlan, ManagedStateError
from zpp.utils.removals import stage_removals
from zpp.utils.skill_bundles import (
    SKILL_MANIFEST_NAME,
    SkillBundle,
    SkillProjectionInspection,
    manifest_for_bundle,
)
from zpp.utils.state_mutation import apply_creation_plan


SkillLifecycleActionKind = Literal[
    "install",
    "replace",
    "remove",
    "skip-current",
    "skip-global",
]


@dataclass(frozen=True, slots=True)
class SkillLifecycleAction:
    kind: SkillLifecycleActionKind
    inspection: SkillProjectionInspection


@dataclass(frozen=True, slots=True)
class SkillLifecyclePlan:
    actions: tuple[SkillLifecycleAction, ...]


@dataclass(frozen=True, slots=True)
class SkillVersionDifference:
    agents: tuple[str, ...]
    global_root: Path
    global_version: str
    local_root: Path
    local_version: str


def plan_skill_install(
    bundle: SkillBundle,
    selected: Iterable[SkillProjectionInspection],
    global_state: Iterable[SkillProjectionInspection],
    *,
    force: bool,
) -> SkillLifecyclePlan:
    del bundle
    selected_items = tuple(selected)
    global_items = tuple(global_state)
    _reject_conflicts(selected_items)

    actions: list[SkillLifecycleAction] = []
    for inspection in selected_items:
        if inspection.state == "compatible":
            kind: SkillLifecycleActionKind = "skip-current"
        elif inspection.state == "outdated":
            kind = "replace"
        elif (
            inspection.scope == "local"
            and not force
            and _has_compatible_global(inspection, global_items)
        ):
            kind = "skip-global"
        else:
            kind = "install"
        actions.append(SkillLifecycleAction(kind, inspection))
    return SkillLifecyclePlan(tuple(actions))


def plan_skill_update(
    bundle: SkillBundle,
    selected: Iterable[SkillProjectionInspection],
) -> SkillLifecyclePlan:
    del bundle
    selected_items = tuple(selected)
    _require_managed(selected_items, "update")
    return SkillLifecyclePlan(
        tuple(
            SkillLifecycleAction(
                "skip-current" if inspection.state == "compatible" else "replace",
                inspection,
            )
            for inspection in selected_items
        )
    )


def plan_skill_remove(
    selected: Iterable[SkillProjectionInspection],
) -> SkillLifecyclePlan:
    selected_items = tuple(selected)
    _require_managed(selected_items, "remove")
    return SkillLifecyclePlan(
        tuple(SkillLifecycleAction("remove", inspection) for inspection in selected_items)
    )


def differing_managed_versions(
    inspections: Iterable[SkillProjectionInspection],
) -> tuple[SkillVersionDifference, ...]:
    items = tuple(
        inspection
        for inspection in inspections
        if inspection.state in {"compatible", "outdated"}
        and inspection.version is not None
    )
    global_items = tuple(item for item in items if item.scope == "global")
    local_items = tuple(item for item in items if item.scope == "local")
    differences: list[SkillVersionDifference] = []
    for global_item in global_items:
        for local_item in local_items:
            shared = tuple(
                agent for agent in local_item.agents if agent in global_item.agents
            )
            if not shared or global_item.version == local_item.version:
                continue
            assert global_item.version is not None and local_item.version is not None
            differences.append(
                SkillVersionDifference(
                    shared,
                    global_item.root,
                    global_item.version,
                    local_item.root,
                    local_item.version,
                )
            )
    return tuple(differences)


def creation_plan_for_skill_lifecycle(
    bundle: SkillBundle,
    plan: SkillLifecyclePlan,
) -> CreationPlan:
    write_roots = tuple(
        action.inspection.root
        for action in plan.actions
        if action.kind in {"install", "replace"}
    )
    directories: set[Path] = set()
    entries: list[CreationEntry] = []
    for root in write_roots:
        directories.update(_missing_directories(root))
        for file in bundle.files:
            destination = root.joinpath(*file.relative_path.split("/"))
            cursor = destination.parent
            while cursor != root.parent and cursor != root:
                directories.add(cursor)
                cursor = cursor.parent
            directories.add(root / file.relative_path.split("/", 1)[0])

    entries.extend(
        CreationEntry(path, "directory")
        for path in sorted(directories, key=lambda item: (len(item.parts), str(item)))
    )
    for root in write_roots:
        entries.extend(
            CreationEntry(
                root.joinpath(*file.relative_path.split("/")),
                "binary",
                file.content,
            )
            for file in bundle.files
        )
        manifest = manifest_for_bundle(bundle)
        source = json.dumps(
            manifest.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        entries.append(CreationEntry(root / SKILL_MANIFEST_NAME, "text", source))
    return CreationPlan(tuple(entries))


def apply_skill_lifecycle(
    bundle: SkillBundle,
    plan: SkillLifecyclePlan,
) -> None:
    creation = creation_plan_for_skill_lifecycle(bundle, plan)
    removal_paths: list[Path] = []
    for action in plan.actions:
        if action.kind not in {"replace", "remove"}:
            continue
        manifest = action.inspection.manifest
        if manifest is None:
            raise ManagedStateError(
                f"managed skill projection has no ownership manifest: {action.inspection.root}"
            )
        owned_names = tuple(dict.fromkeys(path.split("/", 1)[0] for path in manifest.files))
        removal_paths.extend(action.inspection.root / name for name in owned_names)
        removal_paths.append(action.inspection.root / SKILL_MANIFEST_NAME)

    staged = stage_removals(removal_paths)
    try:
        apply_creation_plan(creation)
    except BaseException:
        staged.restore()
        raise
    staged.commit()


def _reject_conflicts(inspections: tuple[SkillProjectionInspection, ...]) -> None:
    conflicts = tuple(item for item in inspections if item.state == "conflict")
    if conflicts:
        raise ManagedStateError(f"conflicting skill projection: {conflicts[0].root}")


def _require_managed(
    inspections: tuple[SkillProjectionInspection, ...],
    operation: str,
) -> None:
    invalid = tuple(
        item for item in inspections if item.state not in {"compatible", "outdated"}
    )
    if invalid:
        raise ManagedStateError(
            f"cannot {operation} unmanaged skill projection: {invalid[0].root}"
        )


def _has_compatible_global(
    selected: SkillProjectionInspection,
    global_state: tuple[SkillProjectionInspection, ...],
) -> bool:
    return any(
        candidate.scope == "global"
        and candidate.state == "compatible"
        and any(agent in candidate.agents for agent in selected.agents)
        for candidate in global_state
    )


def _missing_directories(root: Path) -> tuple[Path, ...]:
    missing: list[Path] = []
    cursor = root
    while not cursor.exists() and not cursor.is_symlink():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor.is_symlink() or not cursor.is_dir():
        raise ManagedStateError(f"skill projection parent is not a directory: {cursor}")
    return tuple(reversed(missing))
