from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass

from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex


@dataclass(frozen=True, slots=True)
class CodespaceConflict:
    checkout_key: str
    owner_id: str


class CodespaceClaimConflictError(ValueError):
    def __init__(self, conflicts: tuple[CodespaceConflict, ...]) -> None:
        self.conflicts = conflicts
        owners = ", ".join(
            f"{conflict.checkout_key} ({conflict.owner_id})"
            for conflict in conflicts
        )
        super().__init__(f"physical checkouts are already claimed: {owners}")


def claimed_checkout_owners(
    index: CodespaceIndex,
    checkout_keys: Collection[str],
    *,
    excluding: str | None = None,
) -> tuple[CodespaceConflict, ...]:
    requested = set(checkout_keys)
    return tuple(
        CodespaceConflict(member.checkout_key, claim.instance_id)
        for claim in index.claims.values()
        if claim.instance_id != excluding
        for member in claim.members
        if member.checkout_key in requested
    )


def register_codespace_claim(
    index: CodespaceIndex,
    claim: CodespaceClaim,
) -> CodespaceIndex:
    if claim.instance_id in index.claims:
        raise ValueError(f"active codespace already exists: {claim.instance_id}")
    conflicts = claimed_checkout_owners(
        index,
        {member.checkout_key for member in claim.members},
    )
    if conflicts:
        raise CodespaceClaimConflictError(conflicts)
    return CodespaceIndex(
        claims={**index.claims, claim.instance_id: claim},
        released=index.released,
    )


def replace_codespace_claim(
    index: CodespaceIndex,
    expected: CodespaceClaim,
    replacement: CodespaceClaim,
) -> CodespaceIndex:
    if replacement.instance_id != expected.instance_id:
        raise ValueError("replacement changes the codespace instance id")
    current = index.claims.get(expected.instance_id)
    if current != expected:
        raise ValueError("codespace claim changed since planning")
    conflicts = claimed_checkout_owners(
        index,
        {member.checkout_key for member in replacement.members},
        excluding=expected.instance_id,
    )
    if conflicts:
        raise CodespaceClaimConflictError(conflicts)
    return CodespaceIndex(
        claims={**index.claims, replacement.instance_id: replacement},
        released=index.released,
    )
