from pathlib import Path

from zpp.utils.codespace_identity import projection_structure_key
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    CodespaceProjection,
)
from zpp.utils.codespace_planning import (
    CodespaceRequest,
    ResolvedMember,
    plan_codespace_cleanup,
    plan_codespace_lock,
    plan_codespace_projection,
    plan_codespace_unlock,
)
from zpp.utils.git_layers import GitCheckout


def _resolved(
    root: Path,
    name: str,
    key: str,
    *,
    access: str = "writable",
    kind: str = "project",
) -> ResolvedMember:
    return ResolvedMember(
        name=name,
        checkout=GitCheckout(root, root / ".git", f"commit-{name}", False),
        checkout_key=key,
        kind=kind,
        access=access,
        store_id=name if kind == "store" else None,
    )


def _active(member: ResolvedMember, instance: str = "active") -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key="old",
        members=(
            CodespaceMember(
                name=member.name,
                original_path=member.checkout.root,
                effective_path=member.checkout.root,
                checkout_key=member.checkout_key,
                commit="older-commit",
                kind=member.kind,
                access=member.access,
                store_id=member.store_id,
            ),
        ),
    )


def test_lock_plan_claims_writable_members_and_retains_shared_references(
    tmp_path: Path,
) -> None:
    project = _resolved(tmp_path / "project", "project", "key-project")
    conflict = _resolved(tmp_path / "conflict", "conflict", "key-conflict")
    reference = _resolved(
        tmp_path / "reference",
        "reference",
        "key-reference",
        access="read_only",
    )
    active = CodespaceIndex(
        claims={"active": _active(conflict)}
    )

    plan = plan_codespace_lock(
        CodespaceRequest("successor", (project, conflict, reference)),
        active,
    )

    assert plan.conflicting_checkout_keys == ("key-conflict",)
    assert [member.access for member in plan.claim.members] == [
        "writable",
        "writable",
        "read_only",
    ]
    assert plan.claim.members[1].generated_worktree
    assert not plan.claim.members[2].generated_worktree
    assert plan.claim.snapshot_key != "old"


def test_release_cleanup_and_projection_plans_preserve_boundaries(
    tmp_path: Path,
) -> None:
    current = _active(_resolved(tmp_path / "current", "current", "key-current"), "current")
    projected = current.model_copy(
        update={
            "projection": CodespaceProjection(
                generation=1,
                structure_key=projection_structure_key(current.members),
            )
        }
    )
    release = plan_codespace_unlock(projected)
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
    cleanup_claim = current.model_copy(
        update={"members": (generated_clean, generated_dirty)}
    )
    cleanup = plan_codespace_cleanup(
        cleanup_claim,
        inspections={
            generated_clean.checkout_key: GitCheckout(
                generated_clean.effective_path, tmp_path / ".git", "a", False
            ),
            generated_dirty.checkout_key: GitCheckout(
                generated_dirty.effective_path, tmp_path / ".git", "b", True
            ),
        },
    )

    assert release.projection_name == "zpp-current-g1"
    assert cleanup.removable == (generated_clean,)
    assert cleanup.preserved == (generated_dirty,)


def test_projection_plan_uses_access_and_paths_but_ignores_commit_movement(
    tmp_path: Path,
) -> None:
    claim = _active(_resolved(tmp_path / "project", "project", "key"), "instance")
    created = plan_codespace_projection(claim)
    projected = claim.model_copy(update={"projection": created.projection})
    moved_commit = projected.model_copy(
        update={
            "members": (
                projected.members[0].model_copy(update={"commit": "new-commit"}),
            )
        }
    )
    changed_access = projected.model_copy(
        update={
            "members": (
                projected.members[0].model_copy(update={"access": "read_only"}),
            )
        }
    )

    assert plan_codespace_projection(projected).action == "reuse"
    assert plan_codespace_projection(moved_commit).action == "reuse"
    assert plan_codespace_projection(changed_access).action == "replace"
