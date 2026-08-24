## Why

Existing Codex integrations can carry the current `zpp-traits` hook fragment under
Agent Router's former `zpp-session` ownership identity. ZPP then classifies the hook
as unmanaged and preserves it during synchronization instead of completing the
current owned integration.

## What Changes

- Recognize the exact Agent Router-owned `zpp-session` hook as the predecessor of
  `zpp-traits` during initialization and grouped workflow update.
- Replace that predecessor ownership atomically through Agent Router when its native
  fragment is intact and matches the accepted migration boundary.
- Continue preserving genuinely unmanaged, modified, ambiguous, or conflicting hook
  destinations.
- Keep confirmed reset limited to the current `zpp-traits` identity; reset does not
  search for or remove the former hook identity.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `automatic-trait-hooks`: Add ownership-safe predecessor migration for the former
  Codex hook identity during install/update lifecycle operations.
- `product-home-lifecycle`: Include exact obsolete hook ownership in initialization
  and synchronization reconciliation without broadening reset.

## Impact

Affected areas include lifecycle inventory and reconciliation, the Agent Router hook
adapter boundary, Codex lifecycle Behave fixtures and bindings, focused unit tests,
and the two canonical specifications named above. No dependency or public command is
added.
