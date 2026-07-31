from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Sequence

from zpp.utils.codespace_models import CodespaceClaim
from zpp.utils.openspec_adapter import OpenSpecWorkset


@dataclass(frozen=True, slots=True)
class CodespaceDiscovery:
    active_id: str | None
    candidates: tuple[OpenSpecWorkset, ...]


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
    worksets: Sequence[OpenSpecWorkset],
) -> CodespaceDiscovery:
    active = [
        claim.instance_id
        for claim in claims
        if any(_contains(member.effective_path, target) for member in claim.members)
    ]
    if len(active) > 1:
        raise ValueError("target belongs to multiple active codespace claims")
    if active:
        return CodespaceDiscovery(active_id=active[0], candidates=())

    candidates = tuple(
        workset
        for workset in worksets
        if any(_contains(member.path, target) for member in workset.members)
    )
    return CodespaceDiscovery(active_id=None, candidates=candidates)
