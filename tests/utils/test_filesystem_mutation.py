from pathlib import Path

import pytest

from zpp.utils.filesystem_mutation import (
    FilesystemMutationPlan,
    apply_mutation_plan,
    merge_mutation_plans,
)
from zpp.utils.models import CreationEntry, CreationPlan


def test_mutation_plan_replaces_atomically_and_restores_after_late_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("old first", encoding="utf-8")
    second.write_text("old second", encoding="utf-8")
    plan = FilesystemMutationPlan(
        CreationPlan(
            (
                CreationEntry(first, "text", "new first"),
                CreationEntry(second, "text", "new second"),
            )
        ),
        (first, second),
    )

    from zpp.utils import state_mutation

    real_write = state_mutation.atomic_write_text

    def fail_second(path: Path, source: str) -> None:
        if path == second:
            raise PermissionError("late failure")
        real_write(path, source)

    monkeypatch.setattr(state_mutation, "atomic_write_text", fail_second)

    with pytest.raises(PermissionError, match="late failure"):
        apply_mutation_plan(plan)

    assert first.read_text(encoding="utf-8") == "old first"
    assert second.read_text(encoding="utf-8") == "old second"


def test_merge_mutation_plans_rejects_duplicate_creation_ownership(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "owned.txt"
    first = FilesystemMutationPlan(
        CreationPlan((CreationEntry(destination, "text", "first"),))
    )
    second = FilesystemMutationPlan(
        CreationPlan((CreationEntry(destination, "text", "second"),))
    )

    with pytest.raises(ValueError, match="duplicate"):
        merge_mutation_plans((first, second))


def test_merge_mutation_plans_coalesces_identical_shared_directories(
    tmp_path: Path,
) -> None:
    root = tmp_path / "shared"
    first_file = root / "zpp-skill" / "SKILL.md"
    second_file = root / "openspec-skill" / "SKILL.md"
    first = FilesystemMutationPlan(
        CreationPlan(
            (
                CreationEntry(root, "directory"),
                CreationEntry(first_file.parent, "directory"),
                CreationEntry(first_file, "text", "zpp"),
            )
        )
    )
    second = FilesystemMutationPlan(
        CreationPlan(
            (
                CreationEntry(root, "directory"),
                CreationEntry(second_file.parent, "directory"),
                CreationEntry(second_file, "text", "openspec"),
            )
        )
    )

    merged = merge_mutation_plans((first, second))
    apply_mutation_plan(merged)

    assert first_file.read_text(encoding="utf-8") == "zpp"
    assert second_file.read_text(encoding="utf-8") == "openspec"
    assert tuple(entry.path for entry in merged.creation.entries).count(root) == 1
