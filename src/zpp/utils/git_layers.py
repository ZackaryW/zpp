from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from zpp.utils.models import CanonicalDirectory
from zpp.utils.paths import path_is_within
from zpp.utils.processes import ProcessResult, run_process


@dataclass(frozen=True, slots=True)
class GitCheckout:
    root: Path
    common_dir: Path
    head: str
    dirty: bool


def _git(checkout: Path, *arguments: str) -> ProcessResult:
    result = run_process(("git", "-C", str(checkout), *arguments))
    return result


def _require_git(result: ProcessResult, operation: str) -> ProcessResult:
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"{operation} failed: {detail}")
    return result


def inspect_git_checkout(path: Path) -> GitCheckout:
    target = path if path.is_dir() else path.parent
    root_result = _require_git(
        _git(target, "rev-parse", "--show-toplevel"),
        "Git checkout inspection",
    )
    root = Path(root_result.stdout.strip()).resolve()
    head_result = _git(root, "rev-parse", "--verify", "HEAD")
    if head_result.returncode != 0:
        raise ValueError(f"{root} has no committed HEAD")
    common_result = _require_git(
        _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"),
        "Git common-directory inspection",
    )
    status_result = _require_git(
        _git(root, "status", "--porcelain=v1", "--untracked-files=normal"),
        "Git dirty-state inspection",
    )
    return GitCheckout(
        root=root,
        common_dir=Path(common_result.stdout.strip()).resolve(),
        head=head_result.stdout.strip(),
        dirty=bool(status_result.stdout),
    )


def git_branch_exists(checkout: GitCheckout, branch: str) -> bool:
    result = _git(
        checkout.root,
        "show-ref",
        "--verify",
        "--quiet",
        f"refs/heads/{branch}",
    )
    if result.returncode not in (0, 1):
        _require_git(result, "Git branch inspection")
    return result.returncode == 0


def create_git_worktree(
    checkout: GitCheckout,
    *,
    destination: Path,
    branch: str,
    start_commit: str,
) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    if git_branch_exists(checkout, branch):
        raise ValueError(f"branch already exists: {branch}")
    _require_git(
        _git(
            checkout.root,
            "worktree",
            "add",
            "-b",
            branch,
            str(destination),
            start_commit,
        ),
        "Git worktree creation",
    )


def remove_git_worktree(checkout: GitCheckout, *, destination: Path) -> None:
    _require_git(
        _git(checkout.root, "worktree", "remove", str(destination)),
        "Git worktree removal",
    )


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
