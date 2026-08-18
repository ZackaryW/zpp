## Why

ZPP's OpenLease integration is document binding only. Across `src/` it calls exactly four OpenLease APIs — `bind_extension_document`, `initialize_extension_document`, `snapshot`, and `bind_extension` — and never `register_repository`, `create_space`, `resolve_session_space`, `set_affected`, `plan`, `lockable`, `lock`, `release`, or `recover`. OpenLease's central guarantee is a blast-surface permit: an agent must declare the surface it intends to affect, OpenLease expands that claim to its closure through the authority graph, checks it, and only then issues a lease. ZPP never arms it, so an agent working under ZPP declares nothing and is stopped by nothing.

The gap is also agent-visible. `zpp-workspace-management` instructs agents to locate the `openlease` executable, read its `--help`, and assemble argv against a prose table, which is why agent sessions reach for OpenLease instead of ZPP's own contracts.

## What Changes

- **BREAKING** ZPP owns the complete OpenLease command surface. The packaged `zpp-workspace-management` skill no longer locates the `openlease` executable, reads its `--help`, or assembles provider argv; `references/workspace-command-contract.md` is replaced by ZPP-owned command guidance. Agents get no route to the OpenLease binary.
- **BREAKING** Repository session establishment registers topology. ZPP files a minimal floorplan for a single repository — registering the repository and one authority covering the worktree — so an affected claim has a graph to resolve against. This supersedes the 2026-08-11 decision that repository trait resolution requires no registration or space selection.
- ZPP keys the session to the worktree rather than consuming `OPENLEASE_SESSION_TOKEN` from the host, offers an explicit session name when a distinct session is wanted, and establishes the session as an OpenLease temporary space over the auto-registered repository.
- ZPP arms the blast-surface permit: before an operation that modifies the worktree, ZPP requires a declared affected claim, resolves its closure, evaluates lockability, and acquires the lease under an explicit go-ahead. Read-only trait resolution stays permit-free on direct invocation-scoped bindings.
- ZPP owns explicit unlock as the guarantee check: a normal boundary-safe release, and a forced path that requires explicit force authority and books reconciliation debt.
- ZPP exposes complete parity of the OpenLease surface, including abandonment, cleanup, handoff, and preparation repair. Destructive operations are gated by ZPP in the CLI through an argument ZPP validates, so a skill instruction alone cannot satisfy the gate.
- Multi-repository work requires explicitly declared relationships — parents, dependencies, and shared authorities — because mere repository existence is now supplied automatically.

## Capabilities

### New Capabilities
- `openlease-session-lifecycle`: Automatic single-repository floorplan registration, ZPP-derived persisted session identity, and temporary-space session establishment and reuse.
- `blast-surface-permit`: Affected-claim declaration, closure resolution, lockability evaluation, permit acquisition before worktree modification, and explicit unlock as the guarantee check.
- `zpp-coordination-commands`: The ZPP-owned command surface covering the complete OpenLease operation set, including CLI-enforced authority for destructive operations.

### Modified Capabilities
- `workspace-management-skill`: Removes provider executable discovery, `--help` interrogation, and the prose argv contract; the skill directs agents to ZPP-owned commands and drops the prohibition on a ZPP-owned workspace command surface.
- `repository-trait-bootstrap`: Repository trait operation establishes a registered session and a temporary space rather than asserting that ordinary resolution never requires registration and never creates or selects a space; read-only document binding itself stays invocation-scoped and permit-free.
- `automatic-trait-hooks`: The packaged session hook establishes the session, so space-scoped sources no longer depend on an externally supplied `--space` or `OPENLEASE_SPACE`.
- `product-home-lifecycle`: The selected home's OpenLease state now holds registered repository topology, authorities, sessions, and leases rather than bound documents alone.

## Impact

- `src/zpp/utils/openlease.py`: extends beyond document binding to registration, session, claim, permit, and disposition operations.
- `src/zpp/cli/`: new coordination command surface; `resolution.py` session establishment replaces `--space`/`OPENLEASE_SPACE` gating as the only route to space-scoped sources.
- `src/zpp/utils/product_home.py`: the OpenLease state child now carries durable topology, so reset boundary handling covers registered state.
- `src/zpp/artifacts/skills/companion/zpp-workspace-management/`: `SKILL.md` rewritten; `references/workspace-command-contract.md` replaced.
- `src/zpp/artifacts/hooks/`: session establishment through the packaged SessionStart hooks for every supported agent.
- OpenLease remains pinned at `f9416008`; this change consumes its existing public API and requires no upstream release.

## Deferred

Recorded as explicitly deferred by the owner. Do not design or implement in this change.

- **Subagent granularity**: whether a subagent inherits its parent's permit or must hold its own. OpenLease excludes a space's own leases from conflict detection, so a subagent resolving to the parent's space is invisible to the guard by construction.
- **Stale session cleanup**: the policy for reclaiming sessions abandoned by crashed or exited agents.
- **Concurrent agent separation**: distinguishing two unnamed concurrent agent sessions in one worktree. No observable channel identifies a host agent session on every supported platform, so unnamed concurrent sessions share one session and an explicit session name is the supported way to separate them.
