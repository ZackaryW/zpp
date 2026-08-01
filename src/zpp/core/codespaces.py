from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Sequence

from zpp.core.errors import ZppDomainError
from zpp.utils.codespace_discovery import discover_codespace
from zpp.utils.codespace_catalog import (
    plan_released_codespace_cleanup,
    record_codespace_cleanup,
    release_codespace_claim,
)
from zpp.utils.codespace_environment import (
    activate_codespace_shell,
    execute_codespace_command,
    materialize_private_registry,
    private_openspec_environment,
)
from zpp.utils.codespace_identity import (
    checkout_claim_key,
    new_codespace_instance_id,
    snapshot_key,
)
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, ReleasedCodespace
from zpp.utils.codespace_planning import (
    CodespaceAddPlan,
    CodespaceLockPlan,
    CodespaceRequest,
    ResolvedMember,
    plan_codespace_add,
    plan_codespace_cleanup,
    plan_codespace_lock,
    plan_codespace_unlock,
)
from zpp.utils.codespace_state import load_codespace_index, mutate_codespace_index
from zpp.utils.git_layers import (
    create_git_worktree,
    git_branch_exists,
    inspect_git_checkout,
    remove_git_worktree,
)
from zpp.utils.openspec_adapter import (
    OpenSpecMember,
    OpenSpecWorkset,
    create_openspec_workset,
    list_openspec_worksets,
    open_openspec_workset,
    remove_openspec_workset,
    resolve_openspec_relations,
)
from zpp.utils.workspace_descriptors import load_code_workspace


@dataclass(frozen=True, slots=True)
class CodespaceLockResult:
    claim: CodespaceClaim
    conflicts: tuple[str, ...]
    dirty_members: tuple[str, ...]
    existing: bool = False


class CodespaceConflictError(ZppDomainError):
    def __init__(self, names: tuple[str, ...]) -> None:
        self.names = names
        super().__init__("conflicting writable checkouts: " + ", ".join(names))


def codespace_root(home: Path) -> Path:
    return home / ".zpp" / "codespaces"


def read_codespaces(home: Path) -> CodespaceIndex:
    return load_codespace_index(codespace_root(home))


def discover_codespace_view(
    *,
    home: Path,
    current_directory: Path,
) -> str | None:
    index = read_codespaces(home)
    return discover_codespace(
        current_directory,
        claims=tuple(index.claims.values()),
        worksets=list_openspec_worksets(),
    )


def select_workset(name: str) -> OpenSpecWorkset:
    matches = [item for item in list_openspec_worksets() if item.name == name]
    if not matches:
        raise ZppDomainError(f"OpenSpec workset does not exist: {name}")
    return matches[0]


def explicit_members(
    *,
    workset: str | None,
    workspace: Path | None,
    paths: Sequence[Path],
) -> tuple[OpenSpecMember, ...] | None:
    supplied = int(workset is not None) + int(workspace is not None) + int(bool(paths))
    if supplied > 1:
        raise ZppDomainError("choose one of --workset, --workspace, or paths")
    if workset is not None:
        return select_workset(workset).members
    if workspace is not None:
        return load_code_workspace(workspace)
    if paths:
        return tuple(OpenSpecMember(path.resolve().name, path.resolve()) for path in paths)
    return None


def _resolved_members(members: Sequence[OpenSpecMember]) -> tuple[ResolvedMember, ...]:
    resolved: list[ResolvedMember] = []
    seen: set[tuple[str, str]] = set()
    for member in members:
        checkout = inspect_git_checkout(member.path)
        project_key = ("project", checkout_claim_key(checkout))
        resolved.append(
            ResolvedMember(
                name=member.name,
                checkout=checkout,
                checkout_key=project_key[1],
                kind="project",
            )
        )
        for relation in resolve_openspec_relations(checkout.root):
            store_checkout = inspect_git_checkout(relation.root)
            store_key = checkout_claim_key(store_checkout)
            key = ("store", store_key)
            if key in seen and relation.role == "reference":
                continue
            seen.add(key)
            resolved.append(
                ResolvedMember(
                    name=relation.store_id,
                    checkout=store_checkout,
                    checkout_key=store_key,
                    kind="store",
                    role=relation.role,
                    store_id=relation.store_id,
                )
            )
    return tuple(resolved)


