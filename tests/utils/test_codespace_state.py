import json
from pathlib import Path

from filelock import Timeout
import pytest

from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    CodespaceProjection,
    ReleasedCodespace,
)
from zpp.utils.codespace_state import (
    codespace_index_lock,
    load_codespace_index,
    migrate_codespace_index,
    mutate_codespace_index,
)


def _claim(root: Path, instance_id: str = "实例") -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance_id,
        snapshot_key="snapshot",
        members=(
            CodespaceMember(
                name="项目",
                original_path=root,
                effective_path=root,
                checkout_key=f"key-{instance_id}",
                commit="abc",
                kind="project",
            ),
        ),
    )


def test_codespace_index_is_validated_utf8_atomic_state(tmp_path: Path) -> None:
    root = tmp_path / "codespaces"
    assert load_codespace_index(root) == CodespaceIndex()
    first = _claim(tmp_path / "项目")
    second = _claim(tmp_path / "two", "second")

    updated = mutate_codespace_index(
        root,
        lambda index: index.model_copy(
            update={"claims": {**index.claims, first.instance_id: first}}
        ),
    )
    updated = mutate_codespace_index(
        root,
        lambda index: index.model_copy(
            update={"claims": {**index.claims, second.instance_id: second}}
        ),
    )

    assert list(updated.claims) == ["实例", "second"]
    assert load_codespace_index(root) == updated
    assert "\\u" not in (root / "index.json").read_text(encoding="utf-8")

    (root / "index.json").write_text('{"schema_version":3}', encoding="utf-8")
    with pytest.raises(ValueError, match="invalid codespace index"):
        load_codespace_index(root)


def test_codespace_lock_contention_preserves_state_and_releases_on_error(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codespaces"
    root.mkdir()
    lock_path = root / "index.lock"
    (root / "index.json").write_text(
        json.dumps(CodespaceIndex().model_dump(mode="json")),
        encoding="utf-8",
    )

    with codespace_index_lock(lock_path):
        with pytest.raises(Timeout):
            mutate_codespace_index(
                root,
                lambda index: index.model_copy(
                    update={"claims": {"blocked": _claim(tmp_path, "blocked")}}
                ),
                timeout=0,
            )
    assert load_codespace_index(root) == CodespaceIndex()

    with pytest.raises(RuntimeError, match="stop"):
        with codespace_index_lock(lock_path):
            raise RuntimeError("stop")
    with codespace_index_lock(lock_path):
        pass


def test_codespace_index_rejects_duplicate_physical_checkout_claims(
    tmp_path: Path,
) -> None:
    first = _claim(tmp_path / "first", "first")
    duplicate = _claim(tmp_path / "second", "second")
    duplicate = duplicate.model_copy(
        update={
            "members": (
                duplicate.members[0].model_copy(
                    update={"checkout_key": first.members[0].checkout_key}
                ),
            )
        }
    )

    with pytest.raises(ValueError, match="physical checkout"):
        CodespaceIndex(claims={"first": first, "second": duplicate})


def test_codespace_index_allows_shared_sources_with_distinct_effective_checkouts(
    tmp_path: Path,
) -> None:
    first = _claim(tmp_path / "first", "first")
    isolated = _claim(tmp_path / "second", "second")
    isolated = isolated.model_copy(
        update={
            "members": (
                isolated.members[0].model_copy(
                    update={
                        "checkout_key": "isolated-effective",
                        "source_checkout_key": first.members[0].checkout_key,
                    }
                ),
            )
        }
    )

    index = CodespaceIndex(claims={"first": first, "second": isolated})

    assert index.claims["second"].members[0].source_checkout_key == (
        index.claims["first"].members[0].checkout_key
    )


def test_member_backward_loading_defaults_source_to_effective(tmp_path: Path) -> None:
    member = _claim(tmp_path, "legacy").members[0]
    payload = member.model_dump(mode="json")
    payload.pop("source_checkout_key", None)

    loaded = CodespaceMember.model_validate(payload)

    assert loaded.source_checkout_key == loaded.checkout_key


def test_version_one_index_migrates_claim_projection_and_generated_debt(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codespaces"
    root.mkdir()
    active = _claim(tmp_path / "项目", "active")
    generated = active.members[0].model_copy(
        update={
            "generated_worktree": True,
            "branch": "zpp/active/0",
            "effective_path": tmp_path / "项目-active",
            "checkout_key": "generated-key",
        }
    )
    payload = {
        "schema_version": 1,
        "claims": {
            "active": {
                **active.model_dump(mode="json"),
                "workset_name": "zpp-active",
                "workset_owned": True,
            },
        },
        "released": {
            "released": {
                "claim": {
                    **active.model_copy(
                        update={"instance_id": "released", "members": (generated,)}
                    ).model_dump(mode="json"),
                    "workset_name": "zpp-released",
                    "workset_owned": True,
                },
                "removed_worktree_keys": ["generated-key"],
            }
        },
    }
    (root / "index.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    migrated = load_codespace_index(root)

    assert migrated.schema_version == 2
    assert migrated.claims["active"].projection == CodespaceProjection(
        generation=1,
        structure_key=migrated.claims["active"].projection.structure_key,
    )
    assert migrated.claims["active"].snapshot_key == "snapshot"
    assert migrated.released["released"] == ReleasedCodespace.model_validate(
        {
            "instance_id": "released",
            "debts": [
                {
                    "original_path": str(generated.original_path),
                    "effective_path": str(generated.effective_path),
                    "checkout_key": "generated-key",
                    "branch": "zpp/active/0",
                    "worktree_removed": True,
                    "branch_disposition": "pending",
                }
            ],
        }
    )


def test_version_one_user_owned_workset_is_not_claimed_as_a_projection(
    tmp_path: Path,
) -> None:
    claim = _claim(tmp_path, "legacy")
    payload = claim.model_dump(mode="json")
    payload.update({"workset_name": "user-view", "workset_owned": False})

    migrated = migrate_codespace_index(
        {"schema_version": 1, "claims": {"legacy": payload}, "released": {}}
    )

    assert migrated.claims["legacy"].projection is None
