"""The `zpp-governance` prompt: the chat surface's stand-in for a session-start
hook. Composes the exact block scripts/zpp-mount.sh emits for the hook surfaces
- governance header, effective trait content, and (only when resolution
degrades) the doctor report - so all four surfaces mount the same context.

Silent-degradation contract, matching the script: an ungoverned, clean context
with no traits yields an empty string (nothing to mount); everything else
yields a well-formed <zpp-governance> block. Never raises for governance state.
"""

from pathlib import Path

from zpp.core import governance, toolchain, traits


def _traits_text(path: Path, tool: str | None) -> str:
    """Applied trait content in application order, block-commented by name -
    the same layout `zpp trait effective` prints for the mount."""
    applied = traits.effective(path, tool)["applied"]
    blocks = [f"<!-- trait: {t['name']} [{t['source']}] -->\n{t['content']}"
              for t in applied]
    return "\n".join(blocks).rstrip()


def _doctor_text(path: Path) -> str:
    """The doctor report rendered as the CLI prints it (detect-only lines)."""
    report, _warning = toolchain.doctor(path)
    lines = []
    for r in report:
        mark = "✓" if r["present"] else "✗"
        if r["present"]:
            detail = r["version"] or ""
        else:
            detail = f"missing - {r['hint']}" if r["hint"] else "missing"
        lines.append(f"{mark} {r['tool']}  {detail}".rstrip())
    return "\n".join(lines)


def governance_block(path: str = ".", tool: str | None = None) -> str:
    """The composed mount block for a context, or "" when nothing to mount."""
    p = Path(path)
    resolved = governance.resolve(p)
    mode = resolved["mode"]
    store = resolved.get("store")
    degraded = bool(resolved.get("warnings"))
    traits_text = _traits_text(p, tool)

    if mode == "ungoverned" and not traits_text and not degraded:
        return ""

    header = f"governance: {mode} (store: {store})" if store else f"governance: {mode}"
    parts = ["<zpp-governance>", header]
    if traits_text:
        parts += ["", traits_text]
    if degraded:
        parts += ["", "environment degraded - doctor report:", _doctor_text(p)]
    parts.append("</zpp-governance>")
    return "\n".join(parts)
