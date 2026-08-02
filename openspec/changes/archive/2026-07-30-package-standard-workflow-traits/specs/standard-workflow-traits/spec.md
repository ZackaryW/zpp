## Purpose

Defines the persistent standard-trait profile and its advisory workflow behavior so users can configure, reuse, and activate shared governance without weakening skill-owned enforcement.

## ADDED Requirements

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
