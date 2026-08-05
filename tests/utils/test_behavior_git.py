from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from zpp.utils.behavior_git import (
    collect_local_changed_paths,
    collect_revision_changed_paths,
    discover_worktree_root,
)
from zpp.utils.models import ManagedStateError


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args), cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "--quiet")
    git(root, "config", "user.email", "bdd@example.test")
    git(root, "config", "user.name", "BDD")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    (root / "nested").mkdir()
    (root / "nested" / "also.txt").write_text("base\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "--quiet", "-m", "base")
    return root


def test_discover_worktree_root_from_nested_directory(tmp_path: Path) -> None:
    root = repository(tmp_path)
    nested = root / "nested" / "deeper"
    nested.mkdir()

    assert discover_worktree_root(nested) == root.resolve()


def test_collect_local_changes_unions_tracked_staged_unstaged_and_untracked(
    tmp_path: Path,
) -> None:
    root = repository(tmp_path)
    (root / "tracked.txt").write_text("unstaged\n", encoding="utf-8")
    (root / "staged.txt").write_text("staged\n", encoding="utf-8")
    git(root, "add", "staged.txt")
    (root / "untracked dir").mkdir()
    (root / "untracked dir" / "value.txt").write_text("new\n", encoding="utf-8")
    (root / "ignored.txt").write_text("ignored\n", encoding="utf-8")
    (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")

    assert collect_local_changed_paths(root) == (
        ".gitignore",
        "staged.txt",
        "tracked.txt",
        "untracked dir/value.txt",
    )


def test_collect_revision_changes_compares_exact_revisions_only(tmp_path: Path) -> None:
    root = repository(tmp_path)
    base = git(root, "rev-parse", "HEAD")
    (root / "nested" / "also.txt").write_text("head\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "--quiet", "-m", "head")
    head = git(root, "rev-parse", "HEAD")
    (root / "working.txt").write_text("working\n", encoding="utf-8")

    assert collect_revision_changed_paths(root, base, head) == ("nested/also.txt",)


def test_git_evidence_fails_without_partial_results(tmp_path: Path) -> None:
    root = repository(tmp_path)

    with pytest.raises(ManagedStateError, match="Git change evidence"):
        collect_revision_changed_paths(root, "missing-base", "HEAD")
    with pytest.raises(ManagedStateError, match="Git worktree"):
        discover_worktree_root(tmp_path)
