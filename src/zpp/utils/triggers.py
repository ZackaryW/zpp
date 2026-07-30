from __future__ import annotations

from collections.abc import Iterable, Sequence
import os
from pathlib import Path, PurePosixPath
import shutil

from zpp.utils.models import LayerControls, TriggerRule


def compose_trigger_rules(
    layers: Iterable[LayerControls],
) -> tuple[TriggerRule, ...]:
    composed: list[TriggerRule] = []
    for layer in layers:
        if layer.trait_overwrites:
            composed.clear()
        composed.extend(layer.triggers)
    return tuple(composed)


def workspace_contains_any(target: Path, patterns: Sequence[str]) -> bool:
    def raise_traversal_error(error: OSError) -> None:
        raise error

    for root_text, directories, files in os.walk(
        target,
        topdown=True,
        onerror=raise_traversal_error,
    ):
        root = Path(root_text)
        directories[:] = [
            name
            for name in directories
            if name != ".git"
            and not (name == "cached" and root.name == ".zpp")
            and not (root / name).is_symlink()
        ]
        for name in files:
            relative = PurePosixPath((root / name).relative_to(target).as_posix())
            if any(relative.full_match(pattern) for pattern in patterns):
                return True
    return False


def activated_trait_names(
    rules: Iterable[TriggerRule],
    *,
    target: Path,
) -> tuple[str, ...]:
    activated: list[str] = []
    seen: set[str] = set()
    for rule in rules:
        matches = (
            rule.which is None
            and rule.workspace_contain is None
            or rule.which is not None
            and shutil.which(rule.which) is not None
            or rule.workspace_contain is not None
            and workspace_contains_any(target, rule.workspace_contain)
        )
        if matches and rule.trait not in seen:
            seen.add(rule.trait)
            activated.append(rule.trait)
    return tuple(activated)
