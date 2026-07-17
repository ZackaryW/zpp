"""Four-mode governance resolution and layered config.

zpp reads its own protocol files - repo zpp.toml, store zpp.default.toml.
(pva.toml remains compose.py's file; zpp does not read it.)

Modes, first hit wins:
  1. local openspec/ root in ancestry  -> self-governed
  2. in-repo zpp.toml binding          -> externally governed (committed fact)
  3. workset sidecar binding           -> externally governed (personal view)
  4. none                              -> ungoverned (explicit, not an error)
"""

import tomllib
from pathlib import Path

from . import adapter, sidecar


def _repo_binding(path: Path) -> tuple[Path, str] | None:
    """Nearest ancestor zpp.toml declaring [governance] store = "id"."""
    for p in (path.resolve(), *path.resolve().parents):
        cfg = p / "zpp.toml"
        if cfg.is_file():
            store = tomllib.loads(cfg.read_text()).get("governance", {}).get("store")
            if store:
                return p, store
    return None


def _sidecar_binding(path: Path) -> tuple[str, str, str] | None:
    """(workset, member, store) whose bound member contains path."""
    resolved = path.resolve()
    for name in sidecar.list_names():
        side = sidecar.load(name)
        for member_name, meta in side.get("members", {}).items():
            store = meta.get("store")
            if store and resolved.is_relative_to(Path(meta.get("path", "/\0"))):
                return name, member_name, store
    return None


def resolve(path: Path) -> dict:
    result = {"path": str(path.resolve()), "mode": "ungoverned", "rule": None,
              "store": None, "warnings": []}
    root = adapter.find_openspec_root(path)
    if root is not None:
        return {**result, "mode": "self-governed", "rule": 1, "root": str(root)}
    stores = adapter.store_list()
    repo = _repo_binding(path)
    if repo is not None:
        repo_root, store = repo
        result |= {"mode": "externally-governed", "rule": 2, "store": store,
                   "binding": "committed", "root": str(repo_root)}
        if store not in stores:
            result["warnings"].append(f"dangling store: '{store}' is not registered")
        return result
    personal = _sidecar_binding(path)
    if personal is not None:
        workset_name, member, store = personal
        result |= {"mode": "externally-governed", "rule": 3, "store": store,
                   "binding": "personal", "workset": workset_name, "member": member}
        if store not in stores:
            result["warnings"].append(f"dangling store: '{store}' is not registered")
        return result
    return result


# --- layered config: repo zpp.toml -> sidecar overlay -> store zpp.default.toml ---


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
            origins[path] = source
    return out


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text()) if path.is_file() else {}


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
    if mode["mode"] == "self-governed":
        store_default = _load_toml(Path(mode["root"]) / "zpp.default.toml")
        repo_cfg = _load_toml(Path(mode["root"]) / "zpp.toml")
        overlay = {}
    else:
        stores = adapter.store_list()
        store_root = stores.get(mode.get("store") or "")
        store_default = _load_toml(Path(store_root) / "zpp.default.toml") if store_root else {}
        repo_root = Path(mode.get("root", path))
        repo_cfg = _load_toml(repo_root / "zpp.toml")
        side = sidecar.load(mode["workset"]) if mode.get("workset") else None
        overlay = (side or {}).get("overlay", {})
    _record_origins(store_default, "store", origins)
    effective = _merge(store_default, overlay, "workset", origins)
    effective = _merge(effective, repo_cfg, "repo", origins)
    return {"mode": mode, "effective": effective, "origins": origins}
