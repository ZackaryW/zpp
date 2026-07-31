# workflow-skill-distribution Specification

## Purpose

Defines safe distribution and lifecycle management of ZPP's permanent workflow-skill bundle across supported agents' native global and repository-local skill scopes.

## Requirements

### Requirement: Permanent workflow bundle ownership
ZPP SHALL package the seven permanent `zpp-*` workflow skills as one versioned owned bundle. Installed copies SHALL be projections of the packaged bundle, preserve every required skill resource, and SHALL NOT embed agent, application-platform, framework, test-runner, or optional-trait policy in skill bodies.

Permanent skills SHALL retain stage-specific operations, hard gates, verification authority, OpenSpec operation ownership, and zmem materiality in their owning skill. Cross-cutting advisory governance SHALL remain in independently configurable standard traits rather than being repeated across skill bodies.

Each completed skill stage SHALL hand its result to the next owning workflow. When automatic progression or explicit end-to-end delegation applies, a satisfied checkpoint or ordinary stage transition SHALL continue without an approval-only pause.

ZPP SHALL establish managed ownership and compatibility through bundle metadata plus exact owned content rather than directory names. Passive trait `skill_lookup` metadata SHALL NOT execute a skill or grant authority.

#### Scenario: Use the permanent workflow bundle
- **WHEN** a user installs the workflow skills and resolves the standard advisory traits
- **THEN** stage-specific enforcement remains skill-owned while shared guidance and automatic handoffs remain advisory

### Requirement: Explicit skill lifecycle and scope
ZPP SHALL expose independent `workflow install`, `workflow update`, and `workflow remove` commands for Pi, Codex, and Claude Code. The lifecycle SHALL support user-global scope or an exact existing repository-local directory inside a Git worktree and SHALL NOT create or modify an authored `.zpp` layer. ZPP SHALL NOT expose the former generic `skill` command group.

Codex and Pi SHALL share their native `.agents/skills` projection, while Claude Code SHALL use its native `.claude/skills` projection. Agent-specific destination rules SHALL remain outside the workflow-skill bodies.

#### Scenario: Select lifecycle scope and agents
- **WHEN** a user invokes a workflow lifecycle command with a valid scope and supported agent selection
- **THEN** ZPP targets only the corresponding native projection or rejects the invocation before changing agent state

### Requirement: Agent selection for skill lifecycle
Repeated explicit agent selections SHALL bypass prompting. Without explicit selections, an interactive workflow lifecycle invocation SHALL offer Pi, Codex, and Claude Code as a zero-or-more selector; empty submission SHALL succeed without changes and cancellation SHALL make no changes. A noninteractive workflow lifecycle invocation without explicit agents SHALL be a usage error.

#### Scenario: Resolve lifecycle agent selection
- **WHEN** a workflow lifecycle command obtains explicit, interactive-empty, cancelled, or missing-noninteractive selection input
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

### Requirement: Workflow lifecycle isolation from authored profiles
Workflow installation, update, and removal SHALL operate only on selected managed agent projections. These operations SHALL NOT create, modify, rename, or remove any user profile or authored trait content, including the persistent `default` profile.

#### Scenario: Maintain skills without changing profiles
- **WHEN** a user installs, updates, declines removal, or confirms removal of selected workflow projections
- **THEN** only eligible managed agent projection state changes and every authored profile remains unchanged

### Requirement: Stage-owned OpenSpec change disposition
Permanent workflow skills SHALL own the lifecycle operations appropriate to
their stages. Clarification SHALL establish the session-local related set.
Utility planning SHALL register its companion as disposable, and utility
maturity SHALL discard it and verify its absence before wiring. Specification
formation SHALL hand the product change to the owning OpenSpec finalizer and
then audit the related set.

A consumed internal anchor whose consumer condition is satisfied SHALL be
discarded. Genuinely unfinished related work MAY remain active only under an
identified owning stage. A consumed related change without an owner SHALL block
the workflow completion claim.

#### Scenario: Apply stage-owned terminal dispositions
- **WHEN** a mature workflow disposes its utility scaffolding and finalizes its product change
- **THEN** the owning skills verify those dispositions and reject completion if any consumed related change remains unowned

Executable public examples for every requirement are maintained in `features/workflow_skill_distribution.feature`.
