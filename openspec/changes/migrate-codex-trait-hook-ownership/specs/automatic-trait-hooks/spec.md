## ADDED Requirements

### Requirement: Ownership-safe former hook migration
During initialization and synchronization, ZPP SHALL recognize the exact former
`zpp-session` hook identity only when Agent Router reports that identity as an intact
owned projection at the selected Codex destination. ZPP SHALL remove that owned
predecessor through Agent Router and install `zpp-traits` through Agent Router in the
same selected scope. ZPP SHALL preserve the destination when the former identity is
absent, unmanaged, modified, ambiguous, conflicting, or cannot be inspected.

Confirmed reset SHALL remain limited to `zpp-traits` and SHALL NOT search for or
remove `zpp-session`.

#### Scenario: Conformance trace for former project hook migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Ownership-safe former hook migration","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Update an intact former Codex hook identity in place"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Update an intact former Codex hook identity in place`

#### Scenario: Preserve an unowned former Codex hook
- **WHEN** the native Codex hook fragment has no intact Agent Router ownership for `zpp-session`
- **THEN** synchronization preserves the destination and does not claim migration
