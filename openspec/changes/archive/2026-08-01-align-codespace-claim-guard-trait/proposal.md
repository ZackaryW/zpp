## Why

The canonical codespace contract already requires configured agent guards to reject writes into both foreign claims and associated read-only members, but the packaged `codespace-claim-guard` advisory mentions only foreign claims. Existing user-owned `default` and global projections can therefore also lack the trait introduced after their initial bootstrap, and the globally installed 0.9.0 executable cannot read the current codespace schema.

## What Changes

- Align the packaged platform-neutral claim-guard trait with the existing codespace authority by naming associated read-only members as rejected mutation targets.
- Add executable regression coverage for the complete packaged default trigger set and claim-guard guidance.
- Repair this user's existing default profile additively, reactivate it into global through the existing archival lifecycle, and reinstall the current implementation as the global CLI.
- Preserve the existing contract that initialization never overwrites an existing user-owned `default` profile.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The existing `codespace-locking` specification already owns the required behavior; this change restores implementation and installed-projection conformance.

## Impact

Affected surfaces are the packaged default trait artifact, its executable feature coverage, the current user's default/global authored layers, and the globally installed ZPP executable. Core claim semantics, profile initialization ownership, and public CLI shape do not change.
