from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterable

from zpp.utils.models import CreationPlan
from zpp.utils.removals import stage_removals
from zpp.utils.state_mutation import apply_creation_plan


@dataclass(frozen=True, slots=True)
class FilesystemMutationPlan:
    creation: CreationPlan
    replacements: tuple[Path, ...] = ()


def merge_mutation_plans(
    plans: Iterable[FilesystemMutationPlan],
) -> FilesystemMutationPlan:
    items = tuple(plans)
    entries = tuple(entry for plan in items for entry in plan.creation.entries)
    paths = tuple(entry.path for entry in entries)
    if len(set(paths)) != len(paths):
        raise ValueError("mutation plans contain duplicate creation ownership")

    replacements = tuple(path for plan in items for path in plan.replacements)
    if len(set(replacements)) != len(replacements):
        raise ValueError("mutation plans contain duplicate replacement ownership")
    for index, path in enumerate(replacements):
        if any(path in other.parents for other in replacements[index + 1 :]):
            raise ValueError("mutation plans contain nested replacement ownership")
        if any(other in path.parents for other in replacements[index + 1 :]):
            raise ValueError("mutation plans contain nested replacement ownership")
    return FilesystemMutationPlan(CreationPlan(entries), replacements)


def apply_mutation_plan(plan: FilesystemMutationPlan) -> None:
    staged = stage_removals(plan.replacements)
    try:
        apply_creation_plan(plan.creation)
    except BaseException:
        staged.restore()
        raise
    staged.commit()
