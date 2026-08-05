## 1. Public behavior contract

- [x] 1.1 Add bootstrap-root Gherkin coverage for the top-level command, option-free help, initialized-state requirement, profile-only update, hook-only discovery, and init/update helper distinction.
- [x] 1.2 Add workflow-root Gherkin coverage for automatic multi-agent bundle discovery, complete hook/OpenSpec maintenance, absent-bundle preservation, version-aware regeneration, conflicts, idempotence, and local isolation.

## 2. Focused update planning

- [x] 2.1 Reconcile reusable additive default-profile planning so top-level update and global workflow lifecycle retain one preservation and validation contract.
- [x] 2.2 Implement and unit-test exact current/historical native-hook discovery for Pi, Codex, and Claude without treating absence or unrelated configuration as ownership.
- [x] 2.3 Implement and unit-test stable discovery of compatible, outdated, absent, and conflicting global workflow projections across all supported agents.
- [x] 2.4 Implement and unit-test complete per-agent maintenance planning, including absent/matching/changed OpenSpec projections and no implicit workflow installation.

## 3. Atomic core and CLI composition

- [x] 3.1 Compose initialized-state validation, default merge, discovered hooks, workflow bundles, and required isolated OpenSpec generation into one preflighted rollback-capable global mutation.
- [x] 3.2 Add the option-free top-level `zpp update` command with stable diagnostics and register it in the root Typer hierarchy.
- [x] 3.3 Revise `zpp init` and `zpp update` Typer help to distinguish bootstrap, selected-hook setup, installed-state maintenance, and executable upgrade ownership.

## 4. Documentation and verification

- [x] 4.1 Replace the README's multi-command post-upgrade sequence with `uv tool upgrade zpp` followed by `zpp update`, and document its global-only preservation boundaries.
- [x] 4.2 Run focused utility tests, the bootstrap and workflow Behave roots, the complete mapped audit, full pytest, help/version checks, and strict OpenSpec validation.
- [x] 4.3 Reconcile mature behavior into canonical specifications and archive the completed product change through the owning workflow.
