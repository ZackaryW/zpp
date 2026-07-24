"""openspec adapter: the only module that talks to the openspec CLI or its
on-disk conventions. If upstream reshapes worksets, only this file changes."""

import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse


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


def _run_json(args: list[str]):
    """_run + parse. Non-JSON output (e.g. a first-run notice) becomes an
    OpenspecError so callers degrade rather than crash on JSONDecodeError."""
    out = _run(args)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise OpenspecError(f"openspec {' '.join(args)} did not return JSON")


def store_list() -> dict[str, str]:
    """Registered stores: id -> root path. Read-only."""
    data = _run_json(["store", "list", "--json"])
    return {s["id"]: s["root"] for s in data.get("stores", [])}


def workset_list() -> dict[str, list[dict]]:
    """Saved worksets: name -> members [{name, path}]."""
    data = _run_json(["workset", "list", "--json"])
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


# --- Git identity (read-only, best effort) ---


def _git(path: Path, *args: str) -> str | None:
    """Return Git output for a checkout, or None when it is not available."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def normalize_git_remote(remote: str) -> str:
    """Normalize the usual HTTPS and SSH spellings of one Git remote."""
    remote = remote.strip().rstrip("/")
    if remote.endswith(".git"):
        remote = remote[:-4]
    if "://" in remote:
        parsed = urlparse(remote)
        host = (parsed.hostname or "").lower()
        path = parsed.path.strip("/")
        return f"{host}/{path}"
    if ":" in remote and not remote.startswith("/"):
        host, path = remote.rsplit(":", 1)
        return f"{host.rsplit('@', 1)[-1].lower()}/{path.strip('/')}"
    return remote


def git_identity(path: Path) -> dict[str, str] | None:
    """Stable identities for clone/worktree membership reconciliation."""
    common_dir = _git(path, "rev-parse", "--git-common-dir")
    if common_dir is None:
        return None
    common_path = Path(common_dir)
    if not common_path.is_absolute():
        common_path = (path / common_path).resolve()
    remote = _git(path, "config", "--get", "remote.origin.url")
    identity = {"common_dir": str(common_path)}
    if remote:
        identity["remote"] = normalize_git_remote(remote)
    return identity


def git_branch(path: Path) -> str | None:
    """The checked-out branch, never creating or changing Git state."""
    branch = _git(path, "symbolic-ref", "--quiet", "--short", "HEAD")
    return branch or None


def git_default_branch(path: Path) -> str | None:
    """The store default branch from ``origin/HEAD``, if the remote exposes it."""
    ref = _git(path, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if not ref or not ref.startswith("refs/remotes/origin/"):
        return None
    return ref.removeprefix("refs/remotes/origin/")


def git_default_ref(path: Path) -> str | None:
    branch = git_default_branch(path)
    return f"origin/{branch}" if branch else None


def git_run(path: Path, *args: str) -> None:
    """Run a mutating Git command and surface its diagnostic as OpenspecError."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), *args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        raise OpenspecError("git not found on PATH")
    if proc.returncode != 0:
        raise OpenspecError(proc.stderr.strip() or proc.stdout.strip() or "git command failed")


def git_has_local_branch(path: Path, branch: str) -> bool:
    return _git(path, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}") is not None


def git_ref_exists(path: Path, ref: str) -> bool:
    return _git(path, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") is not None
