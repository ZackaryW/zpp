from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Literal

from zpp.utils.codespace_members import writable_members
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    ReleasedCodespace,
)


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


def find_matching_codespace_claim(
    index: CodespaceIndex,
    members: Collection[tuple[str, Literal["writable", "read_only"]]],
) -> CodespaceClaim | None:
    requested = set(members)
    return next(
        (
            claim
            for claim in index.claims.values()
            if {
                (member.source_checkout_key, member.access)
                for member in claim.members
            }
            == requested
        ),
        None,
    )


def update_codespace_claim(
    index: CodespaceIndex,
    expected: CodespaceClaim,
    replacement: CodespaceClaim,
) -> CodespaceIndex:
    if replacement.instance_id != expected.instance_id:
        raise ValueError("same-identity update changed the codespace identity")
    if index.claims.get(expected.instance_id) != expected:
        raise ValueError("codespace claim changed since planning")
    return CodespaceIndex(
        claims={**index.claims, replacement.instance_id: replacement},
        released=index.released,
    )


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
        for member in writable_members(claim.members)
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
        {member.checkout_key for member in writable_members(claim.members)},
    )
    if conflicts:
        raise CodespaceClaimConflictError(conflicts)
    return CodespaceIndex(
        claims={**index.claims, claim.instance_id: claim},
        released=index.released,
    )


def transition_codespace_claim(
    index: CodespaceIndex,
    expected: CodespaceClaim,
    successor: CodespaceClaim,
    released: ReleasedCodespace | None,
) -> CodespaceIndex:
    if successor.instance_id == expected.instance_id:
        raise ValueError("successor retains the superseded codespace identity")
    current = index.claims.get(expected.instance_id)
    if current != expected:
        raise ValueError("codespace claim changed since planning")
    if successor.instance_id in index.claims or successor.instance_id in index.released:
        raise ValueError("successor codespace identity already exists")
    if released is not None:
        if released.instance_id != expected.instance_id:
            raise ValueError("released debt does not belong to the superseded identity")
        if expected.instance_id in index.released:
            raise ValueError("superseded codespace debt already exists")
    conflicts = claimed_checkout_owners(
        index,
        {
            member.checkout_key
            for member in writable_members(successor.members)
        },
        excluding=expected.instance_id,
    )
    if conflicts:
        raise CodespaceClaimConflictError(conflicts)
    claims = {
        key: value
        for key, value in index.claims.items()
        if key != expected.instance_id
    }
    claims[successor.instance_id] = successor
    released_entries = dict(index.released)
    if released is not None:
        released_entries[released.instance_id] = released
    return CodespaceIndex(
        claims=claims,
        released=released_entries,
    )
