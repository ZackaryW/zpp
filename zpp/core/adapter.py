"""openspec adapter: the only module that talks to the openspec CLI or its
on-disk conventions. If upstream reshapes worksets, only this file changes."""

import json
import subprocess
from pathlib import Path


class OpenspecError(RuntimeError):
    pass


def _run(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["openspec", *args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        raise OpenspecError("openspec CLI not found on PATH (run: zpp bootstrap)")
    if proc.returncode != 0:
        raise OpenspecError(
            f"openspec {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def store_list() -> dict[str, str]:
    """Registered stores: id -> root path. Read-only."""
    data = json.loads(_run(["store", "list", "--json"]))
    return {s["id"]: s["root"] for s in data.get("stores", [])}


def workset_list() -> dict[str, list[dict]]:
    """Saved worksets: name -> members [{name, path}]."""
    data = json.loads(_run(["workset", "list", "--json"]))
    worksets = data.get("worksets", data) if isinstance(data, dict) else data
    if isinstance(worksets, list):  # tolerate list-shaped output
        return {w["name"]: w.get("members", []) for w in worksets}
    return {name: w.get("members", []) for name, w in worksets.items()}


def workset_create(name: str, members: list[dict]) -> None:
    """members: [{name, path}] with absolute paths; first is primary."""
    args = ["workset", "create", name, "--json"]
    for m in members:
        args += ["--member", f"{m['name']}={m['path']}"]
    _run(args)


def workset_remove(name: str) -> None:
    _run(["workset", "remove", name, "--yes"])


def workset_open(name: str, tool: str | None = None) -> None:
    args = ["workset", "open", name]
    if tool:
        args += ["--tool", tool]
    _run(args)


# --- on-disk detection (openspec conventions, read-only) ---


def find_openspec_root(path: Path) -> Path | None:
    """Ancestor walk for a local openspec/ root (openspec's native rule)."""
    for p in (path.resolve(), *path.resolve().parents):
        if (p / "openspec").is_dir():
            return p
    return None


def is_store(path: Path) -> bool:
    return (path / ".openspec-store" / "store.yaml").is_file()
