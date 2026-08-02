from dataclasses import replace
from pathlib import Path

import pytest

from zpp.utils.codespace_identity import (
    checkout_claim_key,
    checkout_path_claim_key,
    new_codespace_instance_id,
    projection_name,
    sibling_worktree_path,
    snapshot_key,
)
from zpp.utils.codespace_models import CodespaceMember
from zpp.utils.git_layers import GitCheckout


def test_codespace_identity_separates_snapshot_checkout_and_instance(
    tmp_path: Path,
) -> None:
    first = GitCheckout(tmp_path / "one", tmp_path / "one" / ".git", "aaa", False)
    second = GitCheckout(tmp_path / "two", tmp_path / "two" / ".git", "bbb", False)

    first_member = CodespaceMember(
        name="one",
        original_path=first.root,
        effective_path=first.root,
        checkout_key="one",
        commit=first.head,
        kind="project",
    )
    second_member = CodespaceMember(
        name="two",
        original_path=second.root,
        effective_path=second.root,
        checkout_key="two",
        commit=second.head,
        kind="project",
    )
    ordered = snapshot_key((first_member, second_member, first_member))
    reordered = snapshot_key((second_member, first_member, first_member))

    assert ordered == snapshot_key((first_member, second_member, first_member))
    assert ordered != reordered
    assert ordered != snapshot_key((first_member, second_member))
    assert checkout_claim_key(first) == checkout_claim_key(
        replace(first, head="changed", dirty=True)
    )
    assert checkout_path_claim_key(first.root / ".") == checkout_claim_key(first)
    assert new_codespace_instance_id(token="first") == (
        new_codespace_instance_id(token="first")
    )
    assert new_codespace_instance_id(token="first") != (
        new_codespace_instance_id(token="second")
    )
    instance = new_codespace_instance_id(token="first")
    assert sibling_worktree_path(first, instance) == (
        tmp_path / f"one-{instance}"
    )


def test_projection_name_requires_an_instance_and_positive_generation() -> None:
    assert projection_name("instance", 3) == "zpp-instance-g3"
    with pytest.raises(ValueError, match="instance"):
        projection_name("", 1)
    with pytest.raises(ValueError, match="generation"):
        projection_name("instance", 0)
