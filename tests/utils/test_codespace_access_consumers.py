from pathlib import Path

from zpp.utils.codespace_discovery import discover_codespace
from zpp.utils.codespace_environment import materialize_private_registry
from zpp.utils.codespace_guard import GuardRequest, evaluate_codespace_guard
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember


def _member(
    root: Path,
    key: str,
    *,
    access: str,
    kind: str = "project",
    store_id: str | None = None,
) -> CodespaceMember:
    return CodespaceMember(
        name=root.name,
        original_path=root,
        effective_path=root,
        checkout_key=key,
        commit=f"commit-{key}",
        kind=kind,
        store_id=store_id,
        access=access,
    )


def _claim(instance: str, *members: CodespaceMember) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key=f"snapshot-{instance}",
        members=members,
    )


def test_discovery_uses_only_writable_members_even_when_references_are_shared(
    tmp_path: Path,
) -> None:
    shared = _member(tmp_path / "shared", "shared", access="read_only")
    first = _claim(
        "first",
        _member(tmp_path / "first", "first", access="writable"),
        shared,
    )
    second = _claim(
        "second",
        _member(tmp_path / "second", "second", access="writable"),
        shared,
    )

    assert discover_codespace(tmp_path / "first" / "nested", claims=(first, second)) == "first"
    assert discover_codespace(tmp_path / "shared" / "nested", claims=(first, second)) is None


def test_private_registry_materializes_only_writable_store_members(
    tmp_path: Path,
    monkeypatch,
) -> None:
    writable = _member(
        tmp_path / "writable-store",
        "writable",
        access="writable",
        kind="store",
        store_id="writable",
    )
    reference = _member(
        tmp_path / "reference-store",
        "reference",
        access="read_only",
        kind="store",
        store_id="reference",
    )
    calls: list[str] = []
    monkeypatch.setattr(
        "zpp.utils.codespace_environment.register_private_store",
        lambda store_id, root, *, env: calls.append(store_id),
    )

    materialize_private_registry(
        _claim("current", writable, reference),
        environment={},
    )

    assert calls == ["writable"]


def test_associated_guard_blocks_its_read_only_member_before_other_claim_checks(
    tmp_path: Path,
) -> None:
    shared = _member(tmp_path / "shared", "shared", access="read_only")
    first_root = tmp_path / "first"
    first = _claim(
        "first",
        _member(first_root, "first", access="writable"),
        shared,
    )
    owner = _claim(
        "owner",
        _member(tmp_path / "shared", "shared", access="writable"),
    )
    request = GuardRequest(
        kind="direct_write",
        cwd=first_root,
        target_paths=(tmp_path / "shared" / "file.py",),
    )

    decision = evaluate_codespace_guard(
        request,
        CodespaceIndex(claims={"first": first, "owner": owner}),
        associated_codespace="first",
    )

    assert not decision.allowed
    assert decision.associated_codespace == "first"
    assert decision.owner_id is None
    assert decision.reason is not None and "read-only" in decision.reason
