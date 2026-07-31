from pathlib import Path

from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember
from zpp.utils.codespace_planning import (
    CodespaceRequest,
    ResolvedMember,
    plan_codespace_add,
    plan_codespace_cleanup,
    plan_codespace_lock,
    plan_codespace_unlock,
)
from zpp.utils.git_layers import GitCheckout


def _resolved(
    root: Path,
    name: str,
    key: str,
    *,
    role: str = "governing",
    kind: str = "project",
) -> ResolvedMember:
    return ResolvedMember(
        name=name,
        checkout=GitCheckout(root, root / ".git", f"commit-{name}", False),
        checkout_key=key,
        kind=kind,
        role=role,
        store_id=name if kind == "store" else None,
    )


def _active(member: ResolvedMember, instance: str = "active") -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key="old",
        workset_name=f"zpp-{instance}",
        members=(
            CodespaceMember(
                name=member.name,
                original_path=member.checkout.root,
                effective_path=member.checkout.root,
                checkout_key=member.checkout_key,
                commit="older-commit",
                kind=member.kind,
                role=member.role,
                store_id=member.store_id,
            ),
        ),
    )


def test_lock_plan_claims_writable_members_and_mitigates_only_conflicts(
    tmp_path: Path,
) -> None:
    project_c = _resolved(tmp_path / "c", "c", "key-c")
    project_b = _resolved(tmp_path / "b", "b", "key-b")
    store = _resolved(tmp_path / "store", "store", "key-store", kind="store")
    store_reference = _resolved(
        tmp_path / "store",
        "store-ref",
        "key-store",
        kind="store",
        role="reference",
    )
    reference = _resolved(
        tmp_path / "reference",
        "reference",
        "key-reference",
        kind="store",
        role="reference",
    )
    request = CodespaceRequest(
        instance_id="new-instance",
        snapshot_key="snapshot",
        workset_name="zpp-new-instance",
        members=(project_c, project_b, store_reference, store, reference),
    )
    active = CodespaceIndex(
        claims={
            "active": CodespaceClaim(
                instance_id="active",
                snapshot_key="old",
                workset_name="zpp-active",
                members=(
                    _active(project_b).members[0],
                    _active(store).members[0],
                ),
            )
        }
    )

    plan = plan_codespace_lock(request, active)

    assert plan.conflicting_checkout_keys == ("key-b", "key-store")
    assert [member.name for member in plan.claim.members] == ["c", "b", "store-ref"]
    assert plan.claim.members[0].effective_path == project_c.checkout.root
    assert plan.claim.members[1].generated_worktree
    assert plan.claim.members[1].source_checkout_key == "key-b"
    assert plan.claim.members[1].checkout_key != "key-b"
    assert plan.claim.members[2].role == "governing"
    assert plan.claim.members[2].store_id == "store"
    assert "key-reference" not in {
        member.source_checkout_key for member in plan.claim.members
    }


def test_add_release_and_cleanup_plans_preserve_ownership_boundaries(
    tmp_path: Path,
) -> None:
    existing = _resolved(tmp_path / "existing", "existing", "key-existing")
    addition = _resolved(tmp_path / "addition", "addition", "key-addition")
    current = _active(existing, "current")
    competing = _active(addition, "competing")
    index = CodespaceIndex(claims={"current": current, "competing": competing})

    add = plan_codespace_add(current, (addition,), index)
    release = plan_codespace_unlock(current)
    user_owned = current.model_copy(update={"workset_owned": False})
    user_release = plan_codespace_unlock(user_owned, force=True)

    generated_clean = current.members[0].model_copy(
        update={"generated_worktree": True, "branch": "zpp/current/0"}
    )
    generated_dirty = generated_clean.model_copy(
        update={
            "name": "dirty",
            "checkout_key": "key-dirty",
            "effective_path": tmp_path / "dirty",
        }
    )
    canonical = generated_clean.model_copy(
        update={
            "name": "canonical",
            "checkout_key": "key-canonical",
            "generated_worktree": False,
        }
    )
    cleanup_claim = current.model_copy(
        update={"members": (generated_clean, generated_dirty, canonical)}
    )
    cleanup = plan_codespace_cleanup(
        cleanup_claim,
        inspections={
            generated_clean.checkout_key: GitCheckout(
                generated_clean.effective_path,
                tmp_path / ".git",
                "a",
                False,
            ),
            generated_dirty.checkout_key: GitCheckout(
                generated_dirty.effective_path,
                tmp_path / ".git",
                "b",
                True,
            ),
        },
    )

    assert add.conflicting_checkout_keys == ("key-addition",)
    assert add.superseded_workset_name == current.workset_name
    assert [member.name for member in add.replacement.members] == [
        "existing",
        "addition",
    ]
    assert add.replacement.workset_name != current.workset_name
    assert add.replacement.snapshot_key != current.snapshot_key
    added_member = add.replacement.members[-1]
    assert added_member.generated_worktree
    assert added_member.source_checkout_key == "key-addition"
    assert added_member.checkout_key != added_member.source_checkout_key
    assert current.members == _active(existing, "current").members
    assert release.workset_name == current.workset_name
    assert release.preserved_worktrees == ()
    assert user_release.workset_name is None and user_release.forced
    assert cleanup.removable == (generated_clean,)
    assert cleanup.preserved == (generated_dirty,)
