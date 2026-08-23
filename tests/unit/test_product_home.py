from pathlib import Path

import pytest

from zpp.utils.product_home import (
    PreparedBundlerState,
    ZppHome,
    selected_zpp_home,
    validate_reset_boundary,
)


def test_selected_default_home_derives_bundler_child_without_creation(
    tmp_path: Path,
) -> None:
    user_home = tmp_path / "user"

    selected = selected_zpp_home(None, user_home=user_home)

    assert selected.path == user_home / ".zpp"
    assert selected.state_root == user_home / ".zpp" / "bundler"
    assert not selected.path.exists()


def test_selected_custom_home_is_normalized_without_following_symlinks(
    tmp_path: Path,
) -> None:
    custom = tmp_path / "parent" / ".." / "zpp-home"

    selected = selected_zpp_home(custom)

    assert selected.path == tmp_path / "zpp-home"
    assert selected.state_root == tmp_path / "zpp-home" / "bundler"
    assert not selected.path.exists()


@pytest.mark.parametrize("unsafe", [Path("/"), Path("//")])
def test_reset_boundary_rejects_filesystem_root(unsafe: Path) -> None:
    with pytest.raises(ValueError, match="filesystem root"):
        validate_reset_boundary(ZppHome(unsafe))


def test_reset_boundary_rejects_symlinked_home(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)

    with pytest.raises(ValueError, match="symlink"):
        validate_reset_boundary(ZppHome(linked))


def test_reset_boundary_rejects_non_directory_state_child(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    (home / "bundler").write_text("not a directory")

    with pytest.raises(ValueError, match=r"Bundler.*directory"):
        validate_reset_boundary(ZppHome(home))


def test_prepared_state_replaces_only_bundler_child(tmp_path: Path) -> None:
    home_path = tmp_path / "home"
    old_state = home_path / "bundler"
    old_state.mkdir(parents=True)
    (old_state / "old.json").write_text("old")
    sibling = home_path / "notes.txt"
    sibling.write_text("keep")
    prepared = PreparedBundlerState.prepare(ZppHome(home_path))

    prepared.replace()

    assert old_state.is_dir()
    assert [path.name for path in old_state.iterdir()] == ["state.lock"]
    assert sibling.read_text() == "keep"
    assert not prepared.staging_root.exists()


def test_prepared_state_rolls_back_when_staged_swap_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home_path = tmp_path / "home"
    old_state = home_path / "bundler"
    old_state.mkdir(parents=True)
    marker = old_state / "old.json"
    marker.write_text("old")
    prepared = PreparedBundlerState.prepare(ZppHome(home_path))
    original_rename = Path.rename

    def fail_staged_swap(path: Path, target: Path) -> Path:
        if path == prepared.staged_state:
            raise OSError("swap failed")
        return original_rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_staged_swap)

    with pytest.raises(OSError, match="swap failed"):
        prepared.replace()

    assert marker.read_text() == "old"
    assert prepared.staging_root.exists()
    prepared.discard()


def test_discarded_preparation_preserves_existing_state(tmp_path: Path) -> None:
    home_path = tmp_path / "home"
    old_state = home_path / "bundler"
    old_state.mkdir(parents=True)
    marker = old_state / "old.json"
    marker.write_text("old")
    prepared = PreparedBundlerState.prepare(ZppHome(home_path))

    prepared.discard()

    assert marker.read_text() == "old"
    assert not prepared.staging_root.exists()
