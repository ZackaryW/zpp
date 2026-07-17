"""Local undo of zpp-owned state. A camera for config: never touches member
repos, never a distribution mechanism (sharing = commit the .code-workspace)."""

import json
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from ..utils.paths import sidecar_path, snapshots_dir


def take(name: str, trigger: str, note: str | None = None) -> str | None:
    """Snapshot sidecar + current workspace-file text. Returns snapshot id,
    or None when there is no sidecar yet (nothing zpp-owned to protect)."""
    side = sidecar_path(name)
    if not side.is_file():
        return None
    snap_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f")
    snap = snapshots_dir(name) / snap_id
    snap.mkdir(parents=True)
    (snap / "sidecar.toml").write_text(side.read_text())
    meta = {"trigger": trigger, "note": note, "workspace": None}
    workspace = tomllib.loads(side.read_text()).get("workspace")
    if workspace and Path(workspace).is_file():
        (snap / "workspace.code-workspace").write_text(Path(workspace).read_text())
        meta["workspace"] = workspace
    (snap / "meta.json").write_text(json.dumps(meta))
    return snap_id


def list_snapshots(name: str) -> list[dict]:
    root = snapshots_dir(name)
    if not root.is_dir():
        return []
    out = []
    for snap in sorted(root.iterdir()):
        meta_file = snap / "meta.json"
        meta = json.loads(meta_file.read_text()) if meta_file.is_file() else {}
        out.append({"id": snap.name, **meta})
    return out


def restore(name: str, snap_id: str, workspace_file: bool = False) -> list[str]:
    """Rewrite zpp-owned files only; the user-owned .code-workspace is written
    back only on explicit request. Returns the paths written."""
    snap = snapshots_dir(name) / snap_id
    if not snap.is_dir():
        raise FileNotFoundError(f"no snapshot '{snap_id}' for workset '{name}'")
    written = []
    side = sidecar_path(name)
    side.parent.mkdir(parents=True, exist_ok=True)
    side.write_text((snap / "sidecar.toml").read_text())
    written.append(str(side))
    if workspace_file:
        meta = json.loads((snap / "meta.json").read_text())
        target = meta.get("workspace")
        copy = snap / "workspace.code-workspace"
        if target and copy.is_file():
            Path(target).write_text(copy.read_text())
            written.append(target)
    return written
