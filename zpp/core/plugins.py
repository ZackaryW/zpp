"""Agent-surface plugins as a live trait source.

Per-surface Resolver (owns per-OS base dir + how to enumerate installed
plugins) + a shared extractor (reads traits/*.md from a plugin root). Gathering
is live and per-tool - nothing is cached to disk. Only traits/ is read; a
plugin's skills, scripts, and manifests are ignored."""

import json
from pathlib import Path


def _home_base(name: str, override: Path | None) -> Path:
    """Base dir for a home-rooted surface. Claude Code and Codex both store
    under ~/.<tool>, and Path.home() resolves that on every OS (incl. Windows
    %USERPROFILE%). The per-surface config override is the backstop for any
    platform where this proves wrong - Windows is not verified on this host."""
    return Path(override) if override is not None else Path.home() / name


class ClaudeResolver:
    """Claude Code: ~/.claude/plugins/installed_plugins.json maps
    <plugin>@<marketplace> -> installPath(s)."""

    tool = "claude"

    def base_dir(self, override: Path | None = None) -> Path:
        return _home_base(".claude", override)

    def plugin_roots(self, override: Path | None = None):
        index = self.base_dir(override) / "plugins" / "installed_plugins.json"
        if not index.is_file():
            return
        try:
            data = json.loads(index.read_text())
        except json.JSONDecodeError:
            return
        for key, installs in data.get("plugins", {}).items():
            name = key.split("@", 1)[0]
            for install in installs or []:
                path = install.get("installPath")
                if path and Path(path).is_dir():
                    yield name, Path(path)


class CodexResolver:
    """Codex: ~/.codex/plugins. Thin until the surface populates a stable
    layout - resolves what exists, reports nothing rather than guessing."""

    tool = "codex"

    def base_dir(self, override: Path | None = None) -> Path:
        return _home_base(".codex", override)

    def plugin_roots(self, override: Path | None = None):
        root = self.base_dir(override) / "plugins"
        for child in sorted(root.iterdir()) if root.is_dir() else []:
            if child.is_dir() and not child.name.startswith("."):
                yield child.name, child


RESOLVERS = {r.tool: r for r in (ClaudeResolver(), CodexResolver())}


def extract(plugin_root: Path, tool: str, plugin: str) -> list[dict]:
    """A plugin's opt-in traits: traits/*.md only, tagged with provenance."""
    traits_dir = Path(plugin_root) / "traits"
    if not traits_dir.is_dir():
        return []
    return [
        {"name": f.stem, "source": "plugin", "path": str(f),
         "version": None, "tool": tool, "plugin": plugin}
        for f in sorted(traits_dir.glob("*.md"))
    ]


def gather(tool: str, override: Path | None = None) -> list[dict]:
    """Live: resolve the surface's installed plugins and extract their traits.
    Unknown surface -> empty (no error). Order = resolver order, so a later
    plugin's same-named trait wins in the precedence tier."""
    resolver = RESOLVERS.get(tool)
    if resolver is None:
        return []
    rows: list[dict] = []
    for plugin, root in resolver.plugin_roots(override):
        rows.extend(extract(root, tool=tool, plugin=plugin))
    return rows
