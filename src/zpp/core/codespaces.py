from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal, Mapping, Sequence

from zpp.core.errors import ZppDomainError
from zpp.utils.codespace_catalog import (
    finalize_released_codespace,
    plan_released_codespace_cleanup,
    record_branch_disposition,
    record_codespace_cleanup,
    release_codespace_claim,
)
from zpp.utils.codespace_claims import (
    claimed_checkout_owners,
    find_matching_codespace_claim,
    register_codespace_claim,
    transition_codespace_claim,
    update_codespace_claim,
)
from zpp.utils.codespace_discovery import discover_codespace
from zpp.utils.codespace_environment import (
    activate_codespace_shell,
    execute_codespace_command,
    materialize_private_registry,
    private_openspec_environment,
)
from zpp.utils.codespace_guard import (
    AgentName,
    UnsupportedGuardTool,
    decode_agent_guard_request,
    encode_agent_guard_decision,
    evaluate_codespace_guard,
)
from zpp.utils.codespace_edits import CodespaceEditOperations
from zpp.utils.codespace_identity import new_codespace_instance_id, projection_name
from zpp.utils.codespace_members import writable_members
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, ReleasedCodespace
from zpp.utils.codespace_planning import (
    CodespaceEditPlan,
    CodespaceLockPlan,
    CodespaceProjectionPlan,
    CodespaceRequest,
    plan_codespace_edit,
    plan_codespace_edit_projection,
    plan_codespace_lock,
    plan_codespace_projection,
    plan_codespace_unlock,
    refresh_codespace_snapshot,
)
from zpp.utils.codespace_projection import orphaned_codespace_projections
from zpp.utils.codespace_state import load_codespace_index, mutate_codespace_index
from zpp.utils.codespace_targets import CodespaceTarget, resolve_codespace_members
from zpp.utils.git_layers import (
    GitCheckout,
    create_git_worktree,
    git_branch_exists,
    inspect_git_checkout,
    remove_git_worktree,
)
from zpp.utils.openspec_adapter import (
    OpenSpecMember,
    create_openspec_workset,
    list_openspec_worksets,
    open_openspec_workset,
    remove_openspec_workset,
)


@dataclass(frozen=True, slots=True)
class CodespaceLockResult:
    claim: CodespaceClaim
    conflicts: tuple[str, ...]
    dirty_members: tuple[str, ...]
    existing: bool = False


@dataclass(frozen=True, slots=True)
class CodespaceEditPreview:
    plan: CodespaceEditPlan
    sources: Mapping[str, GitCheckout]

    @property
    def conflict_names(self) -> tuple[str, ...]:
        keys = set(self.plan.conflicting_checkout_keys)
        successor = self.plan.successor
        if successor is None:
            return ()
        return tuple(
            member.name
            for member in successor.members
            if member.source_checkout_key in keys
        )


class CodespaceConflictError(ZppDomainError):
    def __init__(
        self,
        names: tuple[str, ...],
        owner_ids: tuple[str, ...] = (),
    ) -> None:
        self.names = names
        self.owner_ids = owner_ids
        message = "conflicting writable checkouts: " + ", ".join(names)
        if owner_ids:
            message += "; active owners: " + ", ".join(owner_ids)
        super().__init__(message)


def codespace_root(home: Path) -> Path:
    return home / ".zpp" / "codespaces"


def read_codespaces(home: Path) -> CodespaceIndex:
    return load_codespace_index(codespace_root(home))


def _remove_orphaned_projections(home: Path) -> None:
    index = read_codespaces(home)
    for name in orphaned_codespace_projections(index, list_openspec_worksets()):
        remove_openspec_workset(name)


def discover_codespace_view(
    *,
    home: Path,
    current_directory: Path,
) -> str | None:
    index = read_codespaces(home)
    return discover_codespace(
        current_directory,
        claims=tuple(index.claims.values()),
    )


def _conflict_names(plan: CodespaceLockPlan) -> tuple[str, ...]:
    keys = set(plan.conflicting_checkout_keys)
    return tuple(
        member.name
        for member in plan.claim.members
        if member.source_checkout_key in keys
    )