def _conflict_names(plan: CodespaceLockPlan) -> tuple[str, ...]:
    keys = set(plan.conflicting_checkout_keys)
    return tuple(
        member.name
        for member in plan.claim.members
        if member.source_checkout_key in keys
    )


def lock_codespace(
    *,
    home: Path,
    members: Sequence[OpenSpecMember],
    mitigate: bool,
) -> CodespaceLockResult:
    resolved = _resolved_members(members)
    writable = tuple(member for member in resolved if member.role == "governing")
    snapshot = snapshot_key(tuple(member.checkout for member in writable))
    instance = new_codespace_instance_id(snapshot)
    plan = plan_codespace_lock(
        CodespaceRequest(instance, snapshot, f"zpp-{instance}", resolved),
        read_codespaces(home),
    )
    conflict_names = _conflict_names(plan)
    if conflict_names and not mitigate:
        raise CodespaceConflictError(conflict_names)
    _preflight_worktrees(plan.claim)
    created: list[tuple[object, Path]] = []
    workset_created = False
    try:
        sources = {member.checkout_key: member.checkout for member in writable}
        for target in plan.claim.members:
            if target.generated_worktree:
                source = sources[target.source_checkout_key]
                create_git_worktree(
                    source,
                    destination=target.effective_path,
                    branch=target.branch or "",
                    start_commit=target.commit,
                )
                created.append((source, target.effective_path))
        environment = private_openspec_environment(
            codespace_root(home) / plan.claim.instance_id,
            os.environ,
        )
        materialize_private_registry(plan.claim, environment=environment)
        create_openspec_workset(
            plan.claim.workset_name,
            tuple(OpenSpecMember(item.name, item.effective_path) for item in plan.claim.members),
        )
        workset_created = True
        mutate_codespace_index(
            codespace_root(home),
            lambda index: CodespaceIndex(
                claims={**index.claims, plan.claim.instance_id: plan.claim},
                released=index.released,
            ),
        )
    except BaseException:
        if workset_created:
            remove_openspec_workset(plan.claim.workset_name)
        for checkout, destination in reversed(created):
            try:
                remove_git_worktree(checkout, destination=destination)  # type: ignore[arg-type]
            except (OSError, ValueError):
                pass
        raise
    return CodespaceLockResult(plan.claim, conflict_names, plan.dirty_member_names)


def _preflight_worktrees(claim: CodespaceClaim) -> None:
    for member in claim.members:
        if not member.generated_worktree:
            continue
        checkout = inspect_git_checkout(member.original_path)
        if member.effective_path.exists() or member.effective_path.is_symlink():
            raise FileExistsError(member.effective_path)
        if member.branch and git_branch_exists(checkout, member.branch):
            raise ZppDomainError(f"branch already exists: {member.branch}")


def find_claim(home: Path, identifier: str | None, cwd: Path) -> CodespaceClaim:
    index = read_codespaces(home)
    if identifier is not None:
        claim = index.claims.get(identifier)
        if claim is None:
            raise ZppDomainError(f"codespace does not exist: {identifier}")
        return claim
    discovery = discover_codespace(
        cwd,
        claims=tuple(index.claims.values()),
        worksets=(),
    )
    if discovery.active_id is None:
        raise ZppDomainError("current directory is not inside an active codespace")
    return index.claims[discovery.active_id]


def find_released(home: Path, identifier: str) -> ReleasedCodespace:
    released = read_codespaces(home).released.get(identifier)
    if released is None:
        raise ZppDomainError(f"released codespace does not exist: {identifier}")
    return released


