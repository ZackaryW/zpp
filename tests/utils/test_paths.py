from pathlib import Path

from zpp.utils.paths import user_zpp_root


def test_user_zpp_root_is_below_the_injected_home(tmp_path: Path) -> None:
    assert user_zpp_root(tmp_path) == tmp_path / ".zpp"
