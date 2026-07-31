from __future__ import annotations

from collections.abc import Collection
from typing import Mapping

from zpp.utils.codespace_models import (
    CodespaceIndex,
    ReleasedCodespace,
)
from zpp.utils.codespace_planning import (
    CodespaceCleanupPlan,
    plan_codespace_cleanup,
)
from zpp.utils.git_layers import GitCheckout


def release_codespace_claim(
    index: CodespaceIndex,
    instance_id: str,
) -> tuple[CodespaceIndex, ReleasedCodespace]:
    claim = index.claims.get(instance_id)
    if claim is None:
        raise ValueError(f"active codespace does not exist: {instance_id}")
    if instance_id in index.released:
        raise ValueError(f"released codespace already exists: {instance_id}")
    released = ReleasedCodespace(claim=claim)
    updated = CodespaceIndex(
        claims={
            key: value
            for key, value in index.claims.items()
            if key != instance_id
        },
        released={**index.released, instance_id: released},
    )
    return updated, released


def record_codespace_cleanup(
    index: CodespaceIndex,
    instance_id: str,
    removed_worktree_keys: Collection[str],
) -> CodespaceIndex:
    released = index.released.get(instance_id)
    if released is None:
        raise ValueError(f"released codespace does not exist: {instance_id}")
    generated = {
        member.checkout_key
        for member in released.claim.members
        if member.generated_worktree
    }
    requested = frozenset(removed_worktree_keys)
    if not requested <= generated:
        raise ValueError("cleanup key is not an owned generated worktree")
    updated_released = released.model_copy(
        update={
            "removed_worktree_keys": (
                released.removed_worktree_keys | requested
            )
        }
    )
    return CodespaceIndex(
        claims=index.claims,
        released={**index.released, instance_id: updated_released},
    )


def plan_released_codespace_cleanup(
    released: ReleasedCodespace,
    inspections: Mapping[str, GitCheckout],
) -> CodespaceCleanupPlan:
    remaining = tuple(
        member
        for member in released.claim.members
        if member.checkout_key not in released.removed_worktree_keys
    )
    claim = released.claim.model_copy(update={"members": remaining})
    return plan_codespace_cleanup(claim, inspections)
