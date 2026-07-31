from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal, Mapping, Sequence

from zpp.utils.codespace_identity import sibling_worktree_path, snapshot_key
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember
from zpp.utils.git_layers import GitCheckout


@dataclass(frozen=True, slots=True)
class ResolvedMember:
    name: str
    checkout: GitCheckout
    checkout_key: str
    kind: Literal["project", "store"]
    role: Literal["governing", "reference"] = "governing"
    store_id: str | None = None


@dataclass(frozen=True, slots=True)
class CodespaceRequest:
    instance_id: str
    snapshot_key: str
    workset_name: str
    members: tuple[ResolvedMember, ...]


@dataclass(frozen=True, slots=True)
class CodespaceLockPlan:
    claim: CodespaceClaim
    conflicting_checkout_keys: tuple[str, ...]
    dirty_member_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CodespaceAddPlan:
    current: CodespaceClaim
    replacement: CodespaceClaim
    additions: tuple[ResolvedMember, ...]
    conflicting_checkout_keys: tuple[str, ...]
    superseded_workset_name: str | None


@dataclass(frozen=True, slots=True)
class CodespaceReleasePlan:
    instance_id: str
    workset_name: str | None
    preserved_worktrees: tuple[Path, ...]
    forced: bool


@dataclass(frozen=True, slots=True)
class CodespaceCleanupPlan:
    removable: tuple[CodespaceMember, ...]
    preserved: tuple[CodespaceMember, ...]


def _claimed_keys(index: CodespaceIndex, *, excluding: str | None = None) -> set[str]:
    return {
        member.checkout_key
        for claim in index.claims.values()
        if claim.instance_id != excluding
        for member in claim.members
    }


def _writable_members(
    members: Sequence[ResolvedMember],
) -> tuple[ResolvedMember, ...]:
    ordered: list[ResolvedMember] = []
    positions: dict[str, int] = {}
    for candidate in members:
        position = positions.get(candidate.checkout_key)
        if position is None:
            positions[candidate.checkout_key] = len(ordered)
            ordered.append(candidate)
            continue
        existing = ordered[position]
        if existing.role == "reference" and candidate.role == "governing":
            ordered[position] = replace(
                candidate,
                name=existing.name,
            )
    return tuple(member for member in ordered if member.role == "governing")


def plan_codespace_lock(
    request: CodespaceRequest,
    active: CodespaceIndex,
) -> CodespaceLockPlan:
    writable = _writable_members(request.members)
    claimed = _claimed_keys(active)
    conflicts = tuple(
        member.checkout_key for member in writable if member.checkout_key in claimed
    )
    conflict_set = set(conflicts)
    claim_members: list[CodespaceMember] = []
    dirty: list[str] = []
    for position, member in enumerate(writable):
        is_conflict = member.checkout_key in conflict_set
        if member.checkout.dirty:
            dirty.append(member.name)
        claim_members.append(
            CodespaceMember(
                name=member.name,
                original_path=member.checkout.root,
                effective_path=(
                    sibling_worktree_path(member.checkout, request.instance_id)
                    if is_conflict
                    else member.checkout.root
                ),
                checkout_key=member.checkout_key,
                commit=member.checkout.head,
                kind=member.kind,
                store_id=member.store_id,
                role="governing",
                generated_worktree=is_conflict,
                branch=(
                    f"zpp/{request.instance_id}/{position}" if is_conflict else None
                ),
            )
        )
    return CodespaceLockPlan(
        claim=CodespaceClaim(
            instance_id=request.instance_id,
            snapshot_key=request.snapshot_key,
            workset_name=request.workset_name,
            members=tuple(claim_members),
        ),
        conflicting_checkout_keys=conflicts,
        dirty_member_names=tuple(dirty),
    )


def plan_codespace_add(
    current: CodespaceClaim,
    additions: Sequence[ResolvedMember],
    active: CodespaceIndex,
) -> CodespaceAddPlan:
    claimed = _claimed_keys(active, excluding=current.instance_id)
    existing_keys = {member.checkout_key for member in current.members}
    writable = tuple(
        member
        for member in _writable_members(additions)
        if member.checkout_key not in existing_keys
    )
    conflicts = tuple(
        member.checkout_key for member in writable if member.checkout_key in claimed
    )
    conflict_set = set(conflicts)
    replacement_members = list(current.members)
    for offset, member in enumerate(writable, start=len(replacement_members)):
        is_conflict = member.checkout_key in conflict_set
        replacement_members.append(
            CodespaceMember(
                name=member.name,
                original_path=member.checkout.root,
                effective_path=(
                    sibling_worktree_path(member.checkout, current.instance_id)
                    if is_conflict
                    else member.checkout.root
                ),
                checkout_key=member.checkout_key,
                commit=member.checkout.head,
                kind=member.kind,
                store_id=member.store_id,
                role="governing",
                generated_worktree=is_conflict,
                branch=(
                    f"zpp/{current.instance_id}/{offset}" if is_conflict else None
                ),
            )
        )
    checkouts = tuple(
        GitCheckout(
            root=member.original_path,
            common_dir=member.original_path,
            head=member.commit,
            dirty=False,
        )
        for member in replacement_members
    )
    replacement_snapshot = snapshot_key(checkouts)
    replacement = CodespaceClaim(
        instance_id=current.instance_id,
        snapshot_key=replacement_snapshot,
        workset_name=f"{current.workset_name}-add-{replacement_snapshot[:8]}",
        members=tuple(replacement_members),
        workset_owned=True,
    )
    return CodespaceAddPlan(
        current=current,
        replacement=replacement,
        additions=writable,
        conflicting_checkout_keys=conflicts,
        superseded_workset_name=current.workset_name if current.workset_owned else None,
    )


def plan_codespace_unlock(
    claim: CodespaceClaim,
    *,
    force: bool = False,
) -> CodespaceReleasePlan:
    return CodespaceReleasePlan(
        instance_id=claim.instance_id,
        workset_name=claim.workset_name if claim.workset_owned else None,
        preserved_worktrees=tuple(
            member.effective_path
            for member in claim.members
            if member.generated_worktree
        ),
        forced=force,
    )


def plan_codespace_cleanup(
    claim: CodespaceClaim,
    inspections: Mapping[str, GitCheckout],
) -> CodespaceCleanupPlan:
    removable: list[CodespaceMember] = []
    preserved: list[CodespaceMember] = []
    for member in claim.members:
        if not member.generated_worktree:
            continue
        inspection = inspections.get(member.checkout_key)
        if inspection is not None and not inspection.dirty:
            removable.append(member)
        else:
            preserved.append(member)
    return CodespaceCleanupPlan(tuple(removable), tuple(preserved))
