## ADDED Requirements

### Requirement: Packaged manual workspace-management guidance
ZPP SHALL package `zpp-workspace-management` as a companion skill for explicit cross-repository topology, workspace lifecycle, lock, successor, reconciliation, handoff, recovery, abandonment, and cleanup requests. The skill SHALL use the existing installed coordination commands internally and SHALL NOT add a `zpp workspace` command, run from an agent hook, activate from repository detection alone, or become a ZPP workflow stage authority.

#### Scenario: Invoke workspace management explicitly
- **WHEN** an owner requests cross-repository workspace coordination or the workflow delegates one exact workspace operation
- **THEN** the agent follows `zpp-workspace-management` without adding a ZPP command or treating the skill as a workflow stage

#### Scenario: Leave workspace management dormant
- **WHEN** a repository session has no explicit cross-repository request or workflow delegation
- **THEN** the skill performs no topology inspection, command invocation, registration, lock, reconciliation, or cleanup

### Requirement: Evidence-backed command and state-root selection
Before prescribing or invoking a coordination command, the workspace-management skill SHALL inspect the installed command surface, resolve the exact selected ZPP home from explicit owner input or the documented default, derive only its `openlease` child as provider state, and inspect the relevant repositories, topology, workspace status, plan, and lockability. It SHALL use explicit workspace, authority, repository, and path identifiers and SHALL NOT invent a command, rely on stale help, substitute a repository path for provider state, or infer an ambient durable selection for mutation.

#### Scenario: Use the selected ZPP state root
- **WHEN** an owner selects a ZPP home for a workspace operation
- **THEN** the skill supplies that home's exact `openlease` child to the installed coordination command and does not reinterpret a repository target as state

#### Scenario: Reject an unavailable command
- **WHEN** installed command evidence does not provide the operation or arguments needed for a requested workspace action
- **THEN** the skill leaves the action blocked and reports the missing command surface instead of inventing syntax or a compatibility operation

### Requirement: Operation-specific workspace authority
The workspace-management skill SHALL treat status, topology inspection, planning, and lockability checks as read-only. It SHALL require explicit authority over every exact affected workspace, authority node, repository, relationship, lease, successor, reconciliation path, or cleanup target before invoking a mutation. Workflow progression or feature completion SHALL NOT grant callback selection, conflict resolution, reconciliation application, release, handoff, abandonment, recovery, or destructive cleanup authority.

#### Scenario: Inspect before mutation
- **WHEN** a requested workspace action can change cross-repository state
- **THEN** the skill first reports the exact observed topology, plan, affected targets, and proposed command before exercising the operation's authority

#### Scenario: Refuse widened workspace mutation
- **WHEN** observed state widens a requested operation to another repository, authority, successor, or reconciliation path
- **THEN** the skill pauses without mutating the widened target and identifies the additional authority required

### Requirement: Complete successor and reconciliation handoff
When workflow finalization delegates retained workspace state, the workspace-management skill SHALL inspect every relevant successor and reconciliation path, distinguish read-only planning from application, and return an evidence-backed outcome for each retained item: reconciled, released, finalized, handed off, explicitly abandoned, recovered, cleaned up, or still blocked. It SHALL NOT convert an unresolved conflict, failed command, retained successor, or missing cleanup authority into workflow completion.

#### Scenario: Reconcile an authorized successor path
- **WHEN** the owner authorizes one exact reconciliation path and its current plan remains valid
- **THEN** the skill applies only that path, re-inspects the workspace state, and reports the observed result to the delegating workflow

#### Scenario: Preserve a blocked successor
- **WHEN** a successor has an unresolved conflict, stale plan, failed command, or missing disposition authority
- **THEN** the skill leaves it retained, reports the blocker, and does not tell the workflow that finalization is complete
