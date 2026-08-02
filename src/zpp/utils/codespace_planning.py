from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, Sequence

from zpp.utils.codespace_edits import CodespaceEditOperations
from zpp.utils.codespace_identity import (
    checkout_path_claim_key,
    projection_name,
    projection_structure_key,
    sibling_worktree_path,
    snapshot_key,
)
from zpp.utils.codespace_members import writable_members
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    CodespaceProjection,
    ReleasedCheckoutDebt,
    ReleasedCodespace,
)
from zpp.utils.git_layers import GitCheckout


@dataclass(frozen=True, slots=True)
class ResolvedMember:
    name: str
    checkout: GitCheckout
    checkout_key: str
    kind: Literal["project", "store"]
    access: Literal["writable", "read_only"] = "writable"
    store_id: str | None = None


@dataclass(frozen=True, slots=True)
class CodespaceRequest:
    instance_id: str
    members: tuple[ResolvedMember, ...]


@dataclass(frozen=True, slots=True)
class CodespaceLockPlan:
    claim: CodespaceClaim
    conflicting_checkout_keys: tuple[str, ...]
    dirty_member_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CodespaceEditPlan:
    current: CodespaceClaim
    successor: CodespaceClaim | None
    conflicting_checkout_keys: tuple[str, ...]
    dirty_member_names: tuple[str, ...]
    released: ReleasedCodespace | None
    no_op: bool


@dataclass(frozen=True, slots=True)
class CodespaceProjectionPlan:
    action: Literal["create", "reuse", "replace"]
    projection: CodespaceProjection
    superseded_name: str | None = None


@dataclass(frozen=True, slots=True)
class CodespaceReleasePlan:
    instance_id: str
    projection_name: str | None
    preserved_worktrees: tuple[Path, ...]
    forced: bool


@dataclass(frozen=True, slots=True)
class CodespaceCleanupPlan:
    removable: tuple[CodespaceMember | ReleasedCheckoutDebt, ...]
    preserved: tuple[CodespaceMember | ReleasedCheckoutDebt, ...]


def _claimed_keys(index: CodespaceIndex, *, excluding: str | None = None) -> set[str]:
    return {
        member.checkout_key
        for claim in index.claims.values()
        if claim.instance_id != excluding
        for member in writable_members(claim.members)
    }


