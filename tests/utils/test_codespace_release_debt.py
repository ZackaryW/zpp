from pathlib import Path

import pytest

from zpp.utils.codespace_catalog import (
    finalize_released_codespace,
    record_branch_disposition,
    record_codespace_cleanup,
    release_codespace_claim,
)
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember


def test_release_retains_only_generated_debt_and_requires_complete_disposition(
    tmp_path: Path,
) -> None:
    generated = CodespaceMember(
        name="generated",
        original_path=tmp_path / "project",
        effective_path=tmp_path / "project-instance",
        checkout_key="generated",
        commit="abc",
        kind="project",
        generated_worktree=True,
        branch="zpp/instance/0",
    )
    canonical = generated.model_copy(
        update={
            "name": "canonical",
            "effective_path": tmp_path / "canonical",
            "checkout_key": "canonical",
            "generated_worktree": False,
            "branch": None,
        }
    )
    claim = CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        members=(generated, canonical),
    )

    released_index, released = release_codespace_claim(
        CodespaceIndex(claims={"instance": claim}),
        "instance",
    )
    cleaned = record_codespace_cleanup(released_index, "instance", {"generated"})

    assert [debt.checkout_key for debt in released.debts] == ["generated"]
    with pytest.raises(ValueError, match="pending branch"):
        finalize_released_codespace(cleaned, "instance")

    disposed = record_branch_disposition(
        cleaned,
        "instance",
        "generated",
        "reconciled",
    )
    finalized = finalize_released_codespace(disposed, "instance")

    assert finalized.released == {}


def test_branch_disposition_rejects_unknown_states(tmp_path: Path) -> None:
    generated = CodespaceMember(
        name="generated",
        original_path=tmp_path / "project",
        effective_path=tmp_path / "project-instance",
        checkout_key="generated",
        commit="abc",
        kind="project",
        generated_worktree=True,
        branch="zpp/instance/0",
    )
    claim = CodespaceClaim(
        instance_id="instance",
        snapshot_key="snapshot",
        members=(generated,),
    )
    index, _ = release_codespace_claim(
        CodespaceIndex(claims={"instance": claim}),
        "instance",
    )

    with pytest.raises(ValueError, match="disposition"):
        record_branch_disposition(
            index,
            "instance",
            "generated",
            "forgotten",  # type: ignore[arg-type]
        )
