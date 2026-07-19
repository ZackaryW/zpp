# Tasks: add-zpp-mcp-server

## 1. Scaffold

- [x] 1.1 Create `zpp-mcp/` subproject: `pyproject.toml` (deps: `zpp`
      workspace source, MCP Python SDK floor pin), `zpp_mcp/` package,
      `zpp-mcp` entry point; add `[tool.uv.workspace]` members to root
      `pyproject.toml`; `uv sync` resolves.
- [x] 1.2 Ground the SDK surface: fetch current (July 2026) MCP Python SDK
      docs for stdio server, tool, and prompt registration; record the
      pinned floor version.

## 2. Fail-first coverage

- [x] 2.1 pytest: failing tests for the five tool wrappers (CLI-parity JSON,
      explicit `path` argument, no mutating tools listed) and for
      degradation (ungoverned path, missing openspec CLI).
- [x] 2.2 behave: failing feature for the `zpp-governance` prompt — governed
      repo yields mode + store + trait content; degraded resolution appends
      doctor report; ungoverned yields well-formed ungoverned block.

## 3. Implement

- [x] 3.1 Implement server module: stdio server wiring, five tools calling
      `zpp.core` in-process, `zpp-governance` prompt composing
      resolve → effective traits → doctor-on-degradation.
- [x] 3.2 Make all new tests and features pass; full suite green
      (existing 49 tests + 36 scenarios untouched).

## 4. Close

- [x] 4.1 README: subproject section (install via `uv tool install zpp-mcp`,
      what it exposes, chat-surface context).
- [x] 4.2 `openspec validate --specs` passes; commit per zmem grammar
      (validator-checked); hand off to `mcpb-desktop-surface` (phase 2) in
      governance-of-agents-1v2.
