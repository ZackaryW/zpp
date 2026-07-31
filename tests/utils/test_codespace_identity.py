from dataclasses import replace
from pathlib import Path

from zpp.utils.codespace_identity import (
    checkout_claim_key,
    new_codespace_instance_id,
    sibling_worktree_path,
    snapshot_key,
)
from zpp.utils.git_layers import GitCheckout


def test_codespace_identity_separates_snapshot_checkout_and_instance(
    tmp_path: Path,
) -> None:
    first = GitCheckout(tmp_path / "one", tmp_path / "one" / ".git", "aaa", False)
    second = GitCheckout(tmp_path / "two", tmp_path / "two" / ".git", "bbb", False)

    ordered = snapshot_key((first, second, first))
    reordered = snapshot_key((second, first, first))

    assert ordered == snapshot_key((first, second, first))
    assert ordered != reordered
    assert ordered != snapshot_key((first, second))
    assert checkout_claim_key(first) == checkout_claim_key(
        replace(first, head="changed", dirty=True)
    )
    assert new_codespace_instance_id(ordered, token="first") == (
        new_codespace_instance_id(ordered, token="first")
    )
    assert new_codespace_instance_id(ordered, token="first") != (
        new_codespace_instance_id(ordered, token="second")
    )
    instance = new_codespace_instance_id(ordered, token="first")
    assert sibling_worktree_path(first, instance) == (
        tmp_path / f"one-{instance}"
    )
