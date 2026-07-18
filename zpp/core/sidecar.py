"""Machine-local sidecar plus workset config profiles.

The sidecar (~/.zpp/worksets/<name>.toml) holds machine-local state - the
workspace path and each member's resolved path. Config profiles (named
zpp.toml-shaped blocks) and member->profile pointers live either in the
sidecar (personal) or in a committed <stem>.zpp-workset file beside the
.code-workspace (shared). The shared file, when present, wins entirely."""

import os
import tomllib
from pathlib import Path

import tomli_w

from ..utils.paths import sidecar_path, worksets_dir

WORKSPACE_SUFFIX = ".code-workspace"
SHARED_SUFFIX = ".zpp-workset"


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
        "version": 2,
        "workspace": str(workspace_file.resolve()),
        "members": {m["name"]: {"path": m["path"]} for m in members},
        "profiles": {},
    }


def list_names() -> list[str]:
    if not worksets_dir().is_dir():
        return []
    return sorted(p.stem for p in worksets_dir().glob("*.toml"))


# --- profiles: shared .zpp-workset file wins over the personal sidecar ---


def shared_file_path(workspace_file: Path) -> Path:
    stem = workspace_file.name.removesuffix(WORKSPACE_SUFFIX)
    return workspace_file.parent / f"{stem}{SHARED_SUFFIX}"


def profiles_and_pointers(side: dict) -> tuple[dict, dict, str]:
    """(profiles, member->profile pointers, home). The shared file, when it
    exists beside the workspace file, is the source of truth for both."""
    shared = shared_file_path(Path(side["workspace"]))
    if shared.is_file():
        data = tomllib.loads(shared.read_text())
        pointers = {n: m.get("profile") for n, m in data.get("members", {}).items()}
        return data.get("profiles", {}), pointers, "shared"
    pointers = {n: m.get("profile") for n, m in side.get("members", {}).items()}
    return side.get("profiles", {}), pointers, "sidecar"


def _members_containing(path: Path) -> list[tuple[str, str, str]]:
    """(workset, member, member_path) for every workset member whose path
    contains `path`, worksets in name order (list_names is sorted)."""
    resolved = path.resolve()
    hits = []
    for name in list_names():
        side = load(name)
        for member, meta in (side or {}).get("members", {}).items():
            mp = meta.get("path")
            if mp and resolved.is_relative_to(Path(mp).resolve()):
                hits.append((name, member, mp))
    return hits


def worksets_containing(path: Path) -> list[str]:
    return [name for name, _, _ in _members_containing(path)]


def resolved_profile(path: Path) -> dict | None:
    """The member's resolved profile for `path`: the alphabetically-first
    containing workset wins. Returns {workset, member, member_path, profile,
    config, home} or None when `path` is not a workset member."""
    hits = _members_containing(path)
    if not hits:
        return None
    name, member, member_path = hits[0]
    profiles, pointers, home = profiles_and_pointers(load(name))
    profile_name = pointers.get(member) or "default"
    return {
        "workset": name, "member": member, "member_path": member_path,
        "profile": profile_name,
        "config": profile_config(profiles, profile_name),
        "home": home,
    }


def profile_config(profiles: dict, name: str) -> dict:
    """A profile's config with one-level `extends` resolved: the parent's
    config merged under the child's (child wins; the parent's own extends is
    deliberately ignored - no chains)."""
    cfg = {k: v for k, v in profiles.get(name, {}).items() if k != "extends"}
    parent_name = profiles.get(name, {}).get("extends")
    if not parent_name or parent_name not in profiles:
        return cfg
    from . import governance

    parent = {k: v for k, v in profiles[parent_name].items() if k != "extends"}
    return governance._merge(parent, cfg, "profile", {})
