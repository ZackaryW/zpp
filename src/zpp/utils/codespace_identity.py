from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
from typing import Sequence

from zpp.utils.git_layers import GitCheckout


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def snapshot_key(checkouts: Sequence[GitCheckout]) -> str:
    commits = [checkout.head for checkout in checkouts]
    return _digest(json.dumps(commits, ensure_ascii=False, separators=(",", ":")))


def checkout_claim_key(checkout: GitCheckout) -> str:
    canonical_root = os.path.normcase(str(checkout.root.resolve()))
    return _digest(canonical_root)


def new_codespace_instance_id(snapshot: str, *, token: str | None = None) -> str:
    entropy = secrets.token_hex(16) if token is None else token
    return _digest(f"{snapshot}\0{entropy}")[:12]


def sibling_worktree_path(checkout: GitCheckout, instance_id: str) -> Path:
    return checkout.root.parent / f"{checkout.root.name}-{instance_id}"
