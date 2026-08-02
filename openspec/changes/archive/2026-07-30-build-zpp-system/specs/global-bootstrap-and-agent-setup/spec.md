## Purpose

Defines neutral ZPP user-state initialization and optional global agent lifecycle integration without introducing project state or embedded policy.

## ADDED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.0 and expose initialization, profile, saved-profile, local-layer, resolution, help, and version behavior through the confirmed command hierarchy. Agent configuration SHALL remain part of initialization rather than a separate installation command.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.0 and the confirmed command hierarchy without a separate agent-install command

### Requirement: Neutral user-state initialization
Initialization SHALL create an unconditional neutral global trait layer plus empty profile, saved-override, and independent cache namespaces under the user's ZPP state. It SHALL NOT create project-local state or derived trait caches.

Initialization SHALL validate all existing managed user sources before creating missing state, preserve valid existing authored bytes, create only missing required entries, and be idempotent. Invalid managed state SHALL reject initialization without partial user-state writes.

#### Scenario: Initialize missing neutral state
- **WHEN** initialization runs against absent or valid partial user state
- **THEN** every required neutral user-state entry exists, valid existing authored bytes are unchanged, and no project or derived-cache state is created

#### Scenario: Reject invalid managed user state
- **WHEN** initialization encounters an invalid managed source while other required entries are missing
- **THEN** initialization fails, identifies the invalid source, and leaves the complete user state unchanged

### Requirement: Agent selection during initialization
Initialization SHALL accept repeated explicit selections from Pi, Codex, and Claude Code. Explicit selections SHALL bypass interactive selection. Without explicit selections, an interactive terminal SHALL offer those three agents as a zero-or-more selector, while a noninteractive invocation SHALL skip agent setup successfully.

Submitting an empty interactive selection SHALL succeed without agent changes. Cancelling the selector SHALL be distinct from an empty submission and SHALL make no agent changes. Unsupported explicit agent names SHALL be usage errors detected before ZPP user state or agent state is changed.

#### Scenario: Select agents explicitly
- **WHEN** initialization receives one or more supported explicit agent selections
- **THEN** it configures exactly those agents without offering the interactive selector

#### Scenario: Resolve an interactive selection
- **WHEN** initialization has no explicit selection in an interactive terminal
- **THEN** submitting selected agents configures them, submitting none succeeds without agent changes, and cancellation reports cancellation without agent changes

#### Scenario: Initialize noninteractively without selections
- **WHEN** initialization has no explicit selection and no interactive terminal
- **THEN** neutral user state is initialized and agent setup is skipped successfully

### Requirement: Global native agent integration
Selected agents SHALL be configured only through their global user-home native lifecycle mechanisms. ZPP SHALL NOT install repository-local agent integration, instruction paragraphs, skills, effective trait content, trust state, or enablement state.

Each agent integration SHALL be independently idempotent, preserve unrelated native configuration, and reject invalid or conflicting unmanaged state without overwrite. ZPP SHALL preflight every selected agent before changing any selected agent, although neutral ZPP user-state initialization may already have completed.

#### Scenario: Configure supported native integrations
- **WHEN** initialization selects any combination of Pi, Codex, and Claude Code against compatible agent state
- **THEN** each selected global native lifecycle integration exists exactly once, unrelated agent content is preserved, and unselected agents and project-local state are unchanged

#### Scenario: Reject a selected-agent conflict atomically
- **WHEN** a later selected agent has invalid or conflicting unmanaged integration state
- **THEN** agent setup fails with the conflicting destination identified and no selected agent is changed

### Requirement: Source-authoritative lifecycle context
Every installed native lifecycle integration SHALL resolve traits for the agent session's current working directory at invocation time. Successful non-empty resolution output SHALL be injected exactly once into the current agent context. Empty successful output SHALL inject nothing. Resolution failure SHALL be surfaced through the agent and SHALL inject no stale or partial ZPP context.

Agent installation itself SHALL NOT invoke resolution or create trait caches.

#### Scenario: Invoke a configured lifecycle integration
- **WHEN** a configured and enabled native lifecycle event invokes ZPP
- **THEN** current successful trait output is injected once, empty output injects nothing, and failed resolution contributes no stale or partial context
