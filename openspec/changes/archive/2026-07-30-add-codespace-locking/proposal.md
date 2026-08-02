## Why

Developers can open overlapping combinations of projects and responsibility-specific OpenSpec stores concurrently, causing shared-checkout writes and branch conflicts. The former ZPP workset wrapper overbuilt this problem by mixing view composition, governance configuration, store roles, session provisioning, and long-lived leases; ZPP instead needs an explicit, on-demand conflict gate that preserves the simple canonical-checkout path when no contention exists.

## What Changes

- Add a `zpp codespace` command group for explicit, on-demand claims over an
  OpenSpec working view. An uncontested view keeps canonical checkouts; ZPP
  creates isolated worktrees only to mitigate confirmed overlap.
- Resolve the complete writable project and governing-store closure while
  leaving reference-only stores shared. Keep ordered commit snapshots,
  physical-checkout ownership, and unique codespace instances as distinct
  identities.
- Project each effective view into an owned OpenSpec workset. Mitigated views
  use a private OpenSpec registry that preserves logical store IDs without
  rewriting shared global registration.
- Provide lock, add, list, status, optional open, activate, exec, unlock, and
  cleanup behavior with atomic replacement and work-preserving failure,
  release, recovery, and cleanup boundaries.
- Package an explicit worktree-reconciliation skill and retain the branch
  metadata it needs. Codespace lifecycle operations never merge isolated work
  automatically.
- Keep the former workset-owned profile, governance sidecar, dedicated-store,
  generated-session-workset, and always-on isolation models retired.

Executable public behavior and edge cases are maintained in
`features/codespace_locking.feature` and
`features/workflow_skill_distribution.feature`.

## Capabilities

### New Capabilities

- `codespace-locking`: Explicit codespace discovery and claims, multi-project and multi-store conflict detection, confirmed worktree mitigation, OpenSpec workset projection, optional opening, and codespace lifecycle behavior.

### Modified Capabilities

- `workflow-skill-distribution`: Extend the permanent workflow bundle with the explicit codespace worktree-reconciliation skill and preserve its required codespace metadata contract.

## Impact

- Adds a public `zpp codespace` CLI surface.
- Introduces local codespace claim and effective-path state owned by ZPP.
- Adds a permanent workflow skill governing explicit reconciliation of isolated codespace worktrees.
- Integrates with OpenSpec's local workset and registered-store facilities without making OpenSpec-owned files carry ZPP semantics.
- Introduces private codespace activation or wrapped OpenSpec execution for mitigated store resolution.
- Requires Git repository/worktree identity, branch creation, safe worktree placement, and cleanup boundaries.
- May optionally invoke supported editor or agent openers after mitigation, but ordinary opening remains outside ZPP ownership.

## Unresolved — Do Not Assume

None.
