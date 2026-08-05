from __future__ import annotations

import json
from pathlib import PurePosixPath

import pytest

from zpp.utils.default_profile_upgrade import plan_default_profile_upgrade
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
