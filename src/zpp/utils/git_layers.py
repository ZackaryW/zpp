from __future__ import annotations

from pathlib import Path
import subprocess

from zpp.utils.models import CanonicalDirectory
from zpp.utils.paths import path_is_within


def git_worktree_root(target: Path) -> Path | None:
    if not target.is_dir():
        return None
    completed = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip()).resolve()


def discover_local_layers(
    worktree_root: CanonicalDirectory,
    target: CanonicalDirectory,
) -> tuple[Path, ...]:
    if not path_is_within(target, worktree_root):
        raise ValueError("target is outside the Git worktree")

    cursor = worktree_root.resolved
    candidates = [cursor]
    for part in target.resolved.relative_to(worktree_root.resolved).parts:
        cursor = cursor / part
        candidates.append(cursor)
    return tuple(candidate / ".zpp" for candidate in candidates if (candidate / ".zpp").is_dir())