def _deduplicate_resolved(
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
        if ordered[position].access == "read_only" and candidate.access == "writable":
            ordered[position] = candidate
    return tuple(ordered)


def _planned_member(
    member: ResolvedMember,
    *,
    instance_id: str,
    position: int,
    conflict: bool,
) -> CodespaceMember:
    generated = conflict and member.access == "writable"
    effective_path = (
        sibling_worktree_path(member.checkout, instance_id)
        if generated
        else member.checkout.root
    )
    return CodespaceMember(
        name=member.name,
        original_path=member.checkout.root,
        effective_path=effective_path,
        checkout_key=(
            checkout_path_claim_key(effective_path)
            if generated
            else member.checkout_key
        ),
        source_checkout_key=member.checkout_key,
        commit=member.checkout.head,
        kind=member.kind,
        store_id=member.store_id,
        access=member.access,
        generated_worktree=generated,
        branch=(f"zpp/{instance_id}/{position}" if generated else None),
    )


def _claim(
    *,
    instance_id: str,
    members: Sequence[CodespaceMember],
    projection: CodespaceProjection | None = None,
) -> CodespaceClaim:
    finalized = tuple(members)
    return CodespaceClaim(
        instance_id=instance_id,
        snapshot_key=snapshot_key(finalized),
        members=finalized,
        projection=projection,
    )


def plan_codespace_lock(
    request: CodespaceRequest,
    active: CodespaceIndex,
) -> CodespaceLockPlan:
    members = _deduplicate_resolved(request.members)
    claimed = _claimed_keys(active)
    conflicts = tuple(
        member.checkout_key
        for member in members
        if member.access == "writable" and member.checkout_key in claimed
    )
    conflict_set = set(conflicts)
    planned = tuple(
        _planned_member(
            member,
            instance_id=request.instance_id,
            position=position,
            conflict=member.checkout_key in conflict_set,
        )
        for position, member in enumerate(members)
    )
    return CodespaceLockPlan(
        claim=_claim(instance_id=request.instance_id, members=planned),
        conflicting_checkout_keys=conflicts,
        dirty_member_names=tuple(
            member.name for member in members if member.checkout.dirty
        ),
    )


def released_edit_debt(
    current: CodespaceClaim,
    successor: CodespaceClaim,
) -> ReleasedCodespace | None:
    retained = {member.checkout_key for member in successor.members}
    debts = tuple(
        ReleasedCheckoutDebt(
            original_path=member.original_path,
            effective_path=member.effective_path,
            checkout_key=member.checkout_key,
            branch=member.branch or "",
        )
        for member in current.members
        if member.generated_worktree and member.checkout_key not in retained
    )
    if not debts:
        return None
    return ReleasedCodespace(instance_id=current.instance_id, debts=debts)


def plan_codespace_edit(
    current: CodespaceClaim,
    operations: CodespaceEditOperations,
    resolved: Sequence[ResolvedMember],
    active: CodespaceIndex,
    *,
    successor_id: str,
) -> CodespaceEditPlan:
    if not operations.targets:
        return CodespaceEditPlan(current, None, (), (), None, True)

    remove_keys = operations.keys("remove")
    promote_keys = operations.keys("promote")
    demote_keys = operations.keys("demote")
    current_by_source = {member.source_checkout_key: member for member in current.members}
    for key in remove_keys | promote_keys | demote_keys:
        if key not in current_by_source:
            raise ValueError("edit target is not a current codespace member")
    if any(current_by_source[key].access != "read_only" for key in promote_keys):
        raise ValueError("only a read-only member can be promoted")
    if any(current_by_source[key].access != "writable" for key in demote_keys):
        raise ValueError("only a writable member can be demoted")

    replaced_keys = remove_keys | promote_keys | demote_keys
    members = [
        member for member in current.members if member.source_checkout_key not in replaced_keys
    ]
    targets_by_key = {target.checkout_key: target for target in operations.targets}
    for key in demote_keys:
        existing = current_by_source[key]
        checkout = targets_by_key[key].checkout
        members.append(
            CodespaceMember(
                name=existing.name,
                original_path=checkout.root,
                effective_path=checkout.root,
                checkout_key=key,
                source_checkout_key=key,
                commit=checkout.head,
                kind=existing.kind,
                store_id=existing.store_id,
                access="read_only",
            )
        )

    existing_sources = {member.source_checkout_key for member in members}
    candidates = tuple(
        member
        for member in _deduplicate_resolved(resolved)
        if member.checkout_key not in existing_sources
    )
    claimed = _claimed_keys(active, excluding=current.instance_id)
    conflicts = tuple(
        member.checkout_key
        for member in candidates
        if member.access == "writable" and member.checkout_key in claimed
    )
    conflict_set = set(conflicts)
    for offset, member in enumerate(candidates, start=len(members)):
        members.append(
            _planned_member(
                member,
                instance_id=successor_id,
                position=offset,
                conflict=member.checkout_key in conflict_set,
            )
        )

    logical_current = tuple(
        (member.source_checkout_key, member.access) for member in current.members
    )
    logical_successor = tuple(
        (member.source_checkout_key, member.access) for member in members
    )
    if logical_successor == logical_current:
        return CodespaceEditPlan(current, None, (), (), None, True)

    successor = _claim(
        instance_id=successor_id,
        members=members,
        projection=current.projection,
    )
    return CodespaceEditPlan(
        current=current,
        successor=successor,
        conflicting_checkout_keys=conflicts,
        dirty_member_names=tuple(
            member.name for member in candidates if member.checkout.dirty
        ),
        released=released_edit_debt(current, successor),
        no_op=False,
    )


def plan_codespace_projection(claim: CodespaceClaim) -> CodespaceProjectionPlan:
    structure_key = projection_structure_key(claim.members)
    current = claim.projection
    if current is None:
        return CodespaceProjectionPlan(
            action="create",
            projection=CodespaceProjection(generation=1, structure_key=structure_key),
        )
    if current.structure_key == structure_key:
        return CodespaceProjectionPlan(action="reuse", projection=current)
    return CodespaceProjectionPlan(
        action="replace",
        projection=CodespaceProjection(
            generation=current.generation + 1,
            structure_key=structure_key,
        ),
        superseded_name=projection_name(claim.instance_id, current.generation),
    )


def plan_codespace_edit_projection(
    current: CodespaceClaim,
    successor: CodespaceClaim,
) -> CodespaceProjectionPlan | None:
    projection = current.projection
    if projection is None:
        return None
    return CodespaceProjectionPlan(
        action="replace",
        projection=CodespaceProjection(
            generation=projection.generation + 1,
            structure_key=projection_structure_key(successor.members),
        ),
        superseded_name=projection_name(
            current.instance_id,
            projection.generation,
        ),
    )


def plan_codespace_unlock(
    claim: CodespaceClaim,
    *,
    force: bool = False,
) -> CodespaceReleasePlan:
    return CodespaceReleasePlan(
        instance_id=claim.instance_id,
        projection_name=(
            projection_name(claim.instance_id, claim.projection.generation)
            if claim.projection is not None
            else None
        ),
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
