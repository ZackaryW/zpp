from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
import json
from pathlib import Path

from filelock import FileLock
from pydantic import ValidationError

from zpp.utils.codespace_identity import projection_structure_key
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceProjection,
    ReleasedCheckoutDebt,
    ReleasedCodespace,
)
from zpp.utils.json_io import atomic_write_json


INDEX_NAME = "index.json"
LOCK_NAME = "index.lock"


@contextmanager
def codespace_index_lock(
    lock_path: Path,
    *,
    timeout: float = 0,
) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(lock_path, timeout=timeout):
        yield


def load_codespace_index(root: Path) -> CodespaceIndex:
    index_path = root / INDEX_NAME
    if not index_path.exists():
        return CodespaceIndex()
    try:
        value = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("codespace index must be a JSON object")
        return migrate_codespace_index(value)
    except (json.JSONDecodeError, UnicodeDecodeError, ValidationError, ValueError) as error:
        raise ValueError(f"{index_path} contains an invalid codespace index") from error


def migrate_codespace_index(payload: Mapping[str, object]) -> CodespaceIndex:
    version = payload.get("schema_version", 1)
    if version == 3:
        return CodespaceIndex.model_validate(payload)
    if version == 2:
        migrated = dict(payload)
        raw_claims = payload.get("claims", {})
        if not isinstance(raw_claims, dict):
            raise ValueError("legacy codespace claims are invalid")
        claims: dict[str, object] = {}
        for key, raw_claim in raw_claims.items():
            if not isinstance(key, str) or not isinstance(raw_claim, dict):
                raise ValueError("legacy codespace claim is invalid")
            claim = dict(raw_claim)
            raw_members = claim.get("members", [])
            if not isinstance(raw_members, list):
                raise ValueError("legacy codespace members are invalid")
            members: list[dict[str, object]] = []
            for raw_member in raw_members:
                if not isinstance(raw_member, dict):
                    raise ValueError("legacy codespace member is invalid")
                member = dict(raw_member)
                role = member.pop("role", "governing")
                if role != "governing":
                    raise ValueError("legacy codespace member access is ambiguous")
                member["access"] = "writable"
                members.append(member)
            claim["members"] = members
            claims[key] = claim
        migrated["schema_version"] = 3
        migrated["claims"] = claims
        return CodespaceIndex.model_validate(migrated)
    if version != 1:
        raise ValueError(f"unsupported codespace index schema: {version}")

    raw_claims = payload.get("claims", {})
    raw_released = payload.get("released", {})
    if not isinstance(raw_claims, dict) or not isinstance(raw_released, dict):
        raise ValueError("legacy codespace index collections are invalid")

    claims: dict[str, CodespaceClaim] = {}
    for key, raw_claim in raw_claims.items():
        if not isinstance(key, str) or not isinstance(raw_claim, dict):
            raise ValueError("legacy codespace claim is invalid")
        claim_payload = dict(raw_claim)
        workset_name = claim_payload.pop("workset_name", None)
        workset_owned = claim_payload.pop("workset_owned", True)
        claim_payload.pop("projection", None)
        claim = CodespaceClaim.model_validate(claim_payload)
        if workset_owned and isinstance(workset_name, str) and workset_name:
            claim = claim.model_copy(
                update={
                    "projection": CodespaceProjection(
                        generation=1,
                        structure_key=projection_structure_key(claim.members),
                    )
                }
            )
        claims[key] = claim

    released: dict[str, ReleasedCodespace] = {}
    for key, raw_entry in raw_released.items():
        if not isinstance(key, str) or not isinstance(raw_entry, dict):
            raise ValueError("legacy released codespace is invalid")
        raw_claim = raw_entry.get("claim")
        removed = raw_entry.get("removed_worktree_keys", [])
        if not isinstance(raw_claim, dict) or not isinstance(removed, (list, set, tuple)):
            raise ValueError("legacy released codespace is invalid")
        claim_payload = dict(raw_claim)
        claim_payload.pop("workset_name", None)
        claim_payload.pop("workset_owned", None)
        claim_payload.pop("projection", None)
        claim = CodespaceClaim.model_validate(claim_payload)
        removed_keys = {str(item) for item in removed}
        debts = tuple(
            ReleasedCheckoutDebt(
                original_path=member.original_path,
                effective_path=member.effective_path,
                checkout_key=member.checkout_key,
                branch=member.branch or "",
                worktree_removed=member.checkout_key in removed_keys,
            )
            for member in claim.members
            if member.generated_worktree
        )
        released[key] = ReleasedCodespace(instance_id=claim.instance_id, debts=debts)

    return CodespaceIndex(claims=claims, released=released)


def mutate_codespace_index(
    root: Path,
    transform: Callable[[CodespaceIndex], CodespaceIndex],
    *,
    timeout: float = 10,
) -> CodespaceIndex:
    root.mkdir(parents=True, exist_ok=True)
    with codespace_index_lock(root / LOCK_NAME, timeout=timeout):
        current = load_codespace_index(root)
        candidate = transform(current)
        if not isinstance(candidate, CodespaceIndex):
            raise TypeError("codespace index transform must return CodespaceIndex")
        updated = CodespaceIndex.model_validate(candidate.model_dump(mode="json"))
        atomic_write_json(root / INDEX_NAME, updated.model_dump(mode="json"))
        return updated
