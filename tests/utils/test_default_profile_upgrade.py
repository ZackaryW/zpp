from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

import pytest

from zpp.utils.default_profile_upgrade import (
    plan_default_profile_upgrade,
    plan_persistent_default_upgrade_mutation,
)
from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.models import AuthoredLayerFile, AuthoredLayerSnapshot, ManagedStateError


def trait(name: str, body: str) -> bytes:
    return (
        f"---\nname: {name}\ndescription: {name} guidance\n"
        "order: null\nconfig: {}\nskill_lookup: []\n---\n"
        f"{body}\n"
    ).encode()


def snapshot(
    *,
    config: bytes = b'{ "trait_overwrites": false, "traitsConfig": {} }\n',
    triggers: bytes = b'[{"trait":"automatic-workflow"}]\n',
    traits: dict[str, bytes] | None = None,
) -> AuthoredLayerSnapshot:
    files = [
        AuthoredLayerFile(PurePosixPath("config.json"), config),
        AuthoredLayerFile(PurePosixPath("trait.json"), triggers),
    ]
    files.extend(
        AuthoredLayerFile(PurePosixPath("traits", name + ".md"), content)
        for name, content in sorted((traits or {}).items())
    )
    return AuthoredLayerSnapshot(tuple(files))


def files(value: AuthoredLayerSnapshot) -> dict[str, bytes]:
    return {item.relative_path.as_posix(): item.content for item in value.files}


def write_snapshot(root: Path, value: AuthoredLayerSnapshot) -> None:
    for item in value.files:
        destination = root.joinpath(*item.relative_path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(item.content)


def test_absent_default_plans_the_complete_packaged_snapshot() -> None:
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    assert plan_default_profile_upgrade(None, packaged) == packaged


def test_complete_default_is_an_idempotent_noop() -> None:
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    assert plan_default_profile_upgrade(packaged, packaged) is None


def test_upgrade_adds_missing_traits_and_trigger_keys_but_preserves_authored_values() -> None:
    custom = trait("automatic-workflow", "user-owned custom body")
    existing = snapshot(
        triggers=b'[ { "trait": "automatic-workflow", "which": "custom" } ]\n',
        traits={"automatic-workflow": custom, "custom": trait("custom", "custom")},
    )
    packaged = snapshot(
        triggers=b'[{"trait":"automatic-workflow"},{"trait":"bdd-structure-python"}]\n',
        traits={
            "automatic-workflow": trait("automatic-workflow", "packaged"),
            "bdd-structure-python": trait("bdd-structure-python", "packaged bdd"),
        },
    )

    planned = plan_default_profile_upgrade(existing, packaged)

    assert planned is not None
    merged = files(planned)
    original = files(existing)
    assert merged["config.json"] == original["config.json"]
    assert merged["traits/automatic-workflow.md"] == custom
    assert merged["traits/custom.md"] == original["traits/custom.md"]
    assert "traits/bdd-structure-python.md" in merged
    triggers = json.loads(merged["trait.json"])
    assert triggers == [
        {"trait": "automatic-workflow", "which": "custom"},
        {"trait": "bdd-structure-python"},
    ]


def test_invalid_existing_snapshot_fails_before_a_plan_is_returned() -> None:
    existing = snapshot(config=b"not-json\n")
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    with pytest.raises(ManagedStateError, match="persistent default"):
        plan_default_profile_upgrade(existing, packaged)


def test_persistent_default_mutation_plans_an_absent_profile_without_writing(
    tmp_path: Path,
) -> None:
    root = tmp_path / ".zpp/profiles/default"
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    plan = plan_persistent_default_upgrade_mutation(root, packaged)

    assert plan is not None
    assert not root.exists()
    apply_mutation_plan(plan)
    assert (root / "config.json").read_bytes() == files(packaged)["config.json"]
    assert (root / "traits/automatic-workflow.md").is_file()


def test_persistent_default_mutation_is_none_for_a_complete_profile(
    tmp_path: Path,
) -> None:
    root = tmp_path / "default"
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})
    write_snapshot(root, packaged)

    assert plan_persistent_default_upgrade_mutation(root, packaged) is None


def test_persistent_default_mutation_adds_packaged_entries_and_preserves_custom_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "default"
    custom = trait("automatic-workflow", "custom body")
    existing = snapshot(
        triggers=b'[{"trait":"automatic-workflow","which":"custom"}]\n',
        traits={"automatic-workflow": custom},
    )
    packaged = snapshot(
        triggers=b'[{"trait":"automatic-workflow"},{"trait":"bdd-structure-python"}]\n',
        traits={
            "automatic-workflow": trait("automatic-workflow", "packaged"),
            "bdd-structure-python": trait("bdd-structure-python", "packaged"),
        },
    )
    write_snapshot(root, existing)

    plan = plan_persistent_default_upgrade_mutation(root, packaged)

    assert plan is not None
    assert plan.replacements == (root,)
    apply_mutation_plan(plan)
    assert (root / "traits/automatic-workflow.md").read_bytes() == custom
    assert (root / "traits/bdd-structure-python.md").is_file()
    assert json.loads((root / "trait.json").read_text(encoding="utf-8")) == [
        {"trait": "automatic-workflow", "which": "custom"},
        {"trait": "bdd-structure-python"},
    ]


def test_persistent_default_mutation_rejects_a_malformed_existing_profile(
    tmp_path: Path,
) -> None:
    root = tmp_path / "default"
    root.mkdir()
    (root / "config.json").write_text("not-json", encoding="utf-8")
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    with pytest.raises(ManagedStateError, match="invalid persistent default profile"):
        plan_persistent_default_upgrade_mutation(root, packaged)


def test_persistent_default_mutation_rejects_a_non_directory_parent(
    tmp_path: Path,
) -> None:
    blocked = tmp_path / ".zpp"
    blocked.write_text("file", encoding="utf-8")
    root = blocked / "profiles/default"
    packaged = snapshot(traits={"automatic-workflow": trait("automatic-workflow", "base")})

    with pytest.raises(ManagedStateError, match="parent is not a directory"):
        plan_persistent_default_upgrade_mutation(root, packaged)
