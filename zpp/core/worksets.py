"""Workset operations: import/sync/bind/status/doctor. Layout truth lives in
the .code-workspace; semantics truth lives in the sidecar."""

import shutil
from pathlib import Path

from . import adapter, sidecar, snapshot
from ..utils import workspace
from ..utils.paths import sidecar_path, worksets_dir


class WorksetError(RuntimeError):
    pass


def derive_name(workspace_file: Path) -> str:
    return workspace_file.stem.lower().replace("_", "-").replace(" ", "-")


def do_import(
    workspace_file: Path, name: str | None = None, partial: bool = False
) -> tuple[str, list[dict]]:
    if not workspace_file.is_file():
        raise WorksetError(f"no such workspace file: {workspace_file}")
    name = name or derive_name(workspace_file)
    if name in adapter.workset_list():
        raise WorksetError(
            f"workset '{name}' already exists - choose --name or remove it first"
        )
    members = workspace.load_members(workspace_file)
    if not members:
        raise WorksetError("workspace file has no folders")
    missing = [m for m in members if not Path(m["path"]).is_dir()]
    if missing and not partial:
        paths = ", ".join(m["path"] for m in missing)
        raise WorksetError(f"missing member folders: {paths} (use --partial to skip)")
    members = [m for m in members if m not in missing]
    if not members:
        raise WorksetError("no member folders exist on this machine")
    snapshot.take(name, "import")
    adapter.workset_create(name, members)
    sidecar.save(name, sidecar.new(workspace_file, members))
    return name, members


def sync_plan(name: str) -> dict:
    """Diff the workspace file against the sidecar. Members are keyed by name;
    labeled folders keep their metadata across path changes. An unlabeled
    disappearance is indistinguishable from remove+add, so dropped bindings
    make the plan destructive."""
    side = sidecar.load(name)
    if side is None:
        raise WorksetError(f"no sidecar for '{name}' - was it imported by zpp?")
    workspace_file = Path(side["workspace"])
    if not workspace_file.is_file():
        raise WorksetError(f"source workspace file moved or deleted: {workspace_file}")
    current = side.get("members", {})
    desired = workspace.load_members(workspace_file)
    desired_names = {m["name"] for m in desired}
    added = [m for m in desired if m["name"] not in current]
    removed = {n: meta for n, meta in current.items() if n not in desired_names}
    moved = [
        m
        for m in desired
        if m["name"] in current and current[m["name"]].get("path") != m["path"]
    ]
    return {
        "workspace": str(workspace_file),
        "desired": desired,
        "added": added,
        "removed": removed,
        "moved": moved,
        "destructive": {
            n: meta for n, meta in removed.items() if "profile" in meta
        },
    }


def sync_apply(name: str, plan: dict) -> None:
    snapshot.take(name, "sync")
    if name in adapter.workset_list():
        adapter.workset_remove(name)
    adapter.workset_create(name, plan["desired"])
    side = sidecar.load(name)
    old_members = side.get("members", {})
    side["members"] = {
        m["name"]: {**old_members.get(m["name"], {}), "path": m["path"]}
        for m in plan["desired"]
    }
    sidecar.save(name, side)


def remove(name: str) -> None:
    if name in adapter.workset_list():
        adapter.workset_remove(name)
    sidecar_path(name).unlink(missing_ok=True)
    shutil.rmtree(worksets_dir() / name, ignore_errors=True)


def status(name: str) -> dict:
    from . import governance

    side = sidecar.load(name)
    if side is None:
        raise WorksetError(f"no sidecar for '{name}'")
    _, pointers, home = sidecar.profiles_and_pointers(side)
    members = []
    for member_name, meta in side.get("members", {}).items():
        path = Path(meta.get("path", ""))
        resolved = governance.resolve(path) if path.is_dir() else {"mode": "unknown", "store": None}
        members.append(
            {
                "name": member_name,
                "path": str(path),
                "exists": path.is_dir(),
                "mode": resolved["mode"],
                "store": resolved.get("store"),
                "profile": pointers.get(member_name) or "default",
                "is_store": adapter.is_store(path),
            }
        )
    return {"name": name, "workspace": side.get("workspace"),
            "home": home, "members": members}


def doctor() -> list[dict]:
    """Drift between zpp and openspec state; each finding carries a fix."""
    findings = []
    openspec_worksets = adapter.workset_list()
    stores = adapter.store_list()
    names = sidecar.list_names()
    for name in names:
        side = sidecar.load(name)
        if name not in openspec_worksets:
            findings.append(
                {
                    "workset": name,
                    "problem": "sidecar has no openspec workset (removed directly?)",
                    "fix": f"zpp workset remove {name}  # or re-import",
                }
            )
        workspace_file = Path(side.get("workspace", ""))
        if not workspace_file.is_file():
            findings.append(
                {
                    "workset": name,
                    "problem": f"source workspace file missing: {workspace_file}",
                    "fix": "restore the file or zpp workset remove",
                }
            )
        profiles, pointers, home = sidecar.profiles_and_pointers(side)
        if home == "shared":
            # correspondence: every shared-file member entry must name a real
            # workspace member - typos are otherwise silently ignored
            for pointer_name in pointers:
                if pointer_name not in side.get("members", {}):
                    findings.append(
                        {
                            "workset": name,
                            "problem": f"shared file names '{pointer_name}', "
                                       f"which is not a member of the workspace",
                            "fix": "fix the member name in the .zpp-workset or add the folder",
                        }
                    )
        for member_name, meta in side.get("members", {}).items():
            member_path = Path(meta.get("path", ""))
            if not member_path.is_dir():
                findings.append(
                    {
                        "workset": name,
                        "problem": f"member '{member_name}' path missing: {meta.get('path')}",
                        "fix": "zpp workset sync",
                    }
                )
            pointer = pointers.get(member_name)
            if pointer and pointer not in profiles:
                findings.append(
                    {
                        "workset": name,
                        "problem": f"member '{member_name}' points at undefined profile '{pointer}'",
                        "fix": f"define [profiles.{pointer}] or drop the pointer",
                    }
                )
            # a repo governed only by a member's multi-workset home
            others = [w for w in sidecar.worksets_containing(member_path) if w != name]
            if others and name == min([name, *others]):
                findings.append(
                    {
                        "workset": name,
                        "problem": f"member '{member_name}' is in multiple worksets "
                                   f"({', '.join(sorted([name, *others]))}); '{name}' wins (first)",
                        "fix": "remove the member from the extra worksets, or accept the winner",
                    }
                )
        for profile_name, cfg in profiles.items():
            store = cfg.get("governance", {}).get("store")
            if store and store not in stores:
                findings.append(
                    {
                        "workset": name,
                        "problem": f"profile '{profile_name}' binds unregistered store '{store}'",
                        "fix": "register the store or fix the profile binding",
                    }
                )
    for name in openspec_worksets:
        if name not in names:
            findings.append(
                {
                    "workset": name,
                    "problem": "openspec workset has no zpp sidecar",
                    "fix": f"zpp workset import <file.code-workspace> --name {name}  # after removing, or leave as zpp-less workset",
                }
            )
    return findings