def _current_dirty_members(claim: CodespaceClaim) -> tuple[str, ...]:
    return tuple(
        member.name
        for member in claim.members
        if inspect_git_checkout(member.effective_path).dirty
    )


def _preflight_worktrees(claim: CodespaceClaim) -> None:
    for member in claim.members:
        if not member.generated_worktree:
            continue
        checkout = inspect_git_checkout(member.original_path)
        if member.effective_path.exists() or member.effective_path.is_symlink():
            raise FileExistsError(member.effective_path)
        if member.branch and git_branch_exists(checkout, member.branch):
            raise ZppDomainError(f"branch already exists: {member.branch}")


def _create_worktrees(
    claim: CodespaceClaim,
    sources: Mapping[str, GitCheckout],
    *,
    existing_keys: set[str] | None = None,
) -> list[tuple[GitCheckout, Path]]:
    created: list[tuple[GitCheckout, Path]] = []
    retained = existing_keys or set()
    for member in claim.members:
        if not member.generated_worktree or member.checkout_key in retained:
            continue
        source = sources[member.source_checkout_key]
        create_git_worktree(
            source,
            destination=member.effective_path,
            branch=member.branch or "",
            start_commit=member.commit,
        )
        created.append((source, member.effective_path))
    return created


def _rollback_worktrees(created: Sequence[tuple[GitCheckout, Path]]) -> None:
    for source, destination in reversed(created):
        try:
            remove_git_worktree(source, destination=destination)
        except (OSError, ValueError):
            pass


def _materialize_registry(home: Path, claim: CodespaceClaim) -> None:
    materialize_private_registry(
        claim,
        environment=private_openspec_environment(
            codespace_root(home) / claim.instance_id,
            os.environ,
        ),
    )


def lock_codespace(
    *,
    home: Path,
    targets: Sequence[CodespaceTarget],
    mitigate: bool,
) -> CodespaceLockResult:
    _remove_orphaned_projections(home)
    resolved = resolve_codespace_members(targets)
    if not resolved:
        raise ZppDomainError("no codespace targets were resolved")
    if not any(member.access == "writable" for member in resolved):
        raise ZppDomainError("a codespace requires at least one writable target")
    index = read_codespaces(home)
    matching = find_matching_codespace_claim(
        index,
        {(member.checkout_key, member.access) for member in resolved},
    )
    if matching is not None:
        return CodespaceLockResult(
            matching,
            (),
            _current_dirty_members(matching),
            existing=True,
        )

    instance = new_codespace_instance_id()
    plan = plan_codespace_lock(
        CodespaceRequest(instance, resolved),
        index,
    )
    conflict_names = _conflict_names(plan)
    if conflict_names and not mitigate:
        owners = claimed_checkout_owners(index, plan.conflicting_checkout_keys)
        raise CodespaceConflictError(
            conflict_names,
            tuple(dict.fromkeys(conflict.owner_id for conflict in owners)),
        )

    _preflight_worktrees(plan.claim)
    sources = {member.checkout_key: member.checkout for member in resolved}
    created: list[tuple[GitCheckout, Path]] = []
    try:
        created = _create_worktrees(plan.claim, sources)
        _materialize_registry(home, plan.claim)
        mutate_codespace_index(
            codespace_root(home),
            lambda current: register_codespace_claim(current, plan.claim),
        )
    except BaseException:
        _rollback_worktrees(created)
        raise
    return CodespaceLockResult(plan.claim, conflict_names, plan.dirty_member_names)


def find_claim(home: Path, identifier: str | None, cwd: Path) -> CodespaceClaim:
    index = read_codespaces(home)
    selected = identifier or os.environ.get("ZPP_CODESPACE_ID")
    if selected is not None:
        claim = index.claims.get(selected)
        if claim is None:
            raise ZppDomainError(f"codespace does not exist: {selected}")
        return claim
    active_id = discover_codespace(
        cwd,
        claims=tuple(index.claims.values()),
    )
    if active_id is None:
        raise ZppDomainError("current directory is not inside an active codespace")
    return index.claims[active_id]


def find_released(home: Path, identifier: str) -> ReleasedCodespace:
    released = read_codespaces(home).released.get(identifier)
    if released is None:
        raise ZppDomainError(f"released codespace does not exist: {identifier}")
    return released


