# standard-workflow-traits Specification

## Purpose

Defines the persistent standard-trait profile and its advisory workflow behavior so users can configure, reuse, and activate shared governance without weakening skill-owned enforcement.

## Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands.

The `default` profile SHALL be provisioned as an inactive reusable preset and SHALL NOT participate in trait resolution merely because it exists or because `zpp init` completed. Its trigger configuration SHALL select `automatic-workflow`, `codespace-claim-guard`, `zero-assumptions`, and `ponytail` conditionlessly when the profile explicitly participates. It SHALL select `use-rg`, `use-jq`, and `use-zmem` only through their corresponding executable conditions. The packaged Python, Django, TypeScript, and Flutter workflow traits SHALL remain inactive until explicitly triggered by a user-owned layer.

Persistent use of the preset in the global layer SHALL require `zpp global activate default`. `ZPP_PROFILE=default` SHALL remain an explicit temporary profile selection and SHALL NOT replace or mutate global authored state.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once or preserved unchanged without participating in trait resolution automatically

#### Scenario: Explicitly select the default profile
- **WHEN** a user explicitly selects `default` through `ZPP_PROFILE` or activates it into global
- **THEN** its conditionless base traits and executable-guarded tool traits participate only through the selected temporary or persistent path while platform traits remain manually selected

### Requirement: Executable-guarded tool-use traits
The packaged standard profile SHALL define focused `use-rg`, `use-jq`, and `use-zmem` advisory traits. Its `trait.json` SHALL select them only with the corresponding single fixed conditions `which: rg`, `which: jq`, and `which: zmem`. An unavailable executable SHALL leave only its corresponding trait inactive and SHALL NOT block trait resolution or workflow execution.

#### Scenario: Resolve available tool guidance
- **WHEN** the selected standard profile participates and `rg` is available while `jq` is unavailable
- **THEN** `use-rg` activates, `use-jq` remains inactive, and resolution succeeds

#### Scenario: Keep zmem guidance inactive without the executable
- **WHEN** the selected standard profile participates and `zmem` is unavailable
- **THEN** `use-zmem` remains inactive and resolution and unrelated workflow behavior continue

### Requirement: Proportionate dependency guidance
The packaged Ponytail guidance SHALL preserve the upstream ladder's need, reuse, standard-library, native-platform, installed-dependency, and minimum-code ordering. When no earlier rung satisfies a confirmed non-trivial responsibility, ZPP's utility workflow SHALL additionally investigate maintained third-party packages and compare maturity, integration cost, and the proportion of their feature surface required by the accepted need. It SHALL NOT invent a universal percentage threshold.

#### Scenario: Evaluate an external dependency after earlier rungs fail
- **WHEN** a confirmed utility responsibility is not satisfied by reuse, standard library, native behavior, or an installed dependency
- **THEN** utility planning compares mature external packages against focused custom implementation using proportional requirement coverage before settling the dependency choice

### Requirement: Manually selected platform workflow traits
The packaged standard profile SHALL provide inactive definitions named `python-bdd`, `python-tdd`, `python-build`, `python-django-tdd`, `typescript-bdd`, `typescript-tdd`, `flutter-bdd`, and `flutter-tdd`. None SHALL appear in the packaged standard `trait.json`; a user-owned global, profile, saved, or repository trigger SHALL be required to activate one. Language files or globally available framework commands SHALL NOT automatically select a project's BDD, TDD, or build policy.

#### Scenario: Resolve a project without platform selection
- **WHEN** a selected standard profile supplies platform definitions but no participating user-owned layer triggers one
- **THEN** no Python, Django, TypeScript, or Flutter workflow trait activates

#### Scenario: Select platform policy explicitly
- **WHEN** a participating user-owned layer triggers one or more packaged platform workflow traits
- **THEN** only those selected definitions join the effective trait output through ordinary layer semantics

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
