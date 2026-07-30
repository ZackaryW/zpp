from pathlib import Path

from zpp.utils.removals import stage_removals


def test_staged_removals_restore_or_commit_owned_paths_only(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    cache = tmp_path / "cache"
    unmanaged = tmp_path / "unmanaged.txt"
    profile.mkdir()
    cache.mkdir()
    (profile / "trait.json").write_text("[]\n", encoding="utf-8")
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    unmanaged.write_text("keep", encoding="utf-8")

    staged = stage_removals((profile, tmp_path / "missing", cache))
    assert not profile.exists() and not cache.exists()
    assert all(item.tombstone.exists() for item in staged.entries)

    staged.restore()
    assert profile.is_dir() and cache.is_dir()
    assert unmanaged.read_text(encoding="utf-8") == "keep"

    committed = stage_removals((profile, cache))
    committed.commit()
    assert not profile.exists() and not cache.exists()
    assert all(not item.tombstone.exists() for item in committed.entries)
    assert unmanaged.read_text(encoding="utf-8") == "keep"
