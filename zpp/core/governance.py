"""Four-mode governance resolution and layered config.

zpp reads its own protocol files - repo zpp.toml, store zpp.default.toml.
(pva.toml remains compose.py's file; zpp does not read it.)

Modes, first hit wins:
  1. local openspec/ root in ancestry  -> self-governed
  2. in-repo zpp.toml binding          -> externally governed (committed fact)
  3. workset sidecar binding           -> externally governed (personal view)
  4. none                              -> ungoverned (explicit, not an error)
"""

import os
import tomllib
from pathlib import Path

from . import adapter, sidecar
from ..utils.paths import governance_worktrees_dir


def _repo_binding(path: Path) -> tuple[Path, str] | None:
    """Nearest ancestor zpp.toml declaring [governance] store = "id"."""
    for p in (path.resolve(), *path.resolve().parents):
        cfg = p / "zpp.toml"
        if cfg.is_file():
            store = tomllib.loads(cfg.read_text()).get("governance", {}).get("store")
            if store:
                return p, store
    return None


def _stores_or_warn(result: dict) -> dict[str, str]:
    """Registry read that degrades when the openspec CLI is unavailable -
    resolution classifies without it, it just can't validate store ids."""
    try:
        return adapter.store_list()
    except adapter.OpenspecError:
        result.setdefault("warnings", []).append(
            "openspec CLI unavailable - store ids not validated"
        )
        return {}


def resolve(path: Path) -> dict:
    result = {"path": str(path.resolve()), "mode": "ungoverned", "rule": None,
              "store": None, "warnings": []}
    root = adapter.find_openspec_root(path)
    if root is not None:
        result |= {"mode": "self-governed", "rule": 1, "root": str(root)}
        return _with_isolation(path, result, None, {})
    stores = _stores_or_warn(result)
    repo = _repo_binding(path)
    if repo is not None:
        repo_root, store = repo
        result |= {"mode": "externally-governed", "rule": 2, "store": store,
                   "binding": "committed", "root": str(repo_root)}
        if store not in stores:
            result["warnings"].append(f"dangling store: '{store}' is not registered")
        return _with_isolation(path, result, sidecar.resolved_profile(path), stores)
    prof = sidecar.resolved_profile(path)
    if prof is not None:
        store = prof["config"].get("governance", {}).get("store")
        if store:
            result |= {"mode": "externally-governed", "rule": 3, "store": store,
                       "binding": "profile", "workset": prof["workset"],
                       "member": prof["member"], "profile": prof["profile"]}
            if store not in stores:
                result["warnings"].append(f"dangling store: '{store}' is not registered")
            return _with_isolation(path, result, prof, stores)
    return _with_isolation(path, result, prof, stores)


def _reference_entries(side: dict, result: dict, stores: dict[str, str]) -> list[dict]:
    """Reference stores assigned to the containing workset, as {id, root}.

    Least privilege: the registry is read only when something is assigned, so
    an unassigned workset costs no registry access. An unregistered id keeps a
    null root - doctor reports it; resolution does not fail on it.
    """
    assigned = sidecar.reference_store_ids(side)
    if not assigned:
        return []
    known = stores or _stores_or_warn(result)
    return [{"id": store_id, "root": known.get(store_id)} for store_id in assigned]


def _with_isolation(path: Path, result: dict, prof: dict | None, stores: dict[str, str]) -> dict:
    """Attach a read-only branch-isolation result for a store-backed workset."""
    try:
        membership = sidecar.resolve_member(path)
    except sidecar.MemberResolutionError as exc:
        return {**result, "reference_stores": [],
                "isolation": {"state": "ambiguous-member", "error": str(exc)}}
    if not membership:
        return {**result, "reference_stores": []}
    side = sidecar.load(membership["workset"]) or {}
    result = {**result, "reference_stores": _reference_entries(side, result, stores)}
    store_members = [
        {"name": name, "path": meta["path"]}
        for name, meta in side.get("members", {}).items()
        if meta.get("path") and adapter.is_store(Path(meta["path"]))
    ]
    if len(store_members) > 1:
        return {**result, "isolation": {
            "state": "invalid-workset",
            "reason": "multiple-dedicated-stores",
            "workset": membership["workset"],
            "stores": [member["name"] for member in store_members],
            "remediation": "keep one .openspec-store member or split the workset",
        }}
    if len(store_members) != 1 or membership["member"] == store_members[0]["name"]:
        return result

    store_member = store_members[0]
    base_root = Path(store_member["path"]).resolve()
    store_id = result.get("store")
    if not store_id:
        store_id = next((key for key, value in stores.items() if Path(value).resolve() == base_root), None)
    project_branch = adapter.git_branch(path)
    if not project_branch:
        return {**result, "isolation": {
            "state": "invalid-project-checkout",
            "reason": "detached-or-non-git-head",
            "member": membership["member"],
            "remediation": "run from a checked-out project branch or use zpp workset open --branch",
        }}
    governance_branch = f"{membership['member']}/{project_branch}"
    effective_root = governance_worktrees_dir(membership["workset"]) / membership["member"] / project_branch
    context = {
        "state": "ready" if effective_root.is_dir() else "provisioning-required",
        "workset": membership["workset"],
        "member": membership["member"],
        "member_match": membership["match"],
        "project_branch": project_branch,
        "governance_branch": governance_branch,
        "store": store_id,
        "base_root": str(base_root),
        "effective_root": str(effective_root),
    }
    if context["state"] == "provisioning-required":
        context["remediation"] = f"zpp workset open {membership['workset']} --project {Path(path).resolve()}"
    governed = result
    if store_id and result.get("store") is None:
        governed = {**result, "mode": "externally-governed", "rule": 3,
                    "store": store_id, "binding": "dedicated-store"}
    return {**governed, "isolation": context}