def _projection_members(claim: CodespaceClaim) -> tuple[OpenSpecMember, ...]:
    return tuple(
        OpenSpecMember(member.name, member.effective_path)
        for member in claim.members
    )


def _projection_claim(
    claim: CodespaceClaim,
    plan: CodespaceProjectionPlan,
) -> CodespaceClaim:
    return claim.model_copy(update={"projection": plan.projection})


def preview_codespace_edit(
    *,
    home: Path,
    claim: CodespaceClaim,
    operations: CodespaceEditOperations,
) -> CodespaceEditPreview:
    targets = tuple(
        CodespaceTarget(
            target.path.name,
            target.path,
            "read_only" if target.action == "add_read_only" else "writable",
        )
        for target in operations.targets
        if target.action in {"add", "add_read_only", "promote"}
    )
    resolved = resolve_codespace_members(targets)
    sources = {member.checkout_key: member.checkout for member in resolved}
    plan = plan_codespace_edit(
        claim,
        operations,
        resolved,
        read_codespaces(home),
        successor_id=new_codespace_instance_id(),
    )
    successor = plan.successor
    if successor is not None:
        inspections = {
            member.checkout_key: inspect_git_checkout(member.effective_path)
            for member in successor.members
            if member.effective_path.exists()
        }
        successor = refresh_codespace_snapshot(successor, inspections)
        plan = CodespaceEditPlan(
            current=plan.current,
            successor=successor,
            conflicting_checkout_keys=plan.conflicting_checkout_keys,
            dirty_member_names=plan.dirty_member_names,
            released=plan.released,
            no_op=plan.no_op,
        )
    return CodespaceEditPreview(plan=plan, sources=sources)


def apply_codespace_edit(
    *,
    home: Path,
    preview: CodespaceEditPreview,
    mitigate: bool,
) -> CodespaceClaim:
    _remove_orphaned_projections(home)
    plan = preview.plan
    if plan.no_op or plan.successor is None:
        return plan.current
    if plan.conflicting_checkout_keys and not mitigate:
        owners = claimed_checkout_owners(
            read_codespaces(home),
            plan.conflicting_checkout_keys,
            excluding=plan.current.instance_id,
        )
        raise CodespaceConflictError(
            preview.conflict_names,
            tuple(dict.fromkeys(conflict.owner_id for conflict in owners)),
        )

    successor = plan.successor
    current_keys = {member.checkout_key for member in plan.current.members}
    new_generated = successor.model_copy(
        update={
            "members": tuple(
                member
                for member in successor.members
                if member.checkout_key not in current_keys
            )
        }
    )
    _preflight_worktrees(new_generated)
    projection_plan = plan_codespace_edit_projection(plan.current, successor)
    created_projection: str | None = None
    if projection_plan is not None:
        successor = _projection_claim(successor, projection_plan)
        created_projection = projection_name(
            successor.instance_id,
            projection_plan.projection.generation,
        )

    created: list[tuple[GitCheckout, Path]] = []
    try:
        created = _create_worktrees(
            successor,
            preview.sources,
            existing_keys=current_keys,
        )
        _materialize_registry(home, successor)
        if created_projection is not None:
            create_openspec_workset(
                created_projection,
                _projection_members(successor),
            )
        mutate_codespace_index(
            codespace_root(home),
            lambda index: transition_codespace_claim(
                index,
                plan.current,
                successor,
                plan.released,
            ),
        )
    except BaseException:
        if created_projection is not None:
            try:
                remove_openspec_workset(created_projection)
            except (OSError, ValueError):
                pass
        _rollback_worktrees(created)
        raise

    if projection_plan is not None and projection_plan.superseded_name is not None:
        remove_openspec_workset(projection_plan.superseded_name)
    return successor


def unlock_codespace(home: Path, claim: CodespaceClaim, *, force: bool = False) -> None:
    _remove_orphaned_projections(home)
    plan = plan_codespace_unlock(claim, force=force)
    mutate_codespace_index(
        codespace_root(home),
        lambda index: release_codespace_claim(index, claim.instance_id)[0],
    )
    if plan.projection_name is not None:
        remove_openspec_workset(plan.projection_name)


