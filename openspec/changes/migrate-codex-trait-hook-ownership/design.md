## Context

See `proposal.md` for motivation. The current Codex hook fragment can be present in
`.codex/hooks.json` while Agent Router ownership remains keyed by `zpp-session`.
Inspecting the packaged `zpp-traits` hook alone therefore reports `unmanaged`, and
the generic lifecycle selector correctly preserves it.

Agent Router already exposes ownership-aware inspection, removal, and installation
for hook identities. ZPP must compose those operations without reading or writing the
native hook or ownership documents itself.

## Goals / Non-Goals

**Goals:**

- Detect only the exact intact Agent Router-owned former identity.
- Migrate through public Agent Router hook operations in the selected scope.
- Reuse the shared lifecycle inventory and reporting model.

**Non-Goals:**

- Adopt arbitrary or unmanaged Codex hooks.
- Add `zpp-session` to the current packaged inventory.
- Change reset behavior or Codex's hook format.
- Repair modified legacy hooks.

## Decisions

### Model the former identity as migration evidence, not a packaged asset

ZPP will derive a typed former-hook value from the current packaged hook with only
the ownership name changed. It is used exclusively for Agent Router inspection and
removal. This keeps one native fragment authority and avoids restoring a distributable
legacy hook file.

Alternative: package a second legacy hook artifact. Rejected because it would blur
the hard-cut current inventory and allow the two fragments to drift.

### Promote only an intact owned predecessor into an outdated current entry

The lifecycle adapter will combine two read-only observations: current `zpp-traits`
must appear unmanaged because the fragment is present, and former `zpp-session` must
appear current under Agent Router ownership. Only that conjunction is migration-ready.
The entry is then reported as outdated so established reconciliation selects it.

Alternative: teach generic selection that every unmanaged hook is migratable.
Rejected because that would violate ownership preservation.

### Perform migration with ownership-safe removal followed by installation

The selected projection operation will remove `zpp-session` through Agent Router and
then install `zpp-traits` through Agent Router. This mirrors the repository's existing
owned re-projection convention and keeps native adaptation outside ZPP.

Alternative: rewrite Agent Router ownership or `.codex/hooks.json` directly. Rejected
because ZPP does not own either storage contract.

## Risks / Trade-offs

- Removal succeeds but installation fails → Report projection failure; a later
  lifecycle retry can install the now-absent current hook without adopting content.
- Two inspections could observe changing external state → Revalidate inside the
  migration operation and let Agent Router reject any ownership conflict.
- Legacy handling leaks into reset → Keep the migration adapter out of reset's exact
  current-only removal path and cover that boundary with existing reset tests.

## Migration Plan

Ship the lifecycle adapter and regression scenarios together. Users run `zpp sync`
or scoped `zpp workflow update`; no package-install side effect is introduced. A
rollback restores the earlier behavior, which preserves the stale predecessor rather
than deleting it.
