"""Trait content sources and the effective-set computation.

Four sources, collision precedence user > builtin > plugin > saucepan. The
`plugin` source is gathered live and only when a tool is named (see plugins.py).
A trait is one markdown file, name = filename stem. No composer: content is
served in realtime, never compiled into artifacts."""

import json
import os
from importlib import resources
from pathlib import Path

from . import governance, plugins
from ..utils.paths import zpp_home

PRECEDENCE = ["user", "builtin", "plugin", "saucepan"]


def _builtin_dir() -> Path:
    return Path(str(resources.files("zpp") / "traits"))


def _scan(tool: str | None = None, plugin_override: Path | None = None) -> list[dict]:
    """Every trait file in every source, in precedence order. The plugin source
    is gathered live only when a tool is named. saucepan packs carry version."""
    rows: list[dict] = []
    user_dir = zpp_home() / "user"
    for f in sorted(user_dir.glob("*.md")) if user_dir.is_dir() else []:
        rows.append({"name": f.stem, "source": "user", "path": str(f), "version": None})
    builtin = _builtin_dir()
    for f in sorted(builtin.glob("*.md")) if builtin.is_dir() else []:
        rows.append({"name": f.stem, "source": "builtin", "path": str(f), "version": None})
    if tool:
        rows.extend(plugins.gather(tool, override=plugin_override))
    sauce_root = zpp_home() / "saucepan"
    for pack in sorted(sauce_root.iterdir()) if sauce_root.is_dir() else []:
        if not pack.is_dir():
            continue
        manifest = pack / "sauce.json"
        version = None
        if manifest.is_file():
            version = json.loads(manifest.read_text()).get("version")
        for f in sorted(pack.glob("*.md")):
            rows.append({"name": f.stem, "source": "saucepan", "path": str(f),
                         "version": version, "pack": pack.name})
    return rows


def _beats(a: dict, b: dict) -> bool:
    """a wins over b: better (lower) source precedence, or - within one source -
    the later-scanned row (so a later-gathered plugin trait wins its tier)."""
    pa, pb = PRECEDENCE.index(a["source"]), PRECEDENCE.index(b["source"])
    if pa != pb:
        return pa < pb
    return a["_order"] > b["_order"]


def available(tool: str | None = None, plugin_override: Path | None = None) -> list[dict]:
    """All trait rows with shadowing resolved: for each name the winning copy is
    kept; every other copy is marked shadowed."""
    rows = _scan(tool, plugin_override)
    for i, row in enumerate(rows):
        row["_order"] = i
    winners: dict[str, dict] = {}
    for row in rows:
        cur = winners.get(row["name"])
        if cur is None or _beats(row, cur):
            winners[row["name"]] = row
    for row in rows:
        row["shadowed"] = row is not winners[row["name"]]
        del row["_order"]
    return rows


def content(name: str, tool: str | None = None,
            plugin_override: Path | None = None) -> str | None:
    """The winning copy's content, or None when the name resolves nowhere."""
    for row in available(tool, plugin_override):
        if row["name"] == name and not row["shadowed"]:
            return Path(row["path"]).read_text()
    return None


def effective(path: Path, tool: str | None = None) -> dict:
    """The applied trait set for a context: [traits] apply lists from the
    config tiers (store -> workset/env -> repo), unioned in tier order, each
    name resolved to winning content. Unknown names are reported, not fatal."""
    resolved = governance.resolve_config(path)
    override = _plugin_override(resolved, tool)
    apply_list = resolved["effective"].get("traits", {}).get("apply", [])
    applied, unknown = [], []
    rows = available(tool, override)
    for name in apply_list:
        text = content(name, tool, override)
        if text is None:
            unknown.append(name)
            continue
        row = next(r for r in rows if r["name"] == name and not r["shadowed"])
        applied.append({"name": name, "source": row["source"],
                        "tier": _introducing_tier(name, resolved["layers"]),
                        "content": text})
    return {"applied": applied, "unknown": unknown, "mode": resolved["mode"]}


def _plugin_override(resolved: dict, tool: str | None) -> Path | None:
    """Per-surface base-dir override from [traits] plugins.<tool>, or None."""
    if not tool:
        return None
    override = resolved["effective"].get("traits", {}).get("plugins", {}).get(tool)
    return Path(override) if override else None


def _introducing_tier(name: str, layers: dict) -> str:
    """The first tier (in application order) whose [traits] apply names it."""
    for tier, cfg in layers.items():
        if name in cfg.get("traits", {}).get("apply", []):
            return tier
    return "?"
