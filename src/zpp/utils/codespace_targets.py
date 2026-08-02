from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from zpp.utils.codespace_identity import checkout_claim_key
from zpp.utils.codespace_planning import ResolvedMember
from zpp.utils.git_layers import inspect_git_checkout
from zpp.utils.openspec_adapter import OpenSpecMember, resolve_openspec_relations
from zpp.utils.workspace_descriptors import load_code_workspace


@dataclass(frozen=True, slots=True)
class CodespaceTarget:
    name: str
    path: Path
    access: Literal["writable", "read_only"]


def explicit_codespace_targets(
    *,
    workspace: Path | None,
    writable_paths: Sequence[Path],
    read_only_paths: Sequence[Path],
) -> tuple[CodespaceTarget, ...] | None:
    if workspace is not None and writable_paths:
        raise ValueError("choose either a workspace or paths")
    writable: tuple[OpenSpecMember, ...]
    if workspace is not None:
        writable = load_code_workspace(workspace)
    else:
        writable = tuple(
            OpenSpecMember(path.resolve().name, path.resolve())
            for path in writable_paths
        )
    targets = tuple(
        CodespaceTarget(member.name, member.path, "writable")
        for member in writable
    ) + tuple(
        CodespaceTarget(path.resolve().name, path.resolve(), "read_only")
        for path in read_only_paths
    )
    return targets or None


def resolve_codespace_members(
    targets: Sequence[CodespaceTarget],
) -> tuple[ResolvedMember, ...]:
    resolved: list[ResolvedMember] = []
    positions: dict[str, int] = {}

    def include(candidate: ResolvedMember) -> None:
        position = positions.get(candidate.checkout_key)
        if position is None:
            positions[candidate.checkout_key] = len(resolved)
            resolved.append(candidate)
            return
        existing = resolved[position]
        if existing.access == "read_only" and candidate.access == "writable":
            resolved[position] = candidate

    for target in targets:
        checkout = inspect_git_checkout(target.path)
        project_key = checkout_claim_key(checkout)
        include(
            ResolvedMember(
                name=target.name,
                checkout=checkout,
                checkout_key=project_key,
                kind="project",
                access=target.access,
            )
        )
        if target.access == "read_only":
            continue
        for relation in resolve_openspec_relations(checkout.root):
            if relation.role == "reference":
                continue
            store_checkout = inspect_git_checkout(relation.root)
            include(
                ResolvedMember(
                    name=relation.store_id,
                    checkout=store_checkout,
                    checkout_key=checkout_claim_key(store_checkout),
                    kind="store",
                    access="writable",
                    store_id=relation.store_id,
                )
            )
    return tuple(resolved)