# --- layered config: repo zpp.toml -> member profile -> store zpp.default.toml ---


def _merge(base: dict, over: dict, source: str, origins: dict, prefix: str = "") -> dict:
    """Scalars override, lists union, dicts recurse. origins records the
    winning layer per key path."""
    out = dict(base)
    for key, value in over.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value, source, origins, f"{path}.")
        elif isinstance(value, list) and isinstance(out.get(key), list):
            out[key] = out[key] + [v for v in value if v not in out[key]]
            origins[path] = f"{origins.get(path, '?')}+{source}"
        else:
            out[key] = value
            # record leaf origins even when an upper tier introduces a whole
            # section the base lacked, so origins stay complete
            if isinstance(value, dict):
                _record_origins(value, source, origins, f"{path}.")
            else:
                origins[path] = source
    return out


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text()) if path.is_file() else {}


def _store_published(root: Path) -> dict:
    """What a store publishes to the repos it governs: its zpp.toml's
    `default` profile (extends-resolved). There is no zpp.default.toml -
    default is a profile, at the store tier like everywhere else."""
    profiles = _load_toml(root / "zpp.toml").get("profiles", {})
    return sidecar.profile_config(profiles, "default")


def _repo_tier(root: Path) -> dict:
    """A repo's own committed config: zpp.toml top-level, minus the profiles
    it publishes (those are the store tier, never the repo's self-config)."""
    return {k: v for k, v in _load_toml(root / "zpp.toml").items() if k != "profiles"}


def _record_origins(data: dict, source: str, origins: dict, prefix: str = "") -> None:
    for key, value in data.items():
        if isinstance(value, dict):
            _record_origins(value, source, origins, f"{prefix}{key}.")
        else:
            origins[f"{prefix}{key}"] = source


def resolve_config(path: Path) -> dict:
    """Effective config with per-value source attribution."""
    mode = resolve(path)
    origins: dict[str, str] = {}
    # Middle tier applies by workset MEMBERSHIP, independent of governance mode:
    # a self-governed or committed-bound member still gets its workset profile.
    prof = sidecar.resolved_profile(path)
    isolation = mode.get("isolation", {})
    if isolation.get("state") == "ready":
        store_default = _store_published(Path(isolation["effective_root"]))
        repo_root = Path(mode.get("root") or (prof and prof["member_path"]) or path)
    elif isolation.get("state") == "provisioning-required":
        # A recognized isolated session must never consume the registered base
        # checkout while waiting for provisioning.
        store_default = {}
        repo_root = Path(mode.get("root") or (prof and prof["member_path"]) or path)
    elif mode["mode"] == "self-governed":
        store_default = _store_published(Path(mode["root"]))
        repo_root = Path(mode["root"])
    else:
        stores = _stores_or_warn(mode)
        store_root = stores.get(mode.get("store") or "")
        store_default = _store_published(Path(store_root)) if store_root else {}
        repo_root = Path(mode.get("root") or (prof and prof["member_path"]) or path)
    repo_cfg = _repo_tier(repo_root)
    profile_cfg = dict(prof["config"]) if prof else {}
    tier_source = "workset"
    if "ZPP_TRAITS" in os.environ:
        # Per-session override: replaces the workset (profile) tier ONLY
        # (mirrors the PVA_ALLOW_NO_STORE ephemeral-bypass doctrine); committed
        # tiers always survive, so discipline lives in store/repo config.
        names = [n.strip() for n in os.environ["ZPP_TRAITS"].split(",") if n.strip()]
        profile_cfg = {"traits": {"apply": names}}
        tier_source = "env"
    _record_origins(store_default, "store", origins)
    effective = _merge(store_default, profile_cfg, tier_source, origins)
    effective = _merge(effective, repo_cfg, "repo", origins)
    return {
        "mode": mode,
        "effective": effective,
        "origins": origins,
        "layers": {"store": store_default, tier_source: profile_cfg, "repo": repo_cfg},
    }
