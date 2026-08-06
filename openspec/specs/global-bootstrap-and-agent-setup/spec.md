# global-bootstrap-and-agent-setup Specification

## Purpose

Defines neutral ZPP user-state initialization and optional global agent lifecycle integration without introducing project state or embedded policy.

## Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.6 and expose initialization, global installed-state update, profile, persistent global activation, saved-profile, local-layer, resolution, repository behavior verification through `zpp behave init`, `zpp behave <command>`, and `zpp behave <command> --all`, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain available through initialization and complete workflow installation, while `zpp update` SHALL maintain existing recognized global integrations without becoming an executable self-updater. Standard-workflow distribution SHALL use the independent `workflow` command group and behavior verification SHALL remain independent from workflow-skill lifecycle management. The generic `skill` command group SHALL NOT remain available.

Typer help SHALL distinguish `zpp init` as missing-state bootstrap plus explicitly selected hook configuration from `zpp update` as maintenance of initialized global ZPP state and already-installed integrations.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.6, exposes independent `init`, top-level `update`, `behave`, and standard-workflow lifecycle surfaces, and does not expose a generic skill-management group

#### Scenario: Distinguish initialization from update
- **WHEN** a user inspects `zpp init --help` and `zpp update --help`
- **THEN** the helpers distinguish bootstrap and selected-hook setup from global installed-state maintenance without claiming that ZPP upgrades its running executable

Executable public examples are maintained in the capability feature contracts that own bootstrap, verification orchestration, and workflow distribution.

### Requirement: Neutral user-state initialization
Initialization SHALL create an unconditional neutral global trait layer, a permanent user-owned `default` profile containing the bundled standard traits, and the saved-override and independent-cache namespaces under the user's ZPP state. It SHALL NOT create project-local state or derived trait caches.

Initialization SHALL create the bundled `default` profile only when it is absent. It SHALL validate all existing required managed user sources before creating missing state, preserve valid existing authored bytes including a user-edited `default` profile, create only missing required entries, and be idempotent. Invalid managed state SHALL reject initialization without partial user-state writes.

#### Scenario: Initialize missing user state
- **WHEN** initialization runs against absent or valid partial user state
- **THEN** neutral global state and the permanent default profile exist, valid existing authored bytes are unchanged, and no project or derived-cache state is created

#### Scenario: Preserve an existing default
- **WHEN** initialization encounters a valid user-edited `default` profile
- **THEN** the complete profile remains byte-for-byte unchanged and bundled content is not reapplied

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
Agents selected by initialization or complete workflow installation SHALL be configured only through their global user-home native lifecycle mechanisms. Global update SHALL reconcile a recognized existing ZPP native integration and SHALL ensure the current native integration for every discovered installed managed global workflow bundle. It SHALL leave an agent with neither a recognized hook nor an installed managed workflow bundle unchanged. Native-integration maintenance SHALL NOT install repository-local agent integration, instruction paragraphs, effective trait content, trust state, or enablement state; workflow installation and update MAY independently project their owned skill surfaces.

Each agent integration SHALL be independently idempotent, preserve unrelated native configuration, and reject invalid or conflicting unmanaged state without overwrite. A current integration SHALL replace an exact historical ZPP-generated native hook record with the current owned record instead of treating that known legacy form as an unmanaged conflict. Initialization SHALL preflight every explicitly selected agent, complete workflow installation SHALL preflight every selected agent, and global update SHALL preflight every discovered ZPP-owned global surface before changing any included state.

#### Scenario: Configure supported native integrations
- **WHEN** initialization or complete workflow installation selects any combination of Pi, Codex, and Claude Code against compatible agent state
- **THEN** each selected global native lifecycle integration exists exactly once, unrelated agent content is preserved, and unselected agents and project-local native state are unchanged

#### Scenario: Refresh a recognizable installed hook
- **WHEN** global update discovers a current or exact historical ZPP native integration without an installed workflow bundle
- **THEN** it reconciles that hook to the current owned form while leaving absent skill projections absent

#### Scenario: Ensure hooks for an installed workflow
- **WHEN** global update discovers an installed managed global workflow bundle with a missing or historical ZPP native integration
- **THEN** it establishes the current native integration as part of that bundle's complete maintained outcome

#### Scenario: Migrate a historical ZPP hook
- **WHEN** a selected agent contains an exact native hook record generated by an earlier supported ZPP version
- **THEN** ZPP replaces that owned record with the current integration while preserving unrelated agent content

#### Scenario: Reject an agent conflict atomically
- **WHEN** any included agent has invalid or conflicting unmanaged integration state
- **THEN** the initiating operation fails with the conflicting destination identified and no included global surface is changed

### Requirement: Top-level global update boundary
`zpp update` SHALL require complete valid initialized user state and SHALL accept no agent, scope, target, force, or installation option. It SHALL automatically discover existing ZPP-owned global surfaces across Pi, Codex, and Claude Code, preflight them with the persistent default profile, and apply the complete compatible refresh atomically. It SHALL fail without mutation when required user state is absent, incomplete, or malformed and SHALL direct the user to initialize first.

Global update SHALL NOT create repository-local state, mutate local skills or authored `.zpp` layers, resolve traits, create derived caches, install an absent workflow bundle, or upgrade the executable that is currently running.

#### Scenario: Update initialized global state
- **WHEN** a user runs `zpp update` against compatible initialized state with any mix of existing ZPP-owned global surfaces
- **THEN** ZPP refreshes the complete discovered global set atomically and leaves absent and repository-local surfaces unchanged

#### Scenario: Reject update before initialization
- **WHEN** a user runs `zpp update` with absent, incomplete, or malformed required user state
- **THEN** ZPP reports that initialization is required or invalid and changes no user or agent surface

#### Scenario: Reject unsupported update syntax
- **WHEN** a user supplies an agent, local/global scope, positional target, force, or install option to `zpp update`
- **THEN** Typer rejects the invocation before ZPP performs discovery or mutation

### Requirement: Source-authoritative lifecycle context
Every installed native lifecycle integration SHALL identify its owning Codex, Claude, or Pi agent when resolving traits for the agent session's current working directory at invocation time. Resolution SHALL use that identity to discover only the invoking agent's active plugin trait sources. Successful non-empty resolution output SHALL be injected exactly once into the current agent context. Empty successful output SHALL inject nothing. Resolution failure SHALL be surfaced through the agent and SHALL inject no stale or partial ZPP context.

Agent installation itself SHALL NOT invoke resolution, discover plugin trait sources, or create trait caches.

#### Scenario: Invoke a configured lifecycle integration
- **WHEN** a configured and enabled native lifecycle event invokes ZPP
- **THEN** it identifies the owning agent, injects current successful trait output once, injects nothing for empty output, and contributes no stale or partial context after failed resolution

#### Scenario: Keep agent installation side-effect free from resolution
- **WHEN** ZPP installs or reconciles a native lifecycle integration
- **THEN** it does not resolve traits, inspect active plugin sources, or create derived trait state during installation
