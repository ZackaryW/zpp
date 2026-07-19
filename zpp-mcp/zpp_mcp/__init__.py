"""zpp-mcp: the governance mount set served over stdio MCP.

The Claude Desktop chat surface has no session-start hook (July 2026 docs);
its only extension path is an MCP server via a Desktop Extension. This package
exposes the same mount zpp-mount.sh composes for the hook surfaces - resolve,
traits, doctor - as read-only MCP tools plus a `zpp-governance` prompt.

Logic lives in `tools` and `prompt` (importing only zpp.core, no MCP); the
thin FastMCP wiring is isolated in `server`, so the mount logic is testable
without the SDK installed.
"""