def cleanup_codespace(
    home: Path,
    released: ReleasedCodespace,
) -> tuple[Path, ...]:
    _remove_orphaned_projections(home)
    inspections = {
        debt.checkout_key: inspect_git_checkout(debt.effective_path)
        for debt in released.debts
        if not debt.worktree_removed and debt.effective_path.exists()
    }
    plan = plan_released_codespace_cleanup(released, inspections)
    removed: list[Path] = []
    removed_keys: list[str] = []
    for debt in plan.removable:
        source = inspect_git_checkout(debt.original_path)
        remove_git_worktree(source, destination=debt.effective_path)
        removed.append(debt.effective_path)
        removed_keys.append(debt.checkout_key)
    if removed_keys:
        mutate_codespace_index(
            codespace_root(home),
            lambda index: record_codespace_cleanup(
                index,
                released.instance_id,
                removed_keys,
            ),
        )
    return tuple(removed)


def record_codespace_disposition(
    home: Path,
    identifier: str,
    checkout_key: str,
    disposition: Literal["reconciled", "abandoned"],
) -> None:
    _remove_orphaned_projections(home)
    mutate_codespace_index(
        codespace_root(home),
        lambda index: record_branch_disposition(
            index,
            identifier,
            checkout_key,
            disposition,
        ),
    )


def finalize_codespace(home: Path, identifier: str) -> None:
    _remove_orphaned_projections(home)
    mutate_codespace_index(
        codespace_root(home),
        lambda index: finalize_released_codespace(index, identifier),
    )


def open_codespace(
    home: Path,
    claim: CodespaceClaim,
    tool: str | None = None,
) -> int:
    _remove_orphaned_projections(home)
    plan = plan_codespace_projection(claim)
    current = claim
    created_name: str | None = None
    if plan.action != "reuse":
        current = _projection_claim(claim, plan)
        created_name = projection_name(
            current.instance_id,
            current.projection.generation,
        )
        create_openspec_workset(created_name, _projection_members(current))
        try:
            mutate_codespace_index(
                codespace_root(home),
                lambda index: update_codespace_claim(index, claim, current),
            )
        except BaseException:
            remove_openspec_workset(created_name)
            raise
        if plan.superseded_name is not None:
            remove_openspec_workset(plan.superseded_name)
    name = projection_name(current.instance_id, current.projection.generation)
    return open_openspec_workset(name, tool=tool)


def inspect_codespace_claim(claim: CodespaceClaim) -> tuple[dict[str, object], ...]:
    states: list[dict[str, object]] = []
    for member in claim.members:
        checkout = inspect_git_checkout(member.effective_path)
        states.append(
            {
                "name": member.name,
                "path": str(member.effective_path),
                "access": member.access,
                "claimed": member.access == "writable",
                "generated": member.generated_worktree,
                "starting_commit": member.commit,
                "current_commit": checkout.head,
                "dirty": checkout.dirty,
            }
        )
    return tuple(states)


def guard_codespace_request(
    home: Path,
    agent: AgentName,
    payload: Mapping[str, object],
) -> Mapping[str, object]:
    try:
        request = decode_agent_guard_request(agent, payload)
    except UnsupportedGuardTool:
        return {}
    decision = evaluate_codespace_guard(
        request,
        read_codespaces(home),
        associated_codespace=os.environ.get("ZPP_CODESPACE_ID"),
    )
    return encode_agent_guard_decision(agent, decision)


def codespace_environment(home: Path, claim: CodespaceClaim) -> dict[str, str]:
    environment = private_openspec_environment(
        codespace_root(home) / claim.instance_id,
        os.environ,
    )
    environment["ZPP_CODESPACE_ID"] = claim.instance_id
    return environment


def exec_codespace(
    home: Path,
    claim: CodespaceClaim,
    argv: Sequence[str],
) -> int:
    return execute_codespace_command(
        argv,
        environment=codespace_environment(home, claim),
        cwd=(writable_members(claim.members) or claim.members)[0].effective_path,
    )


def activate_codespace(home: Path, claim: CodespaceClaim) -> int:
    return activate_codespace_shell(
        environment=codespace_environment(home, claim),
        cwd=(writable_members(claim.members) or claim.members)[0].effective_path,
    )
