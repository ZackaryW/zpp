## MODIFIED Requirements

### Requirement: Explicit component delegation
Before performing an OpenSpec operation, the consolidated workflow skill SHALL name and follow the installed OpenSpec skill that owns that operation: `openspec-explore` for exploration, `openspec-propose` for creating a change and its planning artifacts, `openspec-update-change` for revising existing planning artifacts, `openspec-apply-change` for implementing change tasks, `openspec-sync-specs` for synchronizing delta specifications without archival, and `openspec-archive-change` for archiving a completed change. These skills SHALL remain component operation integrations and SHALL NOT become ZPP workflow stage authorities. The consolidated workflow skill SHALL use OpenLease only through its public coordination and configuration contracts and Agent Router only through its public discovery and projection contracts.

#### Scenario: Create a product change without a space
- **WHEN** the workflow creates repository-local OpenSpec planning without an explicitly requested OpenLease space
- **THEN** it follows `openspec-propose` and does not create or select a space

#### Scenario: Select an exact OpenSpec operation owner
- **WHEN** the workflow must explore requirements, create or revise planning, implement tasks, synchronize specifications, or archive a completed change
- **THEN** it follows the exact installed OpenSpec skill named for that operation without treating the skill as a ZPP workflow stage authority

## ADDED Requirements

### Requirement: Evidence-based stage eligibility assessment
Before executing any workflow stage, the consolidated workflow skill SHALL present an explicit eligibility assessment for the current accepted contract revision. The assessment SHALL identify the explicitly requested stage, the current evidence-backed outcome of every predecessor stage, any missing, stale, failed, or superseded checkpoint, and the output the requested stage owns for the accepted change. A stage name supplied by an owner or proposed by an agent SHALL be dispatch input only and SHALL NOT satisfy the stage's eligibility, any predecessor gate, verification, or mutation authority.

The skill SHALL block a requested stage when any required predecessor outcome is absent, stale, failed, or derived from a superseded contract. It MAY identify the earliest unsatisfied predecessor but SHALL NOT execute it without a new explicit stage invocation unless separate end-to-end progression authority is already in force. A changed contract SHALL return to clarification and invalidate every downstream assessment derived from the older contract revision.

#### Scenario: Reject a named stage with an unsatisfied predecessor
- **WHEN** an owner or agent names a later workflow stage but a required predecessor has no current evidence-backed outcome
- **THEN** the workflow reports the requested stage as blocked and does not treat its name as gate satisfaction

#### Scenario: Reject stale checkpoint evidence
- **WHEN** a newer accepted contract changes an outcome from which downstream stage assessments were derived
- **THEN** the workflow reopens clarification and refuses to execute those stages until replacement predecessor outcomes are established

#### Scenario: Preserve explicit invocation after identifying a blocker
- **WHEN** an eligibility assessment identifies the earliest unsatisfied predecessor without separate end-to-end progression authority
- **THEN** the workflow reports that predecessor but does not execute it until the owner explicitly invokes the stage

### Requirement: Effect-based conditional-stage applicability
Before assessing `shape`, `plan-utilities`, `mature-utilities`, or `wire`, the consolidated workflow skill SHALL classify the complete accepted change by its effects: externally observable public or integration behavior, pure executable utility behavior, executable artifact processing or update behavior, spec-governed prose, and ungoverned artifact text. It SHALL decide each conditional stage from the output that stage owns for those effects and SHALL NOT infer test obligations from a filename, artifact category, selected trait, or generic workflow convention.

A change limited to spec-governed skill prose, environment guidance, or equivalent declarative instructions SHALL require no Gherkin, BDD execution, utility plan, unit TDD, or product wiring. Such a change SHALL still complete `form-specs` when an accepted delta requires canonical reconciliation. A change to executable loading, parsing, validation, conversion, projection, or update mechanics SHALL remain eligible for behavior or unit verification at its actual executable boundary and SHALL NOT be skipped merely because it operates on a skill or environment artifact.

#### Scenario: Skip behavior and utility work for governed prose
- **WHEN** an accepted change alters only spec-governed skill prose or environment guidance and changes no executable behavior
- **THEN** `shape`, `plan-utilities`, `mature-utilities`, and `wire` are each assessed as `skipped: not applicable` without creating Gherkin, BDD, a utility plan, unit tests, or bindings

#### Scenario: Reconcile governed prose specifications
- **WHEN** a prose-only spec-governed artifact change contains an accepted capability delta
- **THEN** `form-specs` remains required even though behavior and utility stages are not applicable

#### Scenario: Test executable artifact update behavior
- **WHEN** an accepted change alters executable loading, validation, projection, or update mechanics for a skill or environment artifact
- **THEN** the workflow assesses the relevant behavior or utility stages from that executable boundary instead of skipping them because of the artifact label
