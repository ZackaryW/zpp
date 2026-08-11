## Context

ZPP 2.0 currently treats root `--path` as an OpenLease state directory and defaults it to `~/.openlease`. OpenLease creates state lazily, while Agent Router independently owns user- and project-scope workflow skill and hook projections. The former ZPP reset combined state replacement with complete user-scope cleanup, but it also carried obsolete global authored-trait behavior that does not exist in 2.0.

The restored boundary must coordinate two owners without reproducing either component: ZPP selects the exact assets and state location, Agent Router proves and removes its projections, and OpenLease initializes its own state. Repository traits and behavior documents remain direct repository extensions outside product-home reset.

## Goals / Non-Goals

**Goals:**

- Establish one selected ZPP home with OpenLease state at its `openlease` child.
- Open that home explicitly through the native file manager.
- Restore a confirmed complete reset that preflights every supported agent's user integration before mutation.
- Replace only OpenLease-managed state after projection cleanup succeeds.
- Preserve retry safety, visible conflicts, and component ownership.

**Non-Goals:**

- Restoring a ZPP 1.x global authored-trait collection or `--overwrite-global-traits`.
- Resetting repository documents, project-scope projections, plugins, worktrees, or unrelated agent assets.
- Adding a mirrored OpenLease lifecycle or directly deleting Agent Router destinations.
- Interpreting or validating arbitrary files merely because the user opens the ZPP home.

## Decisions

### Treat `--path` as the ZPP home

Runtime context will retain the selected home and derive `state_root = home / "openlease"`. The default home is `Path.home() / ".zpp"`. Every existing OpenLease-backed CLI surface receives only the derived state root.

This keeps the public path stable for user handling while preventing reset from deleting the complete home. Retaining `~/.openlease` as the home was rejected because it exposes a component directory as the product boundary and provides no safe location for future ZPP-owned files.

### Keep folder opening in a small platform adapter

`zpp open` explicitly creates the selected home directory, rejects an existing non-directory or unsafe symlink boundary, then delegates to the platform-native folder opener. The adapter uses the operating system's argument-safe API or executable without a command shell and is injected in tests. ZPP reports the resolved path and leaves the created directory intact if the external opener fails.

Opening the OpenLease child was rejected because the owner requested the complete `.zpp` home. Automatically opening during init or reset was rejected because external UI effects require their own explicit command.

### Preflight all user-scope projections before reset mutation

Reset constructs each supported agent's packaged `zpp-workflow` skill and `zpp-session` hook, then asks Agent Router to inspect both in user scope. Only absent or ownership-safe removable results may cross the preflight gate. Any unmanaged, modified, ambiguous, conflicting, or inspection-failed asset aborts before any removal or state replacement.

After complete preflight, reset removes every present selected asset through Agent Router in deterministic agent and hook-before-skill order. Ordinary `workflow remove` retains its selected-agent and selected-scope semantics; reset alone owns the complete all-agent user catalog.

### Replace only the derived OpenLease state after cleanup

Reset requires `--yes` before inspection. It validates the selected home and exact `openlease` child against broad, symlinked, or non-directory destructive targets. It prepares a fresh OpenLease state in a safe sibling staging directory before removing projections. After all projection removals succeed, it swaps the prepared state into `<home>/openlease`; the complete ZPP home is never recursively removed.

If preflight or preparation fails, nothing is removed. If a runtime projection removal fails, reset attempts the remaining preflighted removals, reports every result, leaves the prior OpenLease state untouched, and supports an idempotent retry. State swap failure reports recovery state without claiming reset completion.

## Risks / Trade-offs

- **Changing `--path` semantics can surprise preview users** → Document the breaking path boundary and provide `zpp reset --yes` as the explicit current-state recovery operation.
- **Native folder openers differ by platform and desktop availability** → Isolate platform selection, avoid a shell, and preserve the created home when launch fails.
- **Projection removal is not transactionally reversible** → Complete preflight and state preparation happen first; runtime failures are aggregated and leave state unchanged for retry.
- **A broad or symlinked custom home could escape ownership** → Resolve and validate exact boundaries before preparation or deletion and never recursively delete the selected home.
- **Agent Router status vocabulary may evolve** → Interpret removability through an adapter-level predicate covered against the pinned Agent Router contract and surface unknown results as conflicts.

## Migration Plan

1. Add fail-first feature and utility coverage for selected-home routing, native opening, reset confirmation, preflight, failure, retry, and exclusions.
2. Change runtime path derivation and update existing CLI tests from direct state roots to ZPP homes.
3. Add the platform opener and reset orchestration through current OpenLease and Agent Router APIs.
4. Update README guidance and build the distribution.
5. Rollback by removing `open` and `reset` and restoring direct state-root `--path`; repository-authored files remain unaffected either way.

## Open Questions

None.
