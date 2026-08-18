## MODIFIED Requirements

### Requirement: Packaged manual workspace-management guidance
ZPP SHALL package `zpp-workspace-management` as a companion skill for explicit cross-repository topology, workspace lifecycle, lock, successor, reconciliation, handoff, recovery, abandonment, and cleanup requests. The skill SHALL direct every operation through the ZPP-owned coordination command surface and SHALL NOT run from an agent hook, activate from repository detection alone, or become a ZPP workflow stage authority.

#### Scenario: Invoke workspace management explicitly
- **WHEN** an owner requests cross-repository workspace coordination or the workflow delegates one exact workspace operation
- **THEN** the agent follows `zpp-workspace-management` using ZPP-owned coordination commands without treating the skill as a workflow stage

#### Scenario: Leave workspace management dormant
- **WHEN** a repository session has no explicit cross-repository request or workflow delegation
- **THEN** the skill performs no topology inspection, command invocation, registration, lock, reconciliation, or cleanup

### Requirement: Evidence-backed command and state-root selection
Before proposing or invoking a coordination operation, the workspace-management skill SHALL resolve the exact selected ZPP home from explicit owner input or the documented default and SHALL inspect the relevant repositories, topology, session status, resolved closure, and lockability through ZPP-owned read-only commands. It SHALL use explicit workspace, authority, repository, and path identifiers. It SHALL NOT locate the `openlease` executable, read provider help output, assemble provider argv, supply a provider state-root argument, substitute a repository path for provider state, or infer an ambient durable selection for mutation.

#### Scenario: Use the selected ZPP state root
- **WHEN** an owner selects a ZPP home for a workspace operation
- **THEN** the skill directs the ZPP coordination command at that home and does not reinterpret a repository target as state

#### Scenario: Reject an unavailable command
- **WHEN** the ZPP coordination command surface does not provide the operation needed for a requested workspace action
- **THEN** the skill leaves the action blocked and reports the missing ZPP command instead of inventing syntax or falling back to the provider executable
