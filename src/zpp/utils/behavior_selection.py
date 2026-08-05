from __future__ import annotations

from collections.abc import Sequence

from zpp.utils.behavior_mapping import (
    TARGET_MARKER,
    BehaviorCommand,
    BehaviorTarget,
)
from zpp.utils.globs import glob_full_match


def select_affected_targets(
    command: BehaviorCommand, changed: Sequence[str]
) -> tuple[BehaviorTarget, ...]:
    if not changed:
        return ()

    matched_names: set[str] = set()
    for path in changed:
        path_matches = {
            name
            for name, target in command.targets.items()
            if any(glob_full_match(path, pattern) for pattern in target.paths)
        }
        if not path_matches:
            return tuple(command.targets.values())
        matched_names.update(path_matches)

    return tuple(
        target
        for name, target in command.targets.items()
        if name in matched_names
    )


def expand_target_argv(
    argv: Sequence[str], targets: Sequence[str]
) -> tuple[str, ...]:
    arguments = tuple(argv)
    if arguments.count(TARGET_MARKER) != 1:
        raise ValueError("argv requires exactly one target expansion position")
    index = arguments.index(TARGET_MARKER)
    return (*arguments[:index], *targets, *arguments[index + 1 :])
