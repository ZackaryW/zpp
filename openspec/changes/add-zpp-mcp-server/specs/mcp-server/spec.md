# Delta: mcp-server

## ADDED Requirements

### Requirement: Workspace subproject packaging
The MCP server SHALL live in a `zpp-mcp/` uv workspace subproject with its
own `pyproject.toml`, distribution name `zpp-mcp`, and console entry point
`zpp-mcp`. It SHALL depend on `zpp` and the official MCP Python SDK; the zpp
core distribution's dependencies SHALL remain unchanged.

#### Scenario: Separate installation
- **WHEN** `zpp-mcp` is installed as a tool
- **THEN** the `zpp-mcp` command starts a stdio MCP server, and installing
  `zpp` alone neither provides the command nor pulls the MCP SDK

### Requirement: Governance mount toolset
The server SHALL expose exactly the governance mount set as MCP tools —
`resolve`, `trait_list`, `trait_effective`, `trait_content`, `doctor` — each
a thin wrapper over `zpp.core` returning the same JSON structure as the
corresponding CLI `--json` output for a given target path. No mutating zpp
operation SHALL be exposed.

#### Scenario: Resolve parity with CLI
- **WHEN** the `resolve` tool is called for a governed repo path
- **THEN** the result matches `zpp resolve --json` for that path, including
  mode and store attribution

#### Scenario: No mutating surface
- **WHEN** the client lists available tools
- **THEN** only the five mount-set tools are present; snapshot, workset, and
  config-writing operations are absent

### Requirement: zpp-governance prompt
The server SHALL expose a single MCP prompt named `zpp-governance` that
composes the same context block as the surface mount script: governance
resolution, effective trait content for the target, and the doctor report
only when resolution degrades.

#### Scenario: Governed target yields mount block
- **WHEN** the prompt is requested for a governed repo
- **THEN** the returned message contains the governance mode, store identity,
  and effective trait content, without a doctor report when healthy

### Requirement: Silent degradation
The server SHALL follow the mount degradation contract: an ungoverned path,
missing configuration, or unavailable openspec CLI yields an informative,
well-formed MCP result (never a protocol error or crash), and the ungoverned
mode is reported as a mode, not a failure.

#### Scenario: Ungoverned path
- **WHEN** the `zpp-governance` prompt is requested for an ungoverned path
- **THEN** the server returns a well-formed result stating ungoverned mode
  with no trait content and no error
