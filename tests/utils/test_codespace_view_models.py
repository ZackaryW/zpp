from pathlib import Path

import pytest

from zpp.utils.codespace_identity import (
    new_codespace_instance_id,
    projection_structure_key,
    snapshot_key,
)
from zpp.utils.codespace_members import read_only_members, writable_members
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember
from zpp.utils.codespace_state import migrate_codespace_index


def _member(root: Path, *, access: str, commit: str = "abc") -> CodespaceMember:
    return CodespaceMember(
        name=root.name,
        original_path=root,
        effective_path=root,
        checkout_key=f"key-{root.name}",
        commit=commit,
        kind="project",
        access=access,
    )


def _claim(instance: str, members: tuple[CodespaceMember, ...]) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key=snapshot_key(members),
        members=members,
    )


def test_mixed_access_models_share_references_but_exclude_them_from_ownership(
    tmp_path: Path,
) -> None:
    shared = _member(tmp_path / "shared", access="read_only")
    first = _claim("first", (_member(tmp_path / "first", access="writable"), shared))
    second = _claim(
        "second",
        (_member(tmp_path / "second", access="writable"), shared),
    )

    index = CodespaceIndex(claims={"first": first, "second": second})

    assert writable_members(first.members) == (first.members[0],)
    assert read_only_members(first.members) == (shared,)
    assert index.claims["second"].members[-1] == shared

    conflicting = second.model_copy(
        update={"members": (second.members[0], shared.model_copy(update={"access": "writable"}))}
    )
    owner = first.model_copy(
        update={"members": (first.members[0], shared.model_copy(update={"access": "writable"}))}
    )
    with pytest.raises(ValueError, match="physical checkout"):
        CodespaceIndex(claims={"first": owner, "second": conflicting})


def test_version_two_state_migrates_every_historical_member_to_writable(
    tmp_path: Path,
) -> None:
    legacy = _member(tmp_path / "legacy", access="writable")
    payload = _claim("legacy", (legacy,)).model_dump(mode="json")
    payload["members"][0].pop("access")
    payload["members"][0]["role"] = "governing"

    migrated = migrate_codespace_index(
        {"schema_version": 2, "claims": {"legacy": payload}, "released": {}}
    )

    assert migrated.schema_version == 3
    assert migrated.claims["legacy"].members[0].access == "writable"
    assert "role" not in migrated.model_dump(mode="json")["claims"]["legacy"]["members"][0]


def test_identity_keys_include_access_and_effective_shape_but_not_later_state(
    tmp_path: Path,
) -> None:
    writable = _member(tmp_path / "project", access="writable", commit="one")
    reference = _member(tmp_path / "reference", access="read_only", commit="two")
    members = (writable, reference)

    assert new_codespace_instance_id(token="successor") == new_codespace_instance_id(
        token="successor"
    )
    assert snapshot_key(members) != snapshot_key(
        (writable, reference.model_copy(update={"access": "writable"}))
    )
    assert projection_structure_key(members) != projection_structure_key(
        (writable, reference.model_copy(update={"access": "writable"}))
    )
    assert projection_structure_key(members) == projection_structure_key(
        (writable.model_copy(update={"commit": "advanced"}), reference)
    )
