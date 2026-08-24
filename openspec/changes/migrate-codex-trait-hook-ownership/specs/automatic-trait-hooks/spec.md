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

#### Scenario: Migrate an intact former Codex hook during synchronization
- **WHEN** a Codex integration contains the packaged hook fragment under intact Agent Router ownership for `zpp-session`
- **THEN** synchronization replaces that ownership with `zpp-traits` through Agent Router and leaves no former ownership record

#### Scenario: Preserve an unowned former Codex hook
- **WHEN** the native Codex hook fragment has no intact Agent Router ownership for `zpp-session`
- **THEN** synchronization preserves the destination and does not claim migration

