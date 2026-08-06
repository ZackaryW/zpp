## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.7 and expose initialization, global installed-state update, profile, persistent global activation, saved-profile, local-layer, resolution, repository behavior verification through `zpp behave init`, `zpp behave <command>`, and `zpp behave <command> --all`, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Complete global agent setup SHALL remain available through initialization with selected agents and complete workflow installation, while `zpp update` SHALL maintain existing recognized global integrations without becoming an executable self-updater. Standard-workflow distribution SHALL use the independent `workflow` command group and behavior verification SHALL remain independent from workflow-skill lifecycle management. The generic `skill` command group SHALL NOT remain available.

Typer help SHALL distinguish `zpp init` as missing-state bootstrap plus complete global setup for selected agents from `zpp update` as discovery and maintenance of initialized global ZPP state and already-installed integrations.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.7, exposes independent `init`, top-level `update`, `behave`, and standard-workflow lifecycle surfaces, and does not expose a generic skill-management group

#### Scenario: Distinguish initialization from update
- **WHEN** a user inspects `zpp init --help` and `zpp update --help`
- **THEN** the helpers distinguish selected-agent complete setup from discovered installed-state maintenance without claiming that ZPP upgrades its running executable

Executable public examples are maintained in the capability feature contracts that own bootstrap, verification orchestration, and workflow distribution.

### Requirement: Agent selection during initialization
Initialization SHALL accept repeated explicit selections from Pi, Codex, and Claude Code. Explicit selections SHALL bypass interactive selection. Without explicit selections, an interactive terminal SHALL offer those three agents as a zero-or-more selector, while a noninteractive invocation SHALL skip agent setup successfully.

Every explicitly or interactively selected agent SHALL receive the complete current user-global workflow integration defined by the workflow-skill-distribution capability. Submitting an empty interactive selection SHALL succeed without agent changes. Cancelling the selector SHALL be distinct from an empty submission and SHALL make no agent changes. Unsupported explicit agent names SHALL be usage errors detected before ZPP user state or agent state is changed.

#### Scenario: Select agents explicitly
- **WHEN** initialization receives one or more supported explicit agent selections
- **THEN** it establishes the complete current global integration for exactly those agents without offering the interactive selector

#### Scenario: Resolve an interactive selection
- **WHEN** initialization has no explicit selection in an interactive terminal
- **THEN** submitting selected agents establishes their complete current global integrations, submitting none succeeds without agent changes, and cancellation reports cancellation without agent changes

#### Scenario: Initialize noninteractively without selections
- **WHEN** initialization has no explicit selection and no interactive terminal
- **THEN** neutral user state is initialized and agent setup is skipped successfully

### Requirement: Global native agent integration
Agents selected by initialization or complete workflow installation SHALL be configured only through their global user-home native lifecycle mechanisms. Global update SHALL reconcile a recognized existing ZPP native integration and SHALL ensure the current native integration for every discovered installed managed global workflow bundle. It SHALL leave an agent with neither a recognized hook nor an installed managed workflow bundle unchanged. The native-integration substep SHALL NOT install repository-local agent integration, instruction paragraphs, effective trait content, trust state, or enablement state; selected-agent initialization and workflow installation MAY independently project their owned global skill surfaces.

Each agent integration SHALL be independently idempotent, preserve unrelated native configuration, and reject invalid or conflicting unmanaged state without overwrite. A current integration SHALL replace an exact historical ZPP-generated native hook record with the current owned record instead of treating that known legacy form as an unmanaged conflict. Initialization and complete workflow installation SHALL preflight every selected agent's complete included global surface, and global update SHALL preflight every discovered ZPP-owned global surface before changing any included agent state.

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
- **THEN** the initiating operation fails with the conflicting destination identified and no included agent surface is changed
