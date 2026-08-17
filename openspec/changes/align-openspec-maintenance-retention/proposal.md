## Why

The first maintenance contract made archive removal depend on exhaustive canonical and planning-document mapping, so a dry run produced a large evidence dump and called already-preserved archives only “close” to removable. The owner instead wants a direct preservation, consolidation, aging, and zmem-cancellation policy.

## What Changes

- Treat each archived item as preserved when current behavior exists in canonical OpenSpec or historical/superseded reasoning exists in zmem.
- Remove redundant non-superseded archives after complete preservation is verified, without requiring stale task checkboxes or every planning sentence to be duplicated elsewhere.
- Reconcile canonical requirements that govern the same behavior into one authoritative destination while preserving the strongest accepted contract.
- Give superseded specifications and archives a ten-version grace period, where one version is one later archived change affecting the same capability.
- Cancel a valid zmem decision as soon as current authority proves it superseded, using the exact `zmem(CANCEL)[sha, index]` effect.
- Keep exact-path deletion authorization, strict validation, operation ownership, and local OpenSpec skill-bootstrap prohibitions.
- Require an executive summary and next action before detailed audit evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-maintenance-skill`: Replace the over-constrained archive gate with preservation-source, canonical consolidation, capability-version aging, zmem cancellation, and concise-reporting rules.

## Impact

- Revises the packaged `zpp-maintain-openspec` instructions and maintenance reference.
- Modifies the existing canonical maintenance capability.
- Cancels the superseded repository-memory decision that requires canonical representation for every archive item.
- Adds no executable code, command, dependency, Gherkin, TDD test, archive deletion, or OpenSpec skill bootstrap.
