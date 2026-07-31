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
    ReleasedCodespace,
)
from zpp.utils.git_layers import GitCheckout


def _claim(root: Path, instance: str) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key=f"snapshot-{instance}",
        workset_name=f"zpp-{instance}",
        members=(
            CodespaceMember(
                name="generated",
                original_path=root / "project",
                effective_path=root / f"project-{instance}",
                checkout_key="shared-checkout",
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


def test_released_catalog_loads_old_indexes_and_atomically_releases_claims(
    tmp_path: Path,
) -> None:
    old = CodespaceIndex.model_validate({"schema_version": 1, "claims": {}})
    first = _claim(tmp_path, "first")
    unrelated = _claim(tmp_path, "unrelated").model_copy(
        update={
            "members": tuple(
                member.model_copy(
                    update={"checkout_key": f"{member.checkout_key}-unrelated"}
                )
                for member in _claim(tmp_path, "unrelated").members
            )
        }
    )
    index = CodespaceIndex(
        claims={"first": first, "unrelated": unrelated},
        released={
            "older": ReleasedCodespace(
                claim=_claim(tmp_path, "older").model_copy(
                    update={
                        "members": tuple(
                            member.model_copy(
                                update={"checkout_key": f"{member.checkout_key}-older"}
                            )
                            for member in _claim(tmp_path, "older").members
                        )
                    }
                )
            )
        },
    )

    updated, released = release_codespace_claim(index, "first")

    assert old.released == {}
    assert "first" not in updated.claims
    assert updated.claims["unrelated"] == unrelated
    assert updated.released["older"] == index.released["older"]
    assert released.claim == first
    assert released.removed_worktree_keys == frozenset()
    assert updated.released["first"] == released
    assert CodespaceIndex(
        claims={"replacement": first.model_copy(update={"instance_id": "replacement"})},
        released=updated.released,
    )


def test_cleanup_recording_is_owned_additive_and_preserves_branch_metadata(
    tmp_path: Path,
) -> None:
    claim = _claim(tmp_path, "released")
    index = CodespaceIndex(
        released={"released": ReleasedCodespace(claim=claim)}
    )

    once = record_codespace_cleanup(index, "released", {"shared-checkout"})
    twice = record_codespace_cleanup(once, "released", {"shared-checkout"})

    assert once == twice
    assert twice.released["released"].claim.members[0].branch == "zpp/released/0"
    assert twice.released["released"].removed_worktree_keys == {
        "shared-checkout"
    }
    with pytest.raises(ValueError, match="generated worktree"):
        record_codespace_cleanup(index, "released", {"canonical-released"})
    with pytest.raises(ValueError, match="does not exist"):
        release_codespace_claim(index, "missing")


def test_released_cleanup_plan_skips_removed_and_preserves_dirty_worktrees(
    tmp_path: Path,
) -> None:
    claim = _claim(tmp_path, "released")
    dirty = claim.members[0].model_copy(
        update={
            "name": "dirty",
            "checkout_key": "dirty-key",
            "effective_path": tmp_path / "dirty",
            "branch": "zpp/released/1",
        }
    )
    claim = claim.model_copy(
        update={"members": (claim.members[0], dirty, claim.members[1])}
    )
    released = ReleasedCodespace(
        claim=claim,
        removed_worktree_keys={"shared-checkout"},
    )

    plan = plan_released_codespace_cleanup(
        released,
        inspections={
            "dirty-key": GitCheckout(
                root=dirty.effective_path,
                common_dir=tmp_path / ".git",
                head="abc",
                dirty=True,
            )
        },
    )

    assert plan.removable == ()
    assert plan.preserved == (dirty,)
