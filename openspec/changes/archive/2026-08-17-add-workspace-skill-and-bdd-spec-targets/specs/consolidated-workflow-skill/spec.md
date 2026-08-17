## MODIFIED Requirements

### Requirement: Explicit component delegation
Before performing an OpenSpec operation, the consolidated workflow skill SHALL name and follow the installed OpenSpec skill that owns that operation: `openspec-explore` for exploration, `openspec-propose` for creating a change and its planning artifacts, `openspec-update-change` for revising existing planning artifacts, `openspec-apply-change` for implementing change tasks, `openspec-sync-specs` for synchronizing delta specifications without archival, and `openspec-archive-change` for archiving a completed change. Before performing a cross-repository topology, workspace lifecycle, lock, successor, reconciliation, handoff, recovery, abandonment, or cleanup operation, it SHALL name and follow the installed `zpp-workspace-management` companion skill. These skills SHALL remain component operation integrations and SHALL NOT become ZPP workflow stage authorities. The consolidated workflow skill SHALL use Agent Router only through its public discovery and projection contracts.

#### Scenario: Create a product change without a workspace
- **WHEN** the workflow creates repository-local OpenSpec planning without an explicitly requested cross-repository workspace
- **THEN** it follows `openspec-propose` and does not create or select workspace state

#### Scenario: Select an exact OpenSpec operation owner
- **WHEN** the workflow must explore requirements, create or revise planning, implement tasks, synchronize specifications, or archive a completed change
- **THEN** it follows the exact installed OpenSpec skill named for that operation without treating the skill as a ZPP workflow stage authority

#### Scenario: Delegate a cross-repository workspace operation
- **WHEN** the workflow requires topology, workspace lifecycle, successor, reconciliation, or cleanup work across repositories
- **THEN** it follows `zpp-workspace-management` and does not select commands, callbacks, conflicts, or dispositions on that skill's behalf

## ADDED Requirements

### Requirement: Provider-neutral workflow workspace boundary
The packaged `zpp-workflow` skill metadata and body SHALL describe cross-repository work in ZPP workspace terms, SHALL name `zpp-workspace-management` as its operation owner, and SHALL NOT name OpenLease or embed provider-specific workspace command guidance. Canonical architecture specifications MAY retain the internal provider boundary, and the workspace-management companion skill MAY use its installed commands internally.

#### Scenario: Inspect the general workflow guidance
- **WHEN** an owner inspects the packaged `zpp-workflow` skill
- **THEN** workspace delegation names `zpp-workspace-management` and no OpenLease name or provider command appears in that general workflow artifact

#### Scenario: Finalize retained workspace state
- **WHEN** finalization finds retained cross-repository successor or reconciliation state
- **THEN** the workflow delegates its inspection and authorized disposition to `zpp-workspace-management` and remains incomplete for every blocked retained item

### Requirement: BDD-target canonical specification formation
During `form-specs`, the consolidated workflow skill SHALL replace the repeated body of each OpenSpec scenario with an exact target-form scenario when, and only when, an accepted BDD feature scenario is its executable authority. The target SHALL identify `features/<capability>/<capability>.feature::<scenario name>`, belong to the same capability owner, trace to the requirement, exist exactly, use scenario-selected bindings that exercise the named behavior through the public system, and have relevant passing verification. The target-form OpenSpec scenario SHALL state that the exact feature scenario is executable authority and SHALL NOT repeat its Given/When/Then steps.

Every scenario without qualifying BDD coverage SHALL remain a complete OpenSpec WHEN/THEN scenario. A stale, missing, cross-capability, recorder-only, capability-wide, wording-only, or unverified target SHALL block specification formation rather than justify scenario removal.

#### Scenario: Replace duplicated behavior with an exact BDD target
- **WHEN** an OpenSpec scenario has verified same-capability coverage at `features/<capability>/<capability>.feature::<scenario name>`
- **THEN** canonical formation retains one target-form OpenSpec scenario naming that exact feature and removes the duplicated executable steps

#### Scenario: Preserve a non-BDD specification scenario
- **WHEN** an accepted OpenSpec scenario has no qualifying executable BDD target
- **THEN** canonical formation preserves its complete WHEN/THEN contract in OpenSpec and does not invent feature coverage

#### Scenario: Reject invalid feature authority
- **WHEN** a proposed target is absent, stale, owned by another capability, untraced, unbound, recorder-only, capability-wide, wording-only, or lacks passing relevant verification
- **THEN** canonical formation keeps the specification scenario and leaves `form-specs` incomplete
