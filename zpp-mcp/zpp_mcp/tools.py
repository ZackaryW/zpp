"""The governance mount toolset: read-only wrappers over zpp.core.

Each function returns the same structure as the matching CLI `--json` form, so
parity is structural (same core call), not scraped. No mutating zpp operation
(snapshot, workset, config writes) is exposed here or registered by the server.

These functions import only zpp.core - never mcp - so they are testable without
the SDK. Every one takes an explicit `path`: the chat surface has no cwd.
"""

from pathlib import Path

from zpp.core import governance, toolchain, traits


def _plugin_override(tool: str | None, path: Path) -> Path | None:
    """The [traits] plugins.<tool> base-dir override, mirroring cli/trait.py."""
    if not tool:
        return None
    override = (governance.resolve_config(path)["effective"]
                .get("traits", {}).get("plugins", {}).get(tool))
    return Path(override) if override else None


def resolve(path: str = ".") -> dict:
    """Governance mode of a directory - matches `zpp resolve --json`."""
    return governance.resolve(Path(path))


def trait_list(path: str = ".", tool: str | None = None) -> list[dict]:
    """Every available trait with source/shadowing - matches `zpp trait list --json`."""
    p = Path(path)
    return traits.available(tool, _plugin_override(tool, p))


def trait_effective(path: str = ".", tool: str | None = None) -> dict:
    """The applied trait set for a context - matches `zpp trait effective --json`."""
    return traits.effective(Path(path), tool)


def trait_content(name: str, path: str = ".", tool: str | None = None) -> dict:
    """One trait's winning content. `found` is False when the name resolves
    nowhere (parity with `zpp trait show`, as structured data)."""
    text = traits.content(name, tool, _plugin_override(tool, Path(path)))
    return {"name": name, "found": text is not None, "content": text}


def doctor(path: str = ".") -> list[dict]:
    """Toolchain health, detect-only - matches `zpp doctor --json` (the report
    list). The degradation warning surfaces through the prompt, not here."""
    report, _warning = toolchain.doctor(Path(path))
    return report


# The exact mount set the server registers. Kept here (no mcp import) so a test
# can assert the surface is read-only without the SDK installed.
TOOL_FUNCS = [resolve, trait_list, trait_effective, trait_content, doctor]
