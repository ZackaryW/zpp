from __future__ import annotations

from collections.abc import Collection
from typing import Literal, Mapping

from zpp.utils.codespace_models import (
    CodespaceIndex,
    ReleasedCheckoutDebt,
    ReleasedCodespace,
)
from zpp.utils.codespace_planning import CodespaceCleanupPlan
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
    debts: list[ReleasedCheckoutDebt] = []
    for member in claim.members:
        if not member.generated_worktree:
            continue
        if not member.branch:
            raise ValueError("generated worktree has no reconciliation branch")
        debts.append(
            ReleasedCheckoutDebt(
                original_path=member.original_path,
                effective_path=member.effective_path,
                checkout_key=member.checkout_key,
                branch=member.branch,
            )
        )
    released = ReleasedCodespace(instance_id=claim.instance_id, debts=tuple(debts))
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
    generated = {debt.checkout_key for debt in released.debts}
    requested = frozenset(removed_worktree_keys)
    if not requested <= generated:
        raise ValueError("cleanup key is not an owned generated worktree")
    updated_released = released.model_copy(
        update={
            "debts": tuple(
                debt.model_copy(update={"worktree_removed": True})
                if debt.checkout_key in requested
                else debt
                for debt in released.debts
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
    removable: list[ReleasedCheckoutDebt] = []
    preserved: list[ReleasedCheckoutDebt] = []
    for debt in released.debts:
        if debt.worktree_removed:
            continue
        inspection = inspections.get(debt.checkout_key)
        if inspection is not None and not inspection.dirty:
            removable.append(debt)
        else:
            preserved.append(debt)
    return CodespaceCleanupPlan(tuple(removable), tuple(preserved))


def record_branch_disposition(
    index: CodespaceIndex,
    instance_id: str,
    checkout_key: str,
    disposition: Literal["reconciled", "abandoned"],
) -> CodespaceIndex:
    if disposition not in {"reconciled", "abandoned"}:
        raise ValueError(f"invalid branch disposition: {disposition}")
    released = index.released.get(instance_id)
    if released is None:
        raise ValueError(f"released codespace does not exist: {instance_id}")
    if checkout_key not in {debt.checkout_key for debt in released.debts}:
        raise ValueError("branch disposition key is not released debt")
    updated = released.model_copy(
        update={
            "debts": tuple(
                debt.model_copy(update={"branch_disposition": disposition})
                if debt.checkout_key == checkout_key
                else debt
                for debt in released.debts
            )
        }
    )
    return CodespaceIndex(
        claims=index.claims,
        released={**index.released, instance_id: updated},
    )


def finalize_released_codespace(
    index: CodespaceIndex,
    instance_id: str,
) -> CodespaceIndex:
    released = index.released.get(instance_id)
    if released is None:
        raise ValueError(f"released codespace does not exist: {instance_id}")
    if any(not debt.worktree_removed for debt in released.debts):
        raise ValueError("released codespace has remaining worktrees")
    if any(debt.branch_disposition == "pending" for debt in released.debts):
        raise ValueError("released codespace has a pending branch disposition")
    return CodespaceIndex(
        claims=index.claims,
        released={
            key: value
            for key, value in index.released.items()
            if key != instance_id
        },
    )
