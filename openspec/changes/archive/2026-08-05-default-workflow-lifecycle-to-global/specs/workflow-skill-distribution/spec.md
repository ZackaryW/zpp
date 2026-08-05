## MODIFIED Requirements

### Requirement: Explicit skill lifecycle and scope
ZPP SHALL expose independent `workflow install`, `workflow update`, and `workflow remove` commands for Pi, Codex, and Claude Code. Each workflow lifecycle command SHALL select user-global scope when no scope option is supplied and SHALL select repository-local scope only when the user supplies `--local`. The public workflow lifecycle scope selector SHALL be `--local` rather than `--global`.

Repository-local scope SHALL target the current directory when no positional target is supplied or an exact existing directory inside a Git worktree when a target is supplied, and SHALL NOT create or modify an authored `.zpp` layer. A positional target without `--local` SHALL be rejected before changing managed or agent state. `--force` and `--with-openspec` SHALL be accepted only with `--local` and SHALL be rejected in global scope before changing managed or agent state. ZPP SHALL NOT accept `--global` as a workflow lifecycle option and SHALL NOT expose the former generic `skill` command group.

Codex SHALL use `.agents/skills`. Pi SHALL use `.pi/skills` in repository-local scope and `.pi/agent/skills` in user-global scope. Claude Code SHALL use `.claude/skills`. Agent-specific destination rules SHALL remain outside the workflow-skill bodies.

#### Scenario: Default lifecycle scope to global
- **WHEN** a user invokes `workflow install`, `workflow update`, or `workflow remove` without `--local`
- **THEN** ZPP targets only the corresponding user-global native projection or rejects the invocation before changing agent state

#### Scenario: Select repository-local lifecycle scope explicitly
- **WHEN** a user invokes a workflow lifecycle command with `--local` and a valid supported agent selection
- **THEN** ZPP targets only the corresponding repository-local native projection at the supplied target or current directory when omitted, or rejects the invocation before changing agent state

#### Scenario: Reject local syntax without the local selector
- **WHEN** a user supplies a positional repository target without `--local`, supplies the removed `--global` option, or supplies a local-only install control in global scope
- **THEN** ZPP rejects the invocation before changing managed or agent state

#### Scenario: Keep Pi and Codex projections independent
- **WHEN** a workflow lifecycle operation selects Pi, Codex, or both
- **THEN** Pi's `.pi` projection and Codex's `.agents` projection are planned, owned, and maintained independently
