## 1. Session lifecycle utilities

- [x] 1.1 Add deterministic worktree-derived repository and authority identifier derivation, with unit coverage for stability and for distinct worktrees.
- [x] 1.2 Add worktree-keyed session identity with an explicit name override, with unit coverage proving reuse for one worktree and distinctness under an explicit name. Host-session derivation was withdrawn during clarify on platform evidence.
- [x] 1.3 Extend the OpenLease adapter with idempotent repository and worktree-authority registration that reuses an existing matching registration instead of raising.
- [x] 1.4 Extend the adapter with session space establishment over the registered repository. The session is an ordinary space, because binding a space-scoped source clears a temporary descriptor.
- [x] 1.5 Add relationship declaration operations for parents, dependencies, and additional authorities, and reject a cross-repository claim with no declared relationship.

## 2. Blast-surface permit utilities

- [x] 2.1 Add affected-claim declaration against an established session, refusing an undeclared modification.
- [x] 2.2 Add closure resolution and lockability evaluation returning the resolved closure, conflicts, blockers, and promotion issues.
- [x] 2.3 Add permit acquisition requiring an explicit go-ahead for the exact reported closure, refusing a stale closure.
- [x] 2.4 Add normal unlock over the boundary-safe release path and forced unlock requiring validated force authority, both recording reconciliation debt.

## 3. Coordination command surface

- [x] 3.1 Add the ZPP coordination command group covering topology, relationships, sessions, claims, permits, successors, reconciliation, and disposition through the OpenLease library API.
- [x] 3.2 Keep inspection commands read-only and prove they mutate no topology, session, lease, reconciliation, or disposition.
- [x] 3.3 Gate abandonment, cleanup, handoff, forced recovery, and preparation rollback behind an authority argument ZPP validates, and prove a skill or trait body cannot satisfy it.
- [x] 3.4 Refuse widened targets and report the additional targets and authority required.

## 4. Resolution and hook wiring

- [x] 4.1 Establish the session in `resolve` and supply the established space to space-scoped sources when `--space` and `OPENLEASE_SPACE` are absent.
- [x] 4.2 Keep `--space` and `OPENLEASE_SPACE` working as explicit overrides of the established session.
- [x] 4.3 Verify the packaged SessionStart hooks for Claude Code, Codex, Kimi, and Pi establish the session without declaring a claim or acquiring a permit.
- [x] 4.4 Confirm document binding, trait reading, and `zpp behave` still require no claim and no permit.

## 5. Packaged skill artifacts

- [x] 5.1 Rewrite `zpp-workspace-management/SKILL.md` to direct every operation through ZPP coordination commands and remove executable location and help interrogation.
- [x] 5.2 Replace `references/workspace-command-contract.md` with ZPP-owned command guidance and remove the provider argv classification table and state-root plumbing.
- [x] 5.3 Confirm the skill keeps explicit activation, read-only-before-mutation discipline, and its non-stage-authority boundary.

## 6. Verification and reconciliation

- [x] 6.1 Shape and bind feature coverage for session establishment, claim refusal, closure reporting, go-ahead acquisition, and both unlock paths.
- [x] 6.2 Run lint, format, unit tests, the capability BDD roots, and a clean package build through the declared backend. The repository declares no type checker, so no typing gate applies.
- [x] 6.3 Reconcile canonical specifications for the three new capabilities and the four modified capabilities.
- [x] 6.4 Cancel the superseded `ac8bf9d` workspace-ownership decision and the 2026-08-11 space-free trait resolution decision in repository memory.
