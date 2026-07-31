from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
import json
from pathlib import Path

from filelock import FileLock
from pydantic import ValidationError

from zpp.utils.codespace_models import CodespaceIndex
from zpp.utils.json_io import atomic_write_json


INDEX_NAME = "index.json"
LOCK_NAME = "index.lock"


@contextmanager
def codespace_index_lock(
    lock_path: Path,
    *,
    timeout: float = 0,
) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(lock_path, timeout=timeout):
        yield


def load_codespace_index(root: Path) -> CodespaceIndex:
    index_path = root / INDEX_NAME
    if not index_path.exists():
        return CodespaceIndex()
    try:
        value = json.loads(index_path.read_text(encoding="utf-8"))
        return CodespaceIndex.model_validate(value)
    except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as error:
        raise ValueError(f"{index_path} contains an invalid codespace index") from error


def mutate_codespace_index(
    root: Path,
    transform: Callable[[CodespaceIndex], CodespaceIndex],
) -> CodespaceIndex:
    root.mkdir(parents=True, exist_ok=True)
    with codespace_index_lock(root / LOCK_NAME):
        current = load_codespace_index(root)
        candidate = transform(current)
        if not isinstance(candidate, CodespaceIndex):
            raise TypeError("codespace index transform must return CodespaceIndex")
        updated = CodespaceIndex.model_validate(candidate.model_dump(mode="json"))
        atomic_write_json(root / INDEX_NAME, updated.model_dump(mode="json"))
        return updated
