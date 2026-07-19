# Design: add-zpp-mcp-server

## Context

Three surfaces mount governance via session-start hooks; the Claude Desktop
chat surface has none (hooks are Chat-grayed-out; Desktop Extensions carry
MCP servers only — July 2026 docs). The owner chose the `.mcpb`/MCP route
over chat-surface skills or Code-tab-only. zpp's charter takes the
mechanical half; the 1v2 store takes packaging (phase 2,
`mcpb-desktop-surface`).

## Goals / Non-Goals

**Goals:**
- A separately installable stdio MCP server serving the governance mount
  set, with CLI-parity JSON and the mount degradation contract.
- Zero impact on zpp core's dependency footprint or behavior.

**Non-Goals:**
- No `.mcpb` bundle here (store-side, phase 2).
- No mutating operations (worksets, snapshot, config writes) over MCP.
- No HTTP/SSE transport — stdio only, which is what Desktop Extensions run.
- No hand-rolled protocol: the official SDK owns the wire format.

## Decisions

- **uv workspace subproject, not an extra.** Owner-directed. `zpp-mcp/` is a
  workspace member depending on `zpp` via workspace source locally (version
  pin when published). Cleaner boundary than `zpp[mcp]`: the SDK dependency,
  entry point, and release cadence belong to the subproject.
- **In-process core calls, not shelling out.** Tools import `zpp.core`
  directly — same functions the CLI wires — so parity with `--json` output
  is structural, not scraped. The openspec CLI remains a subprocess
  underneath, with the existing degradation path.
- **Mount-set-only surface.** Owner-selected. Read-only tools plus one
  prompt; a chat model gets governance context, never write access. The
  prompt mirrors `zpp-mount.sh` composition (resolve → effective traits →
  doctor only on degradation). The script stays canonical for hook surfaces;
  parity is asserted by tests here, not by sharing code with the store.
- **Target path as tool argument.** The chat surface has no cwd; every tool
  and the prompt take an explicit `path` argument (defaulting to the
  server's start directory, which the `.mcpb` config can set).
- **Grounding at apply.** MCP SDK API and `.mcpb`-relevant server behavior
  are verified against fetched July 2026 docs during implementation, per the
  standing surface-grounding mandate.

## Risks / Trade-offs

- **SDK drift**: the MCP SDK moves fast; pinning a floor version in the
  subproject confines churn away from zpp core.
- **Prompt/script drift**: two composers of the same block (shell script in
  the store, Python here). Mitigated by the parity scenario in specs and the
  store's validator extension in phase 2; accepted over introducing a shared
  runtime dependency between store and server.
- **Prompts are user-invoked**: on the chat surface the mount only injects
  when the user picks the prompt — weaker than a hook. Accepted; it is the
  strongest mechanism that surface offers (recorded on the capability
  ladder in phase 2).
