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

#### Scenario: Reconcile former hook ownership in user scope
- **WHEN** root synchronization inspects a user-scope Codex integration with intact `zpp-session` ownership
- **THEN** it installs and verifies `zpp-traits` ownership in user scope and retires only the exact former ownership

#### Scenario: Keep hook migration scope bounded
- **WHEN** grouped workflow update selects one project scope containing intact former hook ownership
- **THEN** reconciliation changes only that project hook and inspects no user-scope hook

