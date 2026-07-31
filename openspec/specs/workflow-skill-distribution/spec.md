# workflow-skill-distribution Specification

## Purpose

Defines safe distribution and lifecycle management of ZPP's permanent workflow-skill bundle across supported agents' native global and repository-local skill scopes.

## Requirements

### Requirement: Permanent workflow bundle ownership
ZPP SHALL package the seven permanent `zpp-*` workflow skills as one versioned owned bundle. Installed copies SHALL be projections of the packaged bundle, preserve every required skill resource, and SHALL NOT embed agent, application-platform, framework, or test-runner policy in skill bodies.

ZPP SHALL establish managed ownership and compatibility through bundle metadata plus exact owned content rather than directory names. A conditionless automatic-workflow trait MAY coordinate unattended advancement and reference the permanent skills through passive `skill_lookup`; the trait SHALL NOT execute the lookup, bypass skill-defined gates, settle missing product decisions, or grant mutation authority.

#### Scenario: Use the permanent workflow bundle
- **WHEN** a user installs or resolves the accepted workflow guidance
- **THEN** the complete platform-neutral bundle is available while automatic progression remains advisory and skill-gated

### Requirement: Explicit skill lifecycle and scope
ZPP SHALL expose independent `skill install`, `skill update`, and `skill remove` commands for Pi, Codex, and Claude Code. The lifecycle SHALL support user-global scope or an exact existing repository-local directory inside a Git worktree and SHALL NOT create or modify an authored `.zpp` layer.

Codex and Pi SHALL share their native `.agents/skills` projection, while Claude Code SHALL use its native `.claude/skills` projection. Agent-specific destination rules SHALL remain outside the workflow-skill bodies.

#### Scenario: Select lifecycle scope and agents
- **WHEN** a user invokes a skill lifecycle command with a valid scope and supported agent selection
- **THEN** ZPP targets only the corresponding native projection or rejects the invocation before changing agent state

### Requirement: Agent selection for skill lifecycle
Repeated explicit agent selections SHALL bypass prompting. Without explicit selections, an interactive invocation SHALL offer Pi, Codex, and Claude Code as a zero-or-more selector; empty submission SHALL succeed without changes and cancellation SHALL make no changes. A noninteractive lifecycle invocation without explicit agents SHALL be a usage error.

#### Scenario: Resolve lifecycle agent selection
- **WHEN** a skill lifecycle command obtains explicit, interactive-empty, cancelled, or missing-noninteractive selection input
- **THEN** it follows the established selection outcome without inferring an agent

### Requirement: Compatible installation and coexistence
Installation SHALL preflight the complete bundle and every selected destination before mutation, preserve unrelated content, and reject unmanaged or conflicting destinations without overwrite. Repeating installation against a compatible selected projection SHALL be idempotent.

Local installation SHALL reuse a compatible managed global projection by default. An absent or outdated global projection SHALL NOT suppress current local installation. `--force` SHALL bypass only compatible-global deduplication and SHALL NOT authorize conflict replacement. Managed global and local projections MAY coexist; ZPP SHALL report coexistence and differing versions without asserting scope precedence.

#### Scenario: Plan installation from all selected state
- **WHEN** installation evaluates selected destinations together with corresponding global compatibility
- **THEN** it either applies the complete safe plan or leaves every selected destination unchanged

### Requirement: Managed update and removal
Update SHALL operate only on the explicitly selected managed scope, make compatible projections no-ops, replace outdated managed projections with the packaged bundle, and leave every unselected global or local scope unchanged.

Removal SHALL require confirmation unless `--yes` or `-y` is supplied and SHALL remove only metadata-owned ZPP paths from the selected managed projection. Update and removal SHALL reject missing, malformed, conflicting, or user-owned selected state without partial mutation.

#### Scenario: Maintain one selected managed scope
- **WHEN** a user updates or confirms removal for selected managed projections
- **THEN** only their owned state changes and unrelated or unselected state remains unchanged

Executable public examples for every requirement are maintained in `features/workflow_skill_distribution.feature`.
