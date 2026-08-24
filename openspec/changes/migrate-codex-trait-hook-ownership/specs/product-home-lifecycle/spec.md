## ADDED Requirements

### Requirement: Exact legacy hook lifecycle reconciliation
The shared initialization and synchronization boundary SHALL include a bounded
migration check for the former `zpp-session` hook ownership identity without adding
that identity to the current packaged inventory. An intact owned predecessor SHALL
make the current hook eligible for ownership-safe migration in the exact selected
scope. A former hook that is unowned or not intact SHALL remain a reported conflict
and SHALL block retirement claims without blocking inspection of unrelated entries.

Package installation or upgrade alone SHALL perform no hook migration. Grouped
workflow update and root synchronization SHALL migrate only in their explicitly
selected scope, and root initialization SHALL apply the same migration when
reconciling an owned prior-version installation.

#### Scenario: Conformance trace for former user hook migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Exact legacy hook lifecycle reconciliation","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Repair former Codex hook ownership during synchronization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Repair former Codex hook ownership during synchronization`
