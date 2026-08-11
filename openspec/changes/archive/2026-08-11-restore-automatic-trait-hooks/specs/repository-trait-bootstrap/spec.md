## MODIFIED Requirements

### Requirement: Agent Router discovery and projection authority
Agent Router SHALL remain the owner of supported agent/plugin discovery, effective artifact selection, destination resolution, ownership inspection, skill and hook installation, explicit project skill update, and removal. ZPP SHALL construct Agent Router with the actual user home and the selected repository as project context, register trait artifact semantics, and provide its packaged workflow skill and per-agent hook without independently scanning or mutating agent destinations. One resolution SHALL consume plugin traits only from the explicitly invoking agent's effective active `zpp.traits` artifacts.

#### Scenario: Project the complete workflow integration
- **WHEN** a user installs the ZPP workflow integration for a supported agent
- **THEN** ZPP asks that agent's Agent Router to project the consolidated skill and native hook and does not write either destination directly

#### Scenario: Discover invoking-agent plugin traits
- **WHEN** `resolve --agent codex` targets a repository and Codex has active user or project plugins providing `zpp.traits`
- **THEN** ZPP resolves those active artifacts using the router's home-rooted state and does not combine another agent's plugin context

#### Scenario: Explicitly update a project skill
- **WHEN** a user invokes project-scoped `workflow update` for a selected agent and repository
- **THEN** ZPP uses Agent Router's explicit project `update_skill` operation for the consolidated skill and its owned hook lifecycle for the hook

#### Scenario: Maintain a user integration safely
- **WHEN** a user installs or updates the user-scoped workflow integration
- **THEN** ZPP uses Agent Router's ownership-safe install reconciliation for the skill and hook
