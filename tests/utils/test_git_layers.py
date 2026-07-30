from pathlib import Path
import subprocess

from zpp.utils.git_layers import discover_local_layers, git_worktree_root
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
