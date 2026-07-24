"""Provisioning for branch-isolated governance checkouts."""

from pathlib import Path

from . import adapter, sidecar
from ..utils.paths import governance_worktrees_dir


class IsolationError(RuntimeError):
    pass


def _store_member(workset: str) -> dict:
    side = sidecar.load(workset)
    if side is None:
        raise IsolationError(f"unknown workset: {workset}")
    stores = [
        {"name": name, "path": meta["path"]}
        for name, meta in side.get("members", {}).items()
        if meta.get("path") and adapter.is_store(Path(meta["path"]))
    ]
    if len(stores) != 1:
        raise IsolationError("workset must contain exactly one dedicated store")
    return stores[0]


def _owned_path(workset: str, member: str, project_branch: str) -> Path:
    candidate = governance_worktrees_dir(workset) / member / project_branch
    root = governance_worktrees_dir(workset).resolve()
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise IsolationError("derived governance checkout escapes zpp-owned path")
    return resolved


def provision(
    workset: str,
    project: Path,
    *,
    member_override: str | None = None,
    branch_override: str | None = None,
    base_override: str | None = None,
    checkout_override: Path | None = None,
) -> dict:
    """Create/reuse one isolated store worktree after all safety preflights."""
    try:
        member = sidecar.resolve_member(project, member_override)
    except sidecar.MemberResolutionError as exc:
        raise IsolationError(str(exc))
    if not member or member["workset"] != workset:
        raise IsolationError("project checkout is not a member of this workset")
    store = _store_member(workset)
    if member["member"] == store["name"]:
        raise IsolationError("the dedicated store cannot provision itself")
    project_branch = adapter.git_branch(project)
    if not project_branch:
        raise IsolationError("project checkout is detached or not a Git branch")
    branch = branch_override or f"{member['member']}/{project_branch}"
    base = base_override or adapter.git_default_ref(Path(store["path"]))
    if not base:
        raise IsolationError("store origin/HEAD is unavailable; pass --base <ref>")
    checkout = Path(checkout_override).resolve() if checkout_override else _owned_path(
        workset, member["member"], project_branch
    )
    if checkout_override is None and not checkout.is_relative_to(governance_worktrees_dir(workset).resolve()):
        raise IsolationError("governance checkout must remain under zpp-owned state")
    if checkout.exists():
        existing_branch = adapter.git_branch(checkout)
        if existing_branch != branch:
            raise IsolationError(f"existing checkout is on '{existing_branch}', expected '{branch}'")
        return {"workset": workset, "member": member["member"], "project_branch": project_branch,
                "governance_branch": branch, "base": base, "effective_root": str(checkout), "reused": True}
    if not adapter.git_ref_exists(Path(store["path"]), base):
        raise IsolationError(f"base ref does not exist: {base}; pass --base <ref>")

    # All validation above is read-only. The first mutation is the Git worktree add.
    checkout.parent.mkdir(parents=True, exist_ok=True)
    existing = adapter.git_has_local_branch(Path(store["path"]), branch)
    try:
        if existing:
            adapter.git_run(Path(store["path"]), "worktree", "add", str(checkout), branch)
        else:
            adapter.git_run(Path(store["path"]), "worktree", "add", "-b", branch, str(checkout), base)
    except adapter.OpenspecError as exc:
        raise IsolationError(str(exc))
    return {"workset": workset, "member": member["member"], "project_branch": project_branch,
            "governance_branch": branch, "base": base, "effective_root": str(checkout), "reused": False}


def open_session(project: Path, *, tool: str | None = None, **overrides) -> dict:
    """Provision then open a zpp-owned OpenSpec workset view for this session."""
    try:
        member = sidecar.resolve_member(project, overrides.get("member_override"))
    except sidecar.MemberResolutionError as exc:
        raise IsolationError(str(exc))
    if not member:
        raise IsolationError("project checkout is not a known workset member")
    provisioned = provision(member["workset"], project, **overrides)
    side = sidecar.load(member["workset"]) or {}
    store = _store_member(member["workset"])
    session_name = f"{member['workset']}--{member['member']}--{provisioned['project_branch']}"
    members = []
    for name, meta in side.get("members", {}).items():
        path = meta["path"]
        if name == member["member"]:
            path = str(Path(project).resolve())
        elif name == store["name"]:
            path = provisioned["effective_root"]
        members.append({"name": name, "path": path})
    known = adapter.workset_list()
    if session_name not in known:
        adapter.workset_create(session_name, members)
    side.setdefault("sessions", {})[session_name] = {
        "member": member["member"],
        "project_path": str(Path(project).resolve()),
        "store_path": store["path"],
        "governance_branch": provisioned["governance_branch"],
        "effective_root": provisioned["effective_root"],
        "generated_checkout": overrides.get("checkout_override") is None,
    }
    sidecar.save(member["workset"], side)
    adapter.workset_open(session_name, tool)
    return {**provisioned, "session_view": session_name}


def cleanup_session(session_name: str) -> dict:
    """Remove only a recorded zpp session view and its generated worktree."""
    for workset in sidecar.list_names():
        side = sidecar.load(workset) or {}
        session = side.get("sessions", {}).get(session_name)
        if not session:
            continue
        known = adapter.workset_list()
        if session_name in known:
            adapter.workset_remove(session_name)
        effective_root = Path(session["effective_root"]).resolve()
        owned_root = governance_worktrees_dir(workset).resolve()
        if session.get("generated_checkout") and effective_root.is_relative_to(owned_root):
            if effective_root.exists():
                try:
                    adapter.git_run(
                        Path(session["store_path"]), "worktree", "remove", str(effective_root)
                    )
                except adapter.OpenspecError as exc:
                    raise IsolationError(str(exc))
        del side["sessions"][session_name]
        sidecar.save(workset, side)
        return {"session_view": session_name, "removed": True}
    return {"session_view": session_name, "removed": False}
