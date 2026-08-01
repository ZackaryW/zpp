from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
from typing import Sequence

from zpp.utils.codespace_models import CodespaceMember
from zpp.utils.git_layers import GitCheckout


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def snapshot_key(checkouts: Sequence[GitCheckout]) -> str:
    commits = [checkout.head for checkout in checkouts]
    return _digest(json.dumps(commits, ensure_ascii=False, separators=(",", ":")))


def checkout_claim_key(checkout: GitCheckout) -> str:
    return checkout_path_claim_key(checkout.root)


def checkout_path_claim_key(path: Path) -> str:
    canonical_root = os.path.normcase(str(path.resolve()))
    return _digest(canonical_root)


def new_codespace_instance_id(snapshot: str, *, token: str | None = None) -> str:
    entropy = secrets.token_hex(16) if token is None else token
    return _digest(f"{snapshot}\0{entropy}")[:12]


def projection_structure_key(members: Sequence[CodespaceMember]) -> str:
    structure = [
        (
            member.name,
            member.kind,
            member.store_id,
            os.path.normcase(str(member.effective_path.resolve())),
        )
        for member in members
    ]
    return _digest(json.dumps(structure, ensure_ascii=False, separators=(",", ":")))


def projection_name(instance_id: str, generation: int) -> str:
    if not instance_id:
        raise ValueError("projection instance id must not be empty")
    if generation < 1:
        raise ValueError("projection generation must be positive")
    return f"zpp-{instance_id}-g{generation}"


def sibling_worktree_path(checkout: GitCheckout, instance_id: str) -> Path:
    return checkout.root.parent / f"{checkout.root.name}-{instance_id}"
