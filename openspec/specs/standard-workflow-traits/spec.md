# standard-workflow-traits Specification

## Purpose

Defines the persistent standard-trait profile and its advisory workflow behavior so users can configure, reuse, and activate shared governance without weakening skill-owned enforcement.

## Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands. It SHALL activate `automatic-workflow`, `zero-assumptions`, and `ponytail`; independently authored `python-bdd`, `python-tdd`, and `python-build` traits SHALL remain inactive until triggered.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once with the standard trait set or preserved unchanged when it already exists

### Requirement: Configurable advisory progression
Standard traits SHALL provide default frontmatter configuration that `traitsConfig` MAY override without changing activation. `automatic-workflow` SHALL default to automatic and accept `mode: manual`. Automatic mode or explicit end-to-end delegation SHALL continue past satisfied checkpoints, verification, and handoffs without approval. It SHALL pause only for unresolved clarification, a new product boundary, or a missing or changed utility shape.

#### Scenario: Resolve automatic progression guidance
- **WHEN** automatic-workflow participates with its default or overlaid configuration and the user delegates work
- **THEN** its effective guidance reflects the configuration while preserving the advisory and authority boundaries

### Requirement: Advisory and enforcement ownership
Standard traits and passive `skill_lookup` SHALL grant no authority, execute no skill, settle no decision, and bypass no failed gate. Cross-cutting zero-assumption and focused-composition guidance SHALL remain in their independently configurable traits. Stage-specific operations and non-bypassable OpenSpec ownership, verification authority, and zmem materiality SHALL remain in their owning permanent skills.

#### Scenario: Resolve coordinated workflow guidance
- **WHEN** standard traits and permanent workflow skills are installed and resolved
- **THEN** cross-cutting directions come from traits while enforceable stage rules remain skill-owned

### Requirement: Reusable profile copying
`zpp profile copy SOURCE DESTINATION` SHALL copy only the complete validated authored layer from an existing named profile into an absent destination profile. It SHALL preserve the source byte-for-byte, SHALL NOT activate either profile, and SHALL NOT copy or create derived cache or modification-sidecar state.

Missing, invalid, or conflicting profile state SHALL reject the operation without partial writes.

#### Scenario: Copy an authored profile
- **WHEN** a user copies a valid source profile to an available destination
- **THEN** the destination contains the same authored bytes while source, global, and derived state remain unchanged

### Requirement: Persistent global activation
`zpp global activate NAME` SHALL atomically archive global authored state as an unused collision-safe `{YYYYMMDD-HHMMSS}-global` profile and copy the selected valid profile into global. It SHALL preserve the source, leave `ZPP_PROFILE` unchanged, invalidate global derived state, and transfer no cache or sidecar as authored data. Invalid sources or conflicts SHALL reject without partial changes.

#### Scenario: Activate a reusable profile
- **WHEN** a user persistently activates a valid named profile
- **THEN** prior global authored state is archived, selected authored bytes become global, and source and temporary selection remain unchanged

### Requirement: Related change completion boundary
The `automatic-workflow` trait SHALL direct a workflow to treat every OpenSpec
change it selects, creates, or consumes as related workflow state. Before
reporting completion, each related change SHALL be archived, discarded, or
remain active under an identified owning stage.

The related set SHALL remain session-local rather than being persisted in a
product proposal or authored trait. Unrelated active changes SHALL remain
untouched, and workflow completion SHALL NOT require the global active-change
list to be empty.

#### Scenario: Reconcile related changes before completion
- **WHEN** a workflow reaches finalization with related and unrelated OpenSpec changes active
- **THEN** it completes only after every related change has an owned disposition while unrelated changes remain untouched

#### Scenario: Reject an unowned related change
- **WHEN** a consumed related change remains active without an owning stage
- **THEN** the workflow remains incomplete

### Requirement: Distinct workflow authority layers
The standard workflow guidance SHALL identify canonical OpenSpec specifications as the long-standing authority for currently accepted product behavior, an active proposal as mutable working state for its current change, and zmem as the temporal record of meaningful decision changes and highlights rather than current product truth.

#### Scenario: Resolve authority guidance
- **WHEN** the standard workflow traits participate in a change
- **THEN** current behavior, working intent, and temporal history retain their distinct authority roles

Executable public examples for every requirement are maintained in `features/bootstrap_and_agents.feature`, `features/profiles_and_saved.feature`, and `features/workflow_skill_distribution.feature`.
