from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import shutil
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class StagedRemoval:
    original: Path
    tombstone: Path


@dataclass(slots=True)
class RemovalTransaction:
    entries: tuple[StagedRemoval, ...]
    _active: bool = True

    def restore(self) -> None:
        if not self._active:
            return
        conflicts = [entry.original for entry in self.entries if entry.original.exists()]
        if conflicts:
            raise FileExistsError(conflicts[0])
        for entry in reversed(self.entries):
            entry.tombstone.replace(entry.original)
        self._active = False

    def commit(self) -> None:
        if not self._active:
            return
        for entry in self.entries:
            if entry.tombstone.is_dir() and not entry.tombstone.is_symlink():
                shutil.rmtree(entry.tombstone)
            else:
                entry.tombstone.unlink(missing_ok=True)
        self._active = False


def stage_removals(paths: Iterable[Path]) -> RemovalTransaction:
    requested = tuple(dict.fromkeys(paths))
    entries: list[StagedRemoval] = []
    for path in requested:
        if not path.exists() and not path.is_symlink():
            continue
        if path == Path(path.anchor):
            raise ValueError("filesystem roots cannot be staged for removal")
        tombstone = path.with_name(f".{path.name}.zpp-remove-{uuid4().hex}")
        if tombstone.exists() or tombstone.is_symlink():
            raise FileExistsError(tombstone)
        entries.append(StagedRemoval(original=path, tombstone=tombstone))

    staged: list[StagedRemoval] = []
    try:
        for entry in entries:
            entry.original.replace(entry.tombstone)
            staged.append(entry)
    except BaseException:
        for entry in reversed(staged):
            entry.tombstone.replace(entry.original)
        raise
    return RemovalTransaction(tuple(entries))
