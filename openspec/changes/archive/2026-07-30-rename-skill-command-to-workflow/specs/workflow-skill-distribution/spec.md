## MODIFIED Requirements

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

Executable public examples for every requirement are maintained in `features/workflow_skill_distribution.feature`.
