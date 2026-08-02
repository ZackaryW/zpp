## Context

See `proposal.md` for motivation and `specs/codespace-locking/spec.md` for the behavioral contract. The existing codespace index made workset identity part of active and released ownership state. The replacement spans target discovery, concurrency-safe persistence, worktree planning, lifecycle commands, agent adapters, traits, and the explicit reconciliation skill.

## Goals / Non-Goals

**Goals:**

- Give one machine-local index exclusive authority over effective physical checkout ownership.
- Keep target discovery, claim mutation, worktree materialization, projection maintenance, and CLI orchestration independently testable.
- Preserve safe migration from the prior workset-owned index while bounding future retained state.
- Keep the same claim guard semantics across supported agent adapters without copying policy into their installed hooks.

**Non-Goals:**

- Distributed locking, operating-system sandboxing, or universal interception of filesystem writes.
- Automatic branch reconciliation or inference of merge strategy.
- Editor ownership or automatic discovery of folders from an already-open editor.

## Decisions

### Persist claims and released debt separately

Use a versioned Pydantic index with `claims` for complete active ownership and `released` for only generated-checkout debt. Active members retain source/effective checkout identities, starting commits, store roles, worktree branches, and optional projection metadata. Released entries retain only worktree removal and branch disposition state.

This replaces retaining complete released views. A numeric history cap was rejected because it could discard unresolved work; lifecycle finalization instead removes only fully resolved debt.

### Serialize complete index transformations

Guard every read-transform-validate-write operation with one machine-local file lock and persist through atomic JSON replacement. Claim registration and replacement validate the whole candidate index, including global checkout-key uniqueness, before publishing it.

Per-checkout lock files were rejected because multi-target acquisition would require ordering and rollback across several locks and could expose partial ownership.

### Resolve authority before claim planning

Convert explicit workspace folders or paths into complete physical Git checkouts, then add external governing-store checkouts and deduplicate by effective checkout identity. Repo-local roots remain covered by their project checkout, reference-only stores are omitted, and unknown store roles fail closed.

Using OpenSpec workset membership as discovery input was rejected because a workset is an opening view and can span multiple independent OpenSpec roots without granting write authority.

### Keep side effects outside pure plans

Focused utilities compute claim conflicts, exact-view matches, replacement claims, worktree paths, projection structure, cleanup candidates, and released debt. Core orchestration preflights all paths and branches, materializes worktrees and private registries, and rolls back newly created worktrees when publication fails.

This keeps utility maturity independently testable while allowing the CLI to remain a thin Typer boundary.

### Make worksets replaceable projections

Store only projection generation and structure identity in the active claim. Derive `zpp-<instance>-g<generation>` when opening, reuse it for an unchanged structure, and replace it after structural changes. Mutating boundaries prune generated projection names not represented by the active index while never touching user-owned worksets.

Retaining every historical projection was rejected because it grows with combinations rather than live work.

### Guard supported agent writes cooperatively

Install native agent hooks that resolve current traits at lifecycle boundaries and call the hidden claim guard before supported mutations. Direct writes with explicit target paths can be rejected against the durable index. Shell calls verify current-checkout association but do not attempt command-language path inference.

Agent-specific ownership logic was rejected in favor of one core guard plus a shared platform-neutral trait.

## Risks / Trade-offs

- **[Process termination during worktree materialization]** → Preflight the complete plan, roll back worktrees created by the failed operation, and publish the claim only through a locked atomic index update.
- **[Legacy index ambiguity]** → Migrate version-one workset fields into version-two optional projection metadata and released debt, then validate all uniqueness invariants.
- **[Cooperative guards can be bypassed]** → State the boundary explicitly and retain hard exclusivity between ZPP claims in core.
- **[Stale generated projections remain after external deletion or crashes]** → Prune only provably generated orphan names at later mutating boundaries.
- **[Dirty generated work accumulates]** → Preserve it visibly as released debt until cleanup and explicit branch disposition allow finalization.

## Migration Plan

1. Load version-one indexes through the version-two migration path without rewriting source checkouts or user-owned worksets.
2. Treat migrated owned worksets as optional generation-one projections for active claims and reduce migrated released entries to generated-checkout debt.
3. Use version-two claim operations for every subsequent mutation and atomically persist the upgraded index.
4. Roll back by restoring the prior package version and its index backup; do not delete generated worktrees or branches as part of rollback.
