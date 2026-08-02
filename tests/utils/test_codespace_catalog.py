from pathlib import Path

import pytest

from zpp.utils.codespace_catalog import (
    plan_released_codespace_cleanup,
    record_codespace_cleanup,
    release_codespace_claim,
)
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    ReleasedCheckoutDebt,
    ReleasedCodespace,
)
from zpp.utils.git_layers import GitCheckout


def _claim(root: Path, instance: str) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key=f"snapshot-{instance}",
        members=(
            CodespaceMember(
                name="generated",
                original_path=root / "project",
                effective_path=root / f"project-{instance}",
                checkout_key=f"generated-{instance}",
                commit="abc",
                kind="project",
                generated_worktree=True,
                branch=f"zpp/{instance}/0",
            ),
            CodespaceMember(
                name="canonical",
                original_path=root / "canonical",
                effective_path=root / "canonical",
                checkout_key=f"canonical-{instance}",
                commit="def",
                kind="project",
            ),
        ),
    )


def test_release_is_atomic_and_retains_only_generated_debt(tmp_path: Path) -> None:
    first = _claim(tmp_path, "first")
    unrelated = _claim(tmp_path, "unrelated")
    older = ReleasedCodespace(
        instance_id="older",
        debts=(
            ReleasedCheckoutDebt(
                original_path=tmp_path / "old",
                effective_path=tmp_path / "old-generated",
                checkout_key="old-generated",
                branch="zpp/older/0",
            ),
        ),
    )
    index = CodespaceIndex(
        claims={"first": first, "unrelated": unrelated},
        released={"older": older},
    )

    updated, released = release_codespace_claim(index, "first")

    assert "first" not in updated.claims
    assert updated.claims["unrelated"] == unrelated
    assert updated.released["older"] == older
    assert released.instance_id == "first"
    assert [debt.checkout_key for debt in released.debts] == ["generated-first"]
    assert updated.released["first"] == released
    with pytest.raises(ValueError, match="does not exist"):
        release_codespace_claim(index, "missing")


def test_cleanup_recording_is_owned_additive_and_preserves_branch_metadata(
    tmp_path: Path,
) -> None:
    claim = _claim(tmp_path, "released")
    _, released = release_codespace_claim(
        CodespaceIndex(claims={"released": claim}),
        "released",
    )
    index = CodespaceIndex(released={"released": released})

    once = record_codespace_cleanup(index, "released", {"generated-released"})
    twice = record_codespace_cleanup(once, "released", {"generated-released"})

    assert once == twice
    debt = twice.released["released"].debts[0]
    assert debt.branch == "zpp/released/0"
    assert debt.worktree_removed
    with pytest.raises(ValueError, match="generated worktree"):
        record_codespace_cleanup(index, "released", {"canonical-released"})


def test_released_cleanup_plan_skips_removed_and_preserves_dirty_worktrees(
    tmp_path: Path,
) -> None:
    clean = ReleasedCheckoutDebt(
        original_path=tmp_path / "project",
        effective_path=tmp_path / "clean",
        checkout_key="clean",
        branch="zpp/released/0",
        worktree_removed=True,
    )
    dirty = clean.model_copy(
        update={
            "effective_path": tmp_path / "dirty",
            "checkout_key": "dirty",
            "branch": "zpp/released/1",
            "worktree_removed": False,
        }
    )
    released = ReleasedCodespace(instance_id="released", debts=(clean, dirty))

    plan = plan_released_codespace_cleanup(
        released,
        inspections={
            "dirty": GitCheckout(
                root=dirty.effective_path,
                common_dir=tmp_path / ".git",
                head="abc",
                dirty=True,
            )
        },
    )

    assert plan.removable == ()
    assert plan.preserved == (dirty,)
