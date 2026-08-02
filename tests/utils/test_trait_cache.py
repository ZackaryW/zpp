import json
import os
from pathlib import Path

from zpp.utils.trait_cache import (
    trait_cache_is_current,
    write_trait_cache_watchfile,
)


def test_trait_cache_requires_a_certified_cache_generation(tmp_path: Path) -> None:
    traits_directory = tmp_path / "traits"
    traits_directory.mkdir()
    (traits_directory / "alpha.md").write_text("alpha", encoding="utf-8")
    cache = tmp_path / "cached" / "traits.json"
    cache.parent.mkdir()
    cache.write_text("{}\n", encoding="utf-8")
    watchfile = cache.with_name("traits.watch.json")

    assert trait_cache_is_current(traits_directory, cache, watchfile) is False

    write_trait_cache_watchfile(cache, watchfile)

    assert trait_cache_is_current(traits_directory, cache, watchfile) is True


def test_trait_cache_expires_for_malformed_mismatched_or_newer_state(
    tmp_path: Path,
) -> None:
    traits_directory = tmp_path / "traits"
    traits_directory.mkdir()
    source = traits_directory / "alpha.md"
    source.write_text("alpha", encoding="utf-8")
    cache = tmp_path / "cached" / "traits.json"
    cache.parent.mkdir()
    cache.write_text("{}\n", encoding="utf-8")
    watchfile = cache.with_name("traits.watch.json")

    watchfile.write_text("not-json", encoding="utf-8")
    assert trait_cache_is_current(traits_directory, cache, watchfile) is False

    watchfile.write_text(
        json.dumps({"cache_mtime_ns": cache.stat().st_mtime_ns + 1}),
        encoding="utf-8",
    )
    assert trait_cache_is_current(traits_directory, cache, watchfile) is False

    write_trait_cache_watchfile(cache, watchfile)
    newer = cache.stat().st_mtime_ns + 1_000_000_000
    os.utime(source, ns=(newer, newer))
    assert trait_cache_is_current(traits_directory, cache, watchfile) is False
