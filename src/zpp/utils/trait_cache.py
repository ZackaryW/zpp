from __future__ import annotations

import json
from pathlib import Path

from zpp.utils.control_documents import validate_cache_watch
from zpp.utils.json_io import atomic_write_json
from zpp.utils.models import ZppValidationError


def trait_cache_is_current(
    traits_directory: Path,
    cache: Path,
    watchfile: Path,
) -> bool:
    try:
        if not traits_directory.is_dir() or not cache.is_file() or not watchfile.is_file():
            return False

        watch = validate_cache_watch(
            json.loads(watchfile.read_text(encoding="utf-8"))
        )
        cache_timestamp = cache.stat().st_mtime_ns
        if watch.cache_mtime_ns != cache_timestamp:
            return False
        if traits_directory.stat().st_mtime_ns > cache_timestamp:
            return False

        return all(
            source.stat().st_mtime_ns <= cache_timestamp
            for source in traits_directory.iterdir()
            if source.suffix == ".md"
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ZppValidationError):
        return False


def write_trait_cache_watchfile(cache: Path, watchfile: Path) -> None:
    atomic_write_json(
        watchfile,
        {"cache_mtime_ns": cache.stat().st_mtime_ns},
    )
