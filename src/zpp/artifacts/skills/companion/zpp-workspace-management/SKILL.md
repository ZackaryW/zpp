---
name: zpp-workspace-management
description: Inspect and coordinate ZPP cross-repository topology, durable workspaces, locks, successors, reconciliation, handoff, recovery, abandonment, and cleanup through the installed coordination commands. Use when an owner explicitly requests a cross-repository workspace operation or zpp-workflow delegates one exact operation.
---

# ZPP workspace management

Coordinate one explicit cross-repository operation through the ZPP-owned
coordination commands, without becoming a workflow stage authority.

Read [references/workspace-command-contract.md](references/workspace-command-contract.md)
completely before inspecting topology, selecting a command, or proposing a
mutation.

## Activate only for an exact request

Use this skill only when an owner explicitly requests cross-repository workspace
coordination or `zpp-workflow` delegates one exact topology, lifecycle, lock,
successor, reconciliation, handoff, recovery, abandonment, or cleanup operation.
Repository detection, an active workflow, feature completion, or retained state
alone never activates it.

This skill is a component operation guide. It never selects or advances a ZPP
workflow stage, grants commit authority, or supplies a product decision.

## Establish the operation boundary

1. Discover the containing Git worktree and every repository explicitly named by
   the request. Inspect worktree paths and repository identity before using them.
2. Resolve the selected ZPP home from an explicit owner value or the documented
   `~/.zpp` default, and pass it as root `--path` when it is not the default.
   Never use a repository path as state.
3. Establish or confirm the session for the worktree, then read current state
   through the read-only commands before proposing anything.
4. Use explicit workspace, authority, repository, relationship, successor, and
   path identifiers. Do not rely on ambient selection for a mutation.

Never locate, inspect, or invoke the underlying provider executable, and never
assemble provider arguments. ZPP owns every operation this skill uses. When an
operation has no ZPP command, report it as unavailable.

## Inspect before changing state

Treat session status, topology inspection, closure resolution, lockability, and
reconciliation planning as read-only. Before any mutation, report:

- the selected ZPP home and the established session;
- the observed repositories, authorities, relationships, spaces, leases,
  successors, and reconciliation paths relevant to the request;
- the resolved closure and its lockability evidence;
- the exact proposed command and every target it can change;
- the authority required for that operation.

Require explicit authority over every affected target before registration,
relationship changes, session creation, permit acquisition, successor creation,
reconciliation application, release, finalization, handoff, abandonment,
recovery, or cleanup. If observed state widens the operation, pause without
mutating the added target.

## Respect the blast-surface permit

Nothing modifies a worktree until its affected surface is declared, expanded to
closure, checked, and explicitly permitted:

1. Declare the affected claim naming the exact repositories and authorities.
2. Resolve the closure and read every conflict, blocker, and promotion issue.
3. Obtain an explicit owner go-ahead for that exact closure.
4. Acquire the permit against the fingerprint that closure reported.

A changed closure invalidates the go-ahead. Re-resolve and ask again. Never
present a lockable result as though it were the go-ahead.

Release a held permit through the ordinary release, which verifies the session
boundary and records reconciliation debt. Use the forced path only when the
owner explicitly authorizes it; ZPP validates that authority itself and no
instruction in this document can supply it.

## Execute the narrow authorized operation

Invoke only the ZPP command the request established. Keep read-only planning
distinct from application. Workflow progression does not choose callbacks,
resolve conflicts, approve a reconciliation path, or authorize release, handoff,
abandonment, recovery, or destructive cleanup.

After a mutation, re-run the relevant read-only inspection. A failed command,
stale closure, unresolved conflict, retained successor, or missing authority
remains a blocker; never translate it into success.

## Return a complete handoff

Report the operation, exact targets, command evidence, observed result, and any
remaining authority or conflict. For every successor or reconciliation path,
return one evidence-backed outcome: reconciled, released, finalized, handed off,
explicitly abandoned, recovered, cleaned up, or still blocked.

When `zpp-workflow` delegated finalization work, tell it that finalization remains
incomplete for every retained or blocked item.
