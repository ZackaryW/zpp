from pathlib import Path
import subprocess

import pytest

from zpp.utils.git_layers import (
    create_git_worktree,
    discover_local_layers,
    git_branch_exists,
    git_worktree_root,
    inspect_git_checkout,
    remove_git_worktree,
)
from zpp.utils.paths import canonicalize_existing_directory


def test_git_root_and_local_layers_follow_root_to_target_order(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(
        ["git", "init", "--quiet", str(repository)],
        check=True,
        capture_output=True,
    )
    target = repository / "packages" / "one" / "src"
    target.mkdir(parents=True)
    root_layer = repository / ".zpp"
    nested_layer = repository / "packages" / "one" / ".zpp"
    root_layer.mkdir()
    nested_layer.mkdir()

    root = git_worktree_root(target)

    assert root == repository.resolve()
    assert discover_local_layers(
        canonicalize_existing_directory(root),
        canonicalize_existing_directory(target),
    ) == (root_layer, nested_layer)


def test_git_checkout_adapter_uses_exact_commits_and_guards_collisions(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "project"
    repository.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
    (repository / "README.md").write_text("first\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ZPP Test",
            "-c",
            "user.email=zpp@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "first",
        ],
        cwd=repository,
        check=True,
    )

    checkout = inspect_git_checkout(repository / "README.md")
    destination = tmp_path / "project-copy"
    create_git_worktree(
        checkout,
        destination=destination,
        branch="zpp/test-copy",
        start_commit=checkout.head,
    )

    linked = inspect_git_checkout(destination)
    assert linked.head == checkout.head
    assert linked.common_dir == checkout.common_dir
    assert not linked.dirty
    assert git_branch_exists(checkout, "zpp/test-copy")

    with pytest.raises(FileExistsError):
        create_git_worktree(
            checkout,
            destination=destination,
            branch="zpp/other-copy",
            start_commit=checkout.head,
        )
    with pytest.raises(ValueError, match="branch already exists"):
        create_git_worktree(
            checkout,
            destination=tmp_path / "another-copy",
            branch="zpp/test-copy",
            start_commit=checkout.head,
        )

    remove_git_worktree(checkout, destination=destination)
    assert not destination.exists()


def test_git_checkout_adapter_rejects_unborn_repository(tmp_path: Path) -> None:
    repository = tmp_path / "unborn"
    repository.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)

    with pytest.raises(ValueError, match="committed HEAD"):
        inspect_git_checkout(repository)
