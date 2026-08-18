## Context

ZPP's OpenLease usage is confined to `src/zpp/utils/openlease.py` and consists of four calls: `bind_extension_document`, `initialize_extension_document`, `snapshot`, and `bind_extension`. Registration, spaces, sessions, affected claims, leases, reconciliation, and disposition are never invoked. The `zpp.traits` and `zpp.behave` extensions are registered and their documents bound directly, which is why repository trait resolution works with no topology at all.

OpenLease's guarantee is a permit, not a lock. `_affected_plan` refuses two ways before producing anything: `"an explicit affected claim is required"` when a space names no affected repositories or authorities, and `"an explicit authority graph is required"` when no authorities are registered. `resolve_affected_claim` then expands the claim through the validated `AuthorityGraph` — repositories, authorities, parent relationships, and typed dependencies — into a closure. `lockable` reports that closure with conflicts, blockers, and promotion issues; `lock` writes a `LeaseRecord` per held authority and calls `promote_temporary_space`. Conflict detection in `_conflicts` filters `item.owner_id != owner_id`, so a space never conflicts with itself.

Session support already exists upstream. `resolve_session_space(cwd, session_token)` fingerprints a token with SHA-256, calls `resolve_registered_worktree` to find the single registered repository whose `common_dir` matches the checkout, and creates or reclaims a `SpaceRecord` carrying a `TemporarySpaceDescriptor(repository_id, worktree_path, session_fingerprint)`. Reclaim is guarded by `is_disposable_temporary_space`, which requires `draft` status, no held authorities, no generated members, no projection, no preparation artifacts, no blockers, and no handoff disposition.

The prior contract went the other way. The 2026-08-11 `restore-behavior-verification` change established that invocation-scoped direct bindings remove the need to create or select a space, and `ac8bf9d` recorded that cross-repository operations belong to `zpp-workspace-management` using the installed coordination commands internally. Both are superseded here.

OpenLease is pinned at `f9416008` in `pyproject.toml`. This change consumes its existing public API only.

## Goals / Non-Goals

**Goals:**

- Arm the blast-surface permit so a modification under ZPP requires a declared claim, a resolved closure, a lockability check, and an explicit go-ahead.
- Give a single repository a working permit path automatically, by registering the repository and one worktree-covering authority.
- Make ZPP the only route an agent needs, removing provider executable discovery from the packaged skill.
- Keep read-only trait resolution as fast and unconditional as it is today.

**Non-Goals:**

- Subagent granularity. Whether a subagent inherits its parent's permit or holds its own is deferred; the current model makes a subagent invisible to conflict detection because it resolves to the parent's space.
- Stale session cleanup policy for crashed or exited agents.
- Any change to OpenLease itself, or a version bump away from `f9416008`.
- Replacing direct document bindings. They remain correct for read-only trait and behavior document access.

## Decisions

**Register automatically instead of lifting the upstream requirement.** `resolve_registered_worktree` requires exactly one registered repository matching the worktree's `common_dir`, and `_affected_plan` requires a non-empty authority graph. Rather than change OpenLease, ZPP registers what the permit desk needs: the repository and one authority covering the worktree. The alternative — leaving single repositories unregistered — would leave the permit guard inoperative in the tier where nearly all agent editing happens. The alternative of lifting the requirement upstream would block this change on an OpenLease release.

**Registration supplies existence; relationships stay explicit.** Automatic registration declares no parent, no dependency, and no authority beyond the worktree. Multi-repository work is gated on those relationships, which preserves the owner's boundary: what makes work cross-repository is a declared relationship, not the mere fact that two repositories are known.

**ZPP derives session identity rather than consuming `OPENLEASE_SESSION_TOKEN`.** The upstream CLI takes the token from the environment. ZPP deriving and persisting its own identity keeps sessions automatic where no host exports a token, and keeps the identity in the temporary-space key so two concurrent host sessions in one worktree get distinct spaces instead of displacing each other. Keying on the worktree alone was rejected for exactly that reason.

**Identifiers are derived deterministically from the worktree.** `register_repository` raises on a duplicate identifier and `register_authority` likewise, so idempotent establishment depends on deriving stable identifiers and treating an existing matching registration as reuse rather than error.

**The permit is acquired before modification, not at session start.** Establishing a session creates a `draft` temporary space holding no authorities, which is why `is_disposable_temporary_space` requires `not space.held_authority_ids`. Read-only resolution therefore costs nothing and blocks nobody. Locking at session start was rejected because a session that only reads would exclude every other session.

**Unlock maps onto the two upstream paths.** `release` runs `_assert_boundary_safe`, drops leases, and records `ReconciliationRecord` for generated members. `recover` raises `"recovery requires explicit force authority"` unless `force=True`, then does the same while booking reconciliation debt. ZPP exposes both and validates the force argument itself.

**Destructive authority is enforced in the CLI, not in prose.** The current contract states destructive authority as skill guidance, which an agent that never loads the skill does not see. Moving the gate into an argument ZPP validates makes the guarantee hold regardless of what the agent read.

**The skill keeps its authority discipline and loses its provider knowledge.** `zpp-workspace-management` remains explicit-activation-only and remains a component guide rather than a workflow stage. What it loses is executable discovery, `--help` interrogation, state-root plumbing, and the argv classification table.

## Risks / Trade-offs

[Every repository becomes registered, so `~/.zpp/openlease` accumulates topology] → Registration is idempotent and derived from the worktree, and the existing complete-reset path already replaces the whole `openlease` child. Stale session accumulation is separately deferred and tracked.

[A SessionStart hook now writes durable state on every agent session] → Establishment is idempotent, creates only a `draft` space holding no authorities, and reclaims a disposable prior session for the same identity rather than appending. `StateRepository.mutate` serializes writes under a `FileLock` with generation checks and atomic replacement, and `resolve_session_space` already retries on `StaleStateError`.

[Deriving session identity is host-dependent and may be wrong across agents] → The identity must be stable within one host agent session and distinct across concurrent ones. Getting this wrong degrades toward either shared sessions or session churn, both observable through session status; the spec fixes both properties as scenarios.

[Complete surface parity means ZPP tracks OpenLease drift across every family] → ZPP calls the library API rather than assembling argv, so a signature change surfaces as an import or call error at build and test time rather than as a malformed command at runtime.

[A subagent still slips past the guard] → Explicitly deferred and recorded in the proposal. Conflict detection excludes a space's own leases, so this cannot be closed without deciding subagent granularity first.

[Requiring a declared claim before modification may block ordinary workflow work] → Read-only resolution, trait reading, and `zpp behave` are exempt by specification. Only operations that modify a worktree under a session require a claim.

## Migration Plan

1. Extend the OpenLease adapter with registration, session, claim, permit, and disposition operations alongside the existing document binding.
2. Add the ZPP coordination command surface, with destructive operations gated on a validated authority argument.
3. Establish the session in `resolve`, replacing `--space`/`OPENLEASE_SPACE` as the only route to space-scoped sources while keeping both as explicit overrides.
4. Rewrite `zpp-workspace-management/SKILL.md` and replace `references/workspace-command-contract.md`.
5. Reconcile canonical specifications and cancel the superseded decisions in repository memory.

Rollback is the reverse of step 3: without session establishment in `resolve`, the direct-binding path remains fully functional, because it never depended on topology.

## Open Questions

Both are recorded as owner-deferred in the proposal and are out of scope here:

- Subagent granularity — inherit the parent's permit, or hold a distinct one.
- Stale session cleanup — how sessions abandoned by crashed or exited agents are reclaimed.
