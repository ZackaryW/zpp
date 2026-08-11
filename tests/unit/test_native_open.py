from pathlib import Path

import pytest

from zpp.utils.native_open import open_directory


@pytest.mark.parametrize(
    ("platform", "executable"),
    [("darwin", "open"), ("win32", "explorer"), ("linux", "xdg-open")],
)
def test_open_directory_launches_native_opener_without_a_shell_command(
    tmp_path: Path,
    platform: str,
    executable: str,
) -> None:
    calls: list[tuple[str, ...]] = []

    open_directory(
        tmp_path,
        platform=platform,
        launch=lambda argv: calls.append(tuple(argv)),
    )

    assert calls == [(executable, str(tmp_path))]


def test_open_directory_propagates_launch_failure(tmp_path: Path) -> None:
    def fail(argv) -> None:
        raise OSError(f"cannot launch {argv[0]}")

    with pytest.raises(OSError, match="cannot launch"):
        open_directory(tmp_path, platform="darwin", launch=fail)
