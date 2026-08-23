## MODIFIED Requirements

### Requirement: Agent Router-owned hook lifecycle
Root initialization and grouped workflow lifecycle operations SHALL project and remove the selected agent's complete deterministic packaged workflow skill family and packaged `zpp-traits` hook through Agent Router. Install and update SHALL use Agent Router's skill and hook installation contracts, removal SHALL use its skill and hook uninstallation contracts, and ZPP SHALL NOT write either native destination directly. Confirmed reset SHALL inspect and remove only the new hook identity and SHALL NOT search for, adopt, or remove the former `zpp-session` identity as a compatibility operation.

Grouped `zpp workflow update` SHALL invoke the shared current-plus-obsolete reconciliation in exactly the caller-selected user or project scope. Project-scope update SHALL pass the exact project root through current inspection, obsolete inspection, current-family projection and verification, and owned-obsolete retirement; it SHALL NOT inspect or change user-scope projections. Grouped `zpp workflow install` SHALL remain a first-install operation: it SHALL preflight every current and obsolete destination in the selected scope before mutation, refuse any existing, unmanaged, or conflicting identity without projecting a prefix of the family, and direct an owned existing installation to update. It SHALL report the exact conflict that blocked installation.

#### Scenario: Conformance trace for complete workflow-family installation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Install the complete workflow family and trait hook together"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Install the complete workflow family and trait hook together`

#### Scenario: Conformance trace for complete workflow-family removal
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Remove the complete workflow family and trait hook together"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Remove the complete workflow family and trait hook together`

#### Scenario: Conformance trace for project-scope legacy migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Update an owned old-only project workflow in place"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Update an owned old-only project workflow in place`

#### Scenario: Conformance trace for conflict-safe workflow installation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Agent Router-owned hook lifecycle","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Refuse a conflicting workflow installation before mutation"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Refuse a conflicting workflow installation before mutation`

#### Scenario: Preserve hooks on reset conflict
- **WHEN** any selected `zpp-traits` hook is modified, unmanaged, ambiguous, conflicting, or cannot be inspected
- **THEN** complete reset aborts before removing any hook or changing Bundler state
