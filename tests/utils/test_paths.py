from datetime import datetime
from pathlib import Path
import re

from zpp.utils.paths import next_global_archive_name, user_zpp_root


def test_user_zpp_root_is_below_the_injected_home(tmp_path: Path) -> None:
    assert user_zpp_root(tmp_path) == tmp_path / ".zpp"


def test_global_archive_names_use_the_accepted_base_and_avoid_collisions() -> None:
    when = datetime(2026, 7, 30, 14, 35, 22)

    assert next_global_archive_name(when, ()) == "20260730-143522-global"

    occupied = frozenset(
        {
            "20260730-143522-global",
            "20260730-143522-global-1",
        }
    )
    selected = next_global_archive_name(when, occupied)

    assert selected not in occupied
    assert re.fullmatch(r"20260730-143522-global-\d+", selected)
    assert occupied == {
        "20260730-143522-global",
        "20260730-143522-global-1",
    }
