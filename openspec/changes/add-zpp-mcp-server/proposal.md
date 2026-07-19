# Proposal: add-zpp-mcp-server

## Why

Governance currently mounts on three surfaces (Claude Code, Codex, Kimi)
through session-start hooks. The Claude Desktop **chat surface** has no hook
mechanism at all — per the July 2026 docs, plugin hooks are grayed out in
Chat, and the only supported extension path is MCP via Desktop Extensions
(`.mcpb` bundles, MCP servers only). Reaching that surface therefore requires
an MCP server, and by charter everything mechanical lives in zpp — the
governance store ships only declarations and packaging.

This is **phase 1 of a two-phase project**: this change builds the server in
the zpp repo; the companion change `mcpb-desktop-surface` in the
`governance-of-agents-1v2` store ships the `.mcpb` packaging that invokes it.

## What Changes

- New **uv workspace subproject** `zpp-mcp/` in this repo: its own
  `pyproject.toml` and `zpp-mcp` entry point, depending on `zpp` (workspace
  source) plus the official MCP Python SDK. Installable separately
  (`uv tool install zpp-mcp`); **zpp core's dependency list is unchanged**
  (typer + tomli-w).
- The subproject implements a **stdio MCP server** exposing the governance
  mount set only:
  - tools: `resolve`, `trait_list`, `trait_effective`, `trait_content`,
    `doctor` — thin wrappers over `zpp.core`, returning the same JSON as the
    CLI `--json` forms;
  - one prompt: `zpp-governance`, serving the same composed block as
    `scripts/zpp-mount.sh` (resolution + effective traits, doctor report only
    on degradation) — the chat surface's stand-in for a session-start hook.
- Same degradation contract as the mount: ungoverned or unresolvable state
  yields an empty/informative result, never a crash.
- BDD (behave) + TDD (pytest) coverage, fail-first, per standing mandate.

## Capabilities

### New Capabilities
- `mcp-server`: the zpp-mcp workspace subproject — packaging boundary, the
  governance mount toolset over stdio MCP, the zpp-governance prompt, and
  the degradation contract.

### Modified Capabilities
<!-- none — zpp core behavior is unchanged; the server only consumes it -->

## Impact

- New top-level `zpp-mcp/` folder; root `pyproject.toml` gains a
  `[tool.uv.workspace]` members entry. No changes to `zpp/` package code.
- New dependency (MCP Python SDK) confined to the subproject.
- Downstream: unblocks `mcpb-desktop-surface` in governance-of-agents-1v2
  (phase 2), which packages this server as a Desktop Extension.
