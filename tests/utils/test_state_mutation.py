from pathlib import Path

import pytest

from zpp.utils.models import CreationEntry, CreationPlan
from zpp.utils.state_mutation import apply_creation_plan


def test_creation_plan_rolls_back_only_entries_created_by_the_failed_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_parent = tmp_path / "existing"
    existing_parent.mkdir()
    created_root = existing_parent / "layer"
    first = created_root / "config.json"
    second = created_root / "trait.json"
    plan = CreationPlan(
        (
            CreationEntry(path=created_root, kind="directory"),
            CreationEntry(path=first, kind="text", source="{}\n"),
            CreationEntry(path=second, kind="text", source="[]\n"),
        )
    )

    real_write = __import__("zpp.utils.state_mutation", fromlist=["atomic_write_text"]).atomic_write_text

    def fail_second(destination: Path, source: str) -> None:
        if destination == second:
            raise PermissionError("blocked")
        real_write(destination, source)

    monkeypatch.setattr("zpp.utils.state_mutation.atomic_write_text", fail_second)

    with pytest.raises(PermissionError, match="blocked"):
        apply_creation_plan(plan)

    assert existing_parent.is_dir()
    assert not created_root.exists()
