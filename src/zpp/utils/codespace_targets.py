from __future__ import annotations

from pathlib import Path
from typing import Sequence

from zpp.utils.codespace_identity import checkout_claim_key
from zpp.utils.codespace_planning import ResolvedMember
from zpp.utils.git_layers import inspect_git_checkout
from zpp.utils.openspec_adapter import OpenSpecMember, resolve_openspec_relations
from zpp.utils.workspace_descriptors import load_code_workspace


def explicit_members(
    *,
    workspace: Path | None,
    paths: Sequence[Path],
) -> tuple[OpenSpecMember, ...] | None:
    if workspace is not None and paths:
        raise ValueError("choose either a workspace or paths")
    if workspace is not None:
        return load_code_workspace(workspace)
    if paths:
        return tuple(
            OpenSpecMember(path.resolve().name, path.resolve())
            for path in paths
        )
    return None


def resolve_codespace_members(
    members: Sequence[OpenSpecMember],
) -> tuple[ResolvedMember, ...]:
    resolved: list[ResolvedMember] = []
    seen: set[str] = set()
    for member in members:
        checkout = inspect_git_checkout(member.path)
        project_key = checkout_claim_key(checkout)
        if project_key in seen:
            continue
        seen.add(project_key)
        resolved.append(
            ResolvedMember(
                name=member.name,
                checkout=checkout,
                checkout_key=project_key,
                kind="project",
            )
        )
        for relation in resolve_openspec_relations(checkout.root):
            if relation.role == "reference":
                continue
            store_checkout = inspect_git_checkout(relation.root)
            store_key = checkout_claim_key(store_checkout)
            if store_key in seen:
                continue
            seen.add(store_key)
            resolved.append(
                ResolvedMember(
                    name=relation.store_id,
                    checkout=store_checkout,
                    checkout_key=store_key,
                    kind="store",
                    role="governing",
                    store_id=relation.store_id,
                )
            )
    return tuple(resolved)
