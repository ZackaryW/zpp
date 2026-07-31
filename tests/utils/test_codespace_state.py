import json
from pathlib import Path

from filelock import Timeout
import pytest

from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember
from zpp.utils.codespace_state import (
    codespace_index_lock,
    load_codespace_index,
    mutate_codespace_index,
)


def _claim(root: Path, instance_id: str = "实例") -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance_id,
        snapshot_key="snapshot",
        workset_name=f"zpp-{instance_id}",
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

    (root / "index.json").write_text('{"schema_version":2}', encoding="utf-8")
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
