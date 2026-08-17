---
name: zpp-workspace-management
description: Inspect and coordinate ZPP cross-repository topology, durable workspaces, locks, successors, reconciliation, handoff, recovery, abandonment, and cleanup through the installed coordination commands. Use when an owner explicitly requests a cross-repository workspace operation or zpp-workflow delegates one exact operation.
---

# ZPP workspace management

Coordinate one explicit cross-repository operation without adding a `zpp
workspace` facade or becoming a workflow stage authority.

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
   `~/.zpp` default. Derive only its exact `openlease` child as coordination state.
   Never use a repository path as state or infer a different ambient home for a
   durable mutation.
3. Locate the installed `openlease` command in the active project or agent
   environment. Read its current `--help` and the relevant subcommand help before
   prescribing syntax. If the needed surface is unavailable, leave the operation
   blocked instead of inventing a command or compatibility alias.
4. Use explicit workspace, authority, repository, relationship, successor, and
   path identifiers. Do not rely on ambient workspace selection for mutation.

## Inspect before changing state

Treat topology inspection, status, planning, and lockability checks as read-only.
Before any mutation, report:

- the selected ZPP home and exact coordination state root;
- the observed repositories, authorities, relationships, workspace, leases,
  successors, and reconciliation paths relevant to the request;
- the current status, plan, and lockability evidence;
- the exact proposed command and every target it can change;
- the authority required for that operation.

Require explicit authority over every affected target before registration,
relationship changes, workspace creation or association, locking, successor
creation, reconciliation application, release, finalization, handoff,
abandonment, recovery, or cleanup. If observed state widens the operation, pause
without mutating the added target.

## Execute the narrow authorized operation

Invoke only the command established by current installed help and pass the exact
selected-home state root. Keep read-only planning distinct from application.
Workflow progression does not choose callbacks, resolve conflicts, approve a
reconciliation path, or authorize release, handoff, abandonment, recovery, or
destructive cleanup.

After a mutation, re-run the relevant read-only inspection. A failed command,
stale plan, unresolved conflict, retained successor, or missing authority remains
a blocker; never translate it into success.

## Return a complete handoff

Report the operation, exact targets, command evidence, observed result, and any
remaining authority or conflict. For every successor or reconciliation path,
return one evidence-backed outcome: reconciled, released, finalized, handed off,
explicitly abandoned, recovered, cleaned up, or still blocked.

When `zpp-workflow` delegated finalization work, tell it that finalization remains
incomplete for every retained or blocked item.
