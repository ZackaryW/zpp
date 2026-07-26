## Context

zpp models exactly one store relationship: the dedicated governance store, at
most one per workset, which supplies traits and config and owns the isolated
worktree and write lease. openspec's registry separately knows every store on
the machine but says nothing about relevance to a workset. The gap is a
durable statement that "this workset also draws on that store as knowledge."

The clarifying interview established that the desired second relationship is
*not* a second authority. It is a read-only corpus consulted for particular
tasks — the owner's example being a production-environment setup store
alongside a project's governance store.

## Goals / Non-Goals

**Goals:**
- Durably record which reference stores a workset draws on.
- Report them so a session surface can list them without inferring relevance.
- Keep them completely outside the governance cycle.

**Non-Goals:**
- No change to the at-most-one-dedicated-store rule: a reference store is not
  a workspace member, so the rule never applies.
- No per-session activation mechanism. Assignment plus approval-at-use covers
  the need; a third state (registered → assigned → activated) would exist
  only for convenience that has not been measured.
- No traits, config, policy, lease, or worktree for reference stores.
- No new read path: `openspec <cmd> --store <id>` already works from any cwd.

## Decisions

- **Assignment, not activation.** The record states lasting relevance, not a
  mode the user toggles. This was the owner's correction after a
  registry-only design: the registry says what *exists*, the workset record
  says what is *assigned to this work*. Without it, a session surface would
  have to list every registered store, which is both noisy and an invitation
  to ground in an unrelated corpus.
- **Machine-local sidecar, not the shared `.zpp-workset` file.** Which
  reference material a developer draws on is a personal working choice, and
  the sidecar already owns machine-local per-workset state. Keeps the
  committed file untouched.
- **Reference stores are not workspace members.** This is what keeps the
  change small: the four enforcement sites of the one-store rule, the
  member-count schema, and their tests are all untouched. A reference store is
  named by registry id, and its files are reached through openspec.
- **No session activation.** The original motivation for a session-scoped
  override was preventing a session from switching *governance*; that
  motivation disappeared once reference stores became non-governing.
  Approval at the moment of use is also more precise than a flag set in
  advance, since relevance is known only when the task is underway. Accepted
  cost: repeated approvals in a long single-domain session.
- **Doctor reports anomalies only.** Every `zpp workset doctor` finding is a
  `{workset, problem, fix}` record, so listing healthy assignments there would
  miscategorize normal configuration as a defect. Doctor covers the assignment
  that has gone stale — unregistered id, missing root — while the listing of
  healthy assignments belongs to `zpp resolve` and the session surface, which
  report state.
- **Validate at assignment time, read-only.** Assignment checks the id against
  openspec's registry, consistent with the existing rule that zpp never writes
  to the registry.

## Risks / Trade-offs

- [An assigned store's content drifts from what a task assumes] → reference
  stores are read at their ordinary checkout, which is the promoted canonical
  view; no staleness beyond what the store itself publishes.
- [Assignment becomes a dumping ground and the session listing bloats] →
  assignment is explicit and per-workset; the listing carries only assigned
  stores, so growth is a deliberate owner act rather than registry drift.
- [Approval-at-use friction in long single-domain sessions] → accepted
  deliberately; revisit only if measured, at which point a session flag is an
  additive change to this design rather than a rework of it.
