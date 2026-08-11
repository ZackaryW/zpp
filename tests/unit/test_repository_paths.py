from pathlib import Path, PurePosixPath

import pytest

from zpp.utils.repository_paths import (
    RepositoryPathError,
    glob_full_match,
    normalize_repository_path,
    resolve_repository_file,
    validate_repository_glob,
)


def test_normalizes_one_repository_relative_posix_path() -> None:
    assert normalize_repository_path("tools/task") == PurePosixPath("tools/task")


@pytest.mark.parametrize(
    "value",
    ["", "\x00bad", "/absolute", "C:/absolute", "nested\\windows", "../escape"],
)
def test_rejects_values_outside_repository_path_vocabulary(value: str) -> None:
    with pytest.raises(RepositoryPathError):
        normalize_repository_path(value)


def test_accepts_one_bounded_repository_glob() -> None:
    assert validate_repository_glob("src/**/*.py") == "src/**/*.py"


@pytest.mark.parametrize(
    ("path", "pattern", "expected"),
    [
        ("src/zpp/core.py", "src/**/*.py", True),
        ("src/core.py", "src/**/*.py", True),
        ("features/core/main.feature", "features/*/*.feature", True),
        ("features/core/nested/main.feature", "features/*/*.feature", False),
    ],
)
def test_repository_globs_match_the_complete_path(
    path: str, pattern: str, expected: bool
) -> None:
    assert glob_full_match(path, pattern) is expected


@pytest.mark.parametrize(
    "pattern",
    ["", "/**/*.py", "../**", "src\\**\\*.py", "src//*.py", "src/[abc/*.py"],
)
def test_rejects_unsafe_or_unbalanced_repository_globs(pattern: str) -> None:
    with pytest.raises(RepositoryPathError):
        validate_repository_glob(pattern)


def test_resolves_an_existing_nested_repository_file(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    wrapper = root / "tools" / "task"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text("wrapper")

    assert resolve_repository_file(root, "tools/task") == wrapper.resolve()


def test_rejects_a_symlink_that_escapes_the_repository(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.write_text("outside")
    link = root / "task"
    try:
        link.symlink_to(outside)
    except OSError as error:
        pytest.skip(f"symlinks are unavailable: {error}")

    with pytest.raises(RepositoryPathError):
        resolve_repository_file(root, "task")
