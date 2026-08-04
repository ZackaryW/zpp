import pytest

from zpp.utils.globs import glob_full_match


@pytest.mark.parametrize(
    "path,pattern,expected",
    [
        # `**` matches zero or more segments.
        ("a.py", "**/*.py", True),
        ("src/a.py", "**/*.py", True),
        ("src/nested/a.py", "**/*.py", True),
        ("a.txt", "**/*.py", False),
        # Leading fixed segment followed by `**`.
        ("src/a.py", "src/**/*.py", True),
        ("src/nested/a.py", "src/**/*.py", True),
        ("other/a.py", "src/**/*.py", False),
        # Patterns are anchored to the whole path.
        ("pyproject.toml", "pyproject.toml", True),
        ("nested/pyproject.toml", "pyproject.toml", False),
        # `*` matches within a single segment only.
        ("a.py", "*", True),
        ("a/b.py", "*", False),
        ("a.py", "*.py", True),
        ("a/b.py", "*.py", False),
        # `?` matches a single character within a segment.
        ("a.py", "?.py", True),
        ("ab.py", "?.py", False),
        # Character classes.
        ("a.py", "[ab].py", True),
        ("c.py", "[ab].py", False),
        # A bare `**` matches any path.
        ("a", "**", True),
        ("a/b/c", "**", True),
    ],
)
def test_glob_full_match(path: str, pattern: str, expected: bool) -> None:
    assert glob_full_match(path, pattern) is expected


def test_glob_full_match_matches_pathlib_full_match_when_available() -> None:
    pytest.importorskip("pathlib")
    from pathlib import PurePosixPath

    if not hasattr(PurePosixPath, "full_match"):
        pytest.skip("PurePosixPath.full_match requires Python 3.13+")

    cases = [
        ("a.py", "**/*.py"),
        ("src/nested/a.py", "src/**/*.py"),
        ("pyproject.toml", "pyproject.toml"),
        ("nested/pyproject.toml", "pyproject.toml"),
        ("a/b.py", "*"),
        ("a.py", "[ab].py"),
    ]
    for path, pattern in cases:
        assert glob_full_match(path, pattern) == PurePosixPath(path).full_match(
            pattern
        )