def add_codespace_paths(
    *,
    home: Path,
    claim: CodespaceClaim,
    paths: Sequence[Path],
    mitigate: bool,
) -> CodespaceClaim:
    additions = _resolved_members(
        tuple(OpenSpecMember(path.resolve().name, path.resolve()) for path in paths)
    )
    plan: CodespaceAddPlan = plan_codespace_add(claim, additions, read_codespaces(home))
    names = tuple(
        item.name
        for item in plan.additions
        if item.checkout_key in set(plan.conflicting_checkout_keys)
    )
    if names and not mitigate:
        raise CodespaceConflictError(names)
    replacement = plan.replacement
    existing_keys = {member.checkout_key for member in claim.members}
    _preflight_worktrees(
        replacement.model_copy(
            update={
                "members": tuple(
                    member
                    for member in replacement.members
                    if member.checkout_key not in existing_keys
                )
            }
        )
    )
    created: list[tuple[object, Path]] = []
    registered = False
    try:
        source_by_key = {item.checkout_key: item.checkout for item in plan.additions}
        for member in replacement.members:
            if member.generated_worktree and member.checkout_key not in {
                item.checkout_key for item in claim.members
            }:
                source = source_by_key[member.source_checkout_key]
                create_git_worktree(
                    source,
                    destination=member.effective_path,
                    branch=member.branch or "",
                    start_commit=member.commit,
                )
                created.append((source, member.effective_path))
        create_openspec_workset(
            replacement.workset_name,
            tuple(OpenSpecMember(item.name, item.effective_path) for item in replacement.members),
        )
        registered = True
        mutate_codespace_index(
            codespace_root(home),
            lambda index: CodespaceIndex(
                claims={**index.claims, claim.instance_id: replacement},
                released=index.released,
            ),
        )
        if plan.superseded_workset_name:
            remove_openspec_workset(plan.superseded_workset_name)
    except BaseException:
        if registered:
            remove_openspec_workset(replacement.workset_name)
        for source, path in reversed(created):
            try:
                remove_git_worktree(source, destination=path)  # type: ignore[arg-type]
            except (OSError, ValueError):
                pass
        raise
    return replacement


def unlock_codespace(home: Path, claim: CodespaceClaim, *, force: bool = False) -> None:
    plan = plan_codespace_unlock(claim, force=force)
    if plan.workset_name:
        remove_openspec_workset(plan.workset_name)
    mutate_codespace_index(
        codespace_root(home),
        lambda index: release_codespace_claim(index, claim.instance_id)[0],
    )


def cleanup_codespace(
    home: Path,
    released: ReleasedCodespace,
) -> tuple[Path, ...]:
    inspections = {}
    for member in released.claim.members:
        if (
            member.generated_worktree
            and member.checkout_key not in released.removed_worktree_keys
            and member.effective_path.exists()
        ):
            inspections[member.checkout_key] = inspect_git_checkout(member.effective_path)
    plan = plan_released_codespace_cleanup(released, inspections)
    removed: list[Path] = []
    removed_keys: list[str] = []
    for member in plan.removable:
        source = inspect_git_checkout(member.original_path)
        remove_git_worktree(source, destination=member.effective_path)
        removed.append(member.effective_path)
        removed_keys.append(member.checkout_key)
    if removed_keys:
        mutate_codespace_index(
            codespace_root(home),
            lambda index: record_codespace_cleanup(
                index,
                released.claim.instance_id,
                removed_keys,
            ),
        )
    return tuple(removed)


def open_codespace(claim: CodespaceClaim, tool: str | None = None) -> int:
    return open_openspec_workset(claim.workset_name, tool=tool)


def codespace_environment(home: Path, claim: CodespaceClaim) -> dict[str, str]:
    return private_openspec_environment(
        codespace_root(home) / claim.instance_id,
        os.environ,
    )


def exec_codespace(
    home: Path,
    claim: CodespaceClaim,
    argv: Sequence[str],
) -> int:
    return execute_codespace_command(
        argv,
        environment=codespace_environment(home, claim),
        cwd=claim.members[0].effective_path,
    )


def activate_codespace(home: Path, claim: CodespaceClaim) -> int:
    return activate_codespace_shell(
        environment=codespace_environment(home, claim),
        cwd=claim.members[0].effective_path,
    )
