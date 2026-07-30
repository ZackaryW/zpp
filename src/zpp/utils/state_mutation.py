from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from zpp.utils.json_io import atomic_write_text
from zpp.utils.models import CreationPlan


def apply_creation_plan(plan: CreationPlan) -> None:
    paths = [entry.path for entry in plan.entries]
    if len(set(paths)) != len(paths):
        raise ValueError("creation plan contains duplicate paths")
    conflicts = [path for path in paths if path.exists() or path.is_symlink()]
    if conflicts:
        raise FileExistsError(conflicts[0])

    created: list[Path] = []
    try:
        for entry in plan.entries:
            if entry.kind == "directory":
                entry.path.mkdir()
            elif entry.kind == "text":
                if entry.source is None:
                    raise ValueError(f"text entry {entry.path} has no source")
                atomic_write_text(entry.path, entry.source)
            else:
                raise ValueError(f"unsupported creation entry kind: {entry.kind}")
            created.append(entry.path)
    except BaseException:
        for path in reversed(created):
            with suppress(OSError):
                if path.is_dir() and not path.is_symlink():
                    path.rmdir()
                else:
                    path.unlink(missing_ok=True)
        raise
