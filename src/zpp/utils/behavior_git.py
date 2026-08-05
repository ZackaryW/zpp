from __future__ import annotations

from pathlib import Path

from zpp.utils.models import ManagedStateError
from zpp.utils.processes import ProcessResult, run_process


_DIFF_FILTER = "ACMRTUXB"


def discover_worktree_root(start: Path) -> Path:
    result = run_process(("git", "rev-parse", "--show-toplevel"), cwd=start)
    if result.returncode != 0:
        raise ManagedStateError(
            f"Git worktree discovery failed for {start}: {_diagnostic(result)}"
        )
    value = result.stdout.strip()
    if not value:
        raise ManagedStateError(f"Git worktree discovery returned no root for {start}")
    return Path(value).resolve()


def collect_local_changed_paths(root: Path) -> tuple[str, ...]:
    tracked = _git_paths(
        root,
        ("git", "diff", "--name-only", f"--diff-filter={_DIFF_FILTER}", "-z", "HEAD"),
    )
    untracked = _git_paths(
        root,
        ("git", "ls-files", "--others", "--exclude-standard", "-z"),
    )
    return tuple(sorted({*tracked, *untracked}))


def collect_revision_changed_paths(
    root: Path, base: str, head: str
) -> tuple[str, ...]:
    return _git_paths(
        root,
        (
            "git",
            "diff",
            "--name-only",
            f"--diff-filter={_DIFF_FILTER}",
            "-z",
            base,
            head,
        ),
    )


def _git_paths(root: Path, argv: tuple[str, ...]) -> tuple[str, ...]:
    result = run_process(argv, cwd=root)
    if result.returncode != 0:
        raise ManagedStateError(
            f"Git change evidence failed for {root}: {_diagnostic(result)}"
        )
    paths = {
        value.replace("\\", "/")
        for value in result.stdout.split("\0")
        if value
    }
    return tuple(sorted(paths))


def _diagnostic(result: ProcessResult) -> str:
    return (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
