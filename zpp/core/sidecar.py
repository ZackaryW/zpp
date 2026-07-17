"""Machine-local sidecar: what openspec's strict workset schema refuses to
hold. Personal by doctrine - never committed, never written into members."""

import os
import tomllib
from pathlib import Path

import tomli_w

from ..utils.paths import sidecar_path, worksets_dir


def load(name: str) -> dict | None:
    path = sidecar_path(name)
    if not path.is_file():
        return None
    return tomllib.loads(path.read_text())


def save(name: str, data: dict) -> None:
    worksets_dir().mkdir(parents=True, exist_ok=True)
    path = sidecar_path(name)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(tomli_w.dumps(data))
    os.replace(tmp, path)


def new(workspace_file: Path, members: list[dict]) -> dict:
    return {
        "version": 1,
        "workspace": str(workspace_file.resolve()),
        "members": {
            m["name"]: {"path": m["path"]} for m in members
        },
    }


def list_names() -> list[str]:
    if not worksets_dir().is_dir():
        return []
    return sorted(p.stem for p in worksets_dir().glob("*.toml"))
