## Context

See `proposal.md` for motivation and `specs/codespace-locking/spec.md` for the
complete behavior contract. Codespace state currently assumes every member is
writable, `add` mutates one identity in place, and projection reconciliation
derives ownership from a single claim. The mature utility layer now models
member access, edit operations, successor planning, atomic claim transition,
released debt, and current-to-successor projection transfer.

## Goals / Non-Goals

**Goals:**

- Compose the mature utilities into complete lock, edit, status, projection,
  environment, and cooperative guard behavior.
- Make every edit mutation transactional from the durable claim index's point
  of view and recover external resources on failure.
- Preserve old state compatibility through explicit schema migration.

**Non-Goals:**

- Infer editor folders or arbitrary shell write targets.
- Create worktrees for read-only members or reconcile read-only context.
- Add a second ownership mechanism beyond the machine-local claim index.

## Decisions

### Separate explicit target roles at the CLI boundary

`lock` will map positional paths and workspace members to writable targets and
repeatable `--read-only` values to non-owning targets before resolution. Read-only
resolution stops at the selected repository; writable resolution retains the
existing OpenSpec relation closure. This keeps role policy out of Git inspection
and prevents accidental authority expansion.

### Replace add with one normalized edit transaction

`edit` will collect repeatable `--add`, `--add-read-only`, `--remove`,
`--promote`, and `--demote` values, normalize physical identities, and reject
contradictions before confirmation or mutation. The command computes the whole
successor first. A no-op returns the current identity immediately. Interactive
shape-changing edits confirm the displayed successor and then release of the
old lock; `--yes`/`-y` preauthorizes both.

### Stage resources before one locked identity transition

For a real edit, ZPP creates only newly required generated worktrees,
materializes the successor private registry, and—only when the current view has
one—creates the successor projection. It then uses the file-locked index update
to replace the expected current claim with the successor and append any released
generated-work debt. Failures before that update remove newly created resources;
after success, the superseded projection is removed. Existing generated
worktrees transfer by identity rather than being recreated.

The alternative of unlocking before registration is rejected because it exposes
an ownership gap. Mutating the existing ID is rejected because it loses the edit
boundary and cannot keep released debt anchored to the superseded view.

### Associate activated processes explicitly

Private codespace environments will export the active codespace identity. Guard
evaluation uses that value when present and otherwise infers association only
from a writable current directory. It never infers association from shared
read-only context. This makes read-only guarding deterministic without claiming
that ZPP can police unsupported tools or unrelated processes.

### Keep projection and status as views of the complete membership

Projection members include both access roles, while writable private-store
materialization and ownership discovery filter to writable members. Status
reports role, claim/generation state, recorded commit, current commit, and dirty
state without updating identity when a checkout advances.

## Risks / Trade-offs

- [External worktree or projection creation cannot share the index transaction]
  → Preflight all inputs, stage new resources first, roll them back on failure,
  and remove the old projection only after the durable transition succeeds.
- [A process can bypass cooperative hooks] → Preserve the documented advisory
  boundary and keep exclusivity enforcement in core claim registration.
- [Older state lacks explicit access roles] → Migrate unambiguous legacy members
  to writable and reject ambiguous legacy role data rather than guessing.
- [An edit can leave preserved generated debt] → Keep it under the superseded
  identity until normal cleanup and disposition complete; never delete it in the
  edit transaction.

## Migration Plan

Load version 1 and 2 indexes into version 3 with existing members marked
writable. Write only version 3. The CLI removal of `add` is intentionally
breaking; users use `edit --add` instead. Rollback requires restoring the prior
binary before it writes version 3 state or retaining the version 3 reader.

