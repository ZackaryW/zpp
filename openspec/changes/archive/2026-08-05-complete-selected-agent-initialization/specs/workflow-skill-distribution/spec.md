## ADDED Requirements

### Requirement: Complete selected-agent initialization
Initialization with one or more explicitly or interactively selected agents SHALL establish the complete current user-global workflow integration for exactly those agents. Success SHALL leave each selected agent with the current managed ZPP workflow bundle, its current native ZPP lifecycle hooks, and the OpenSpec core operation skills emitted for that agent by the installed OpenSpec version in the agent's global skill location.

Initialization SHALL use the established complete global installation ownership and compatibility rules: it SHALL install absent projections, replace intact outdated managed ZPP projections, regenerate outdated managed OpenSpec projections according to the detected-version contract, preserve compatible projections without rewriting them, and reject malformed, modified, unsafe, or unmanaged conflicting state without overwrite. It SHALL obtain OpenSpec-owned skill content through isolated generation and SHALL preserve unrelated agent content.

Initialization SHALL preflight every selected agent's included hook, workflow, and OpenSpec destination before changing any selected agent surface, and SHALL apply the complete selected-agent integration atomically. Neutral ZPP user-state initialization MAY complete before a later selected-agent conflict is reported, but a failed selected-agent setup SHALL leave every selected agent surface unchanged. An existing valid user-owned default profile SHALL remain byte-for-byte unchanged during initialization.

Initialization without a selected agent, an empty interactive selection, and a cancelled interactive selection SHALL NOT create or change workflow or OpenSpec skill projections. Repository-local projections and unselected agents SHALL remain unchanged in every initialization outcome.

#### Scenario: Initialize a selected agent with missing workflow skills
- **WHEN** a user runs `zpp init --agent codex` while Codex lacks the managed ZPP workflow bundle but has compatible global OpenSpec skills
- **THEN** Codex receives the current ZPP workflow bundle and native hooks under its global locations while its compatible OpenSpec skills, unrelated content, and repository-local projections remain unchanged

#### Scenario: Complete every selected integration atomically
- **WHEN** initialization selects multiple agents whose complete global integrations can all be established safely
- **THEN** every selected agent receives its current ZPP bundle, native hooks, and OpenSpec core skills as one selected-agent setup outcome

#### Scenario: Reject a selected integration conflict without partial agent setup
- **WHEN** any selected hook, ZPP projection, generated OpenSpec skill set, or OpenSpec destination conflicts or cannot be preflighted
- **THEN** initialization may retain successfully created neutral ZPP user state but changes no selected agent surface and preserves unrelated content

#### Scenario: Refresh an intact outdated selected integration
- **WHEN** initialization selects an agent with intact outdated managed ZPP or OpenSpec projections
- **THEN** it establishes the current complete selected-agent integration through the existing managed replacement and version-aware generation rules

#### Scenario: Repeat complete selected-agent initialization
- **WHEN** a selected agent already has a complete compatible global workflow integration
- **THEN** initialization succeeds without rewriting its managed, generated, or unrelated agent content or the existing valid default profile

#### Scenario: Initialize without selecting an agent
- **WHEN** initialization receives no selected agent through a noninteractive invocation, empty submission, or cancellation
- **THEN** it creates or changes no global or repository-local workflow or OpenSpec skill projection
