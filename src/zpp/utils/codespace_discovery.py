from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from zpp.utils.codespace_models import CodespaceClaim


def _contains(root: Path, target: Path) -> bool:
    canonical_root = os.path.normcase(str(root.resolve()))
    canonical_target = os.path.normcase(str(target.resolve()))
    try:
        return os.path.commonpath((canonical_root, canonical_target)) == canonical_root
    except ValueError:
        return False


def discover_codespace(
    target: Path,
    *,
    claims: Sequence[CodespaceClaim],
) -> str | None:
    active = [
        claim.instance_id
        for claim in claims
        if any(_contains(member.effective_path, target) for member in claim.members)
    ]
    if len(active) > 1:
        raise ValueError("target belongs to multiple active codespace claims")
    return active[0] if active else None
