# Workspace command contract

Every coordination operation runs through `zpp workspace`. ZPP executes them
against the OpenLease library directly, so this skill never locates a provider
executable, reads provider help, or assembles provider arguments.

## Resolve the home and session

1. The selected ZPP home defaults to `~/.zpp`. Pass root `--path` only when the
   owner named a different home: `zpp --path <home> workspace ...`.
2. Establish or confirm the worktree's session before anything else. The session
   is keyed to the worktree, so repeated invocations reuse it.
3. Use `--session <name>` only when the owner wants a session distinct from the
   worktree's default. Unnamed concurrent work shares one session by design.
4. Read structured output with `jq`. Preserve typed identifiers and fail on
   invalid input.

If a requested operation has no command below, it is unavailable. Report that
and stop. Do not fall back to a provider executable or invent a command.

## Command families

| Purpose | Command | Authority |
| --- | --- | --- |
| Establish or confirm a session | `workspace session [TARGET] [--session NAME]` | Registers this worktree only |
| Observe state | `workspace status [--space ID]` | Read-only |
| Declare a blast surface | `workspace claim --space ID [--repository ID] [--authority ID]` | Records the claim |
| Resolve closure and lockability | `workspace closure --space ID` | Read-only |
| Acquire the permit | `workspace permit --space ID --fingerprint VALUE` | Requires the closure fingerprint |
| Release a permit | `workspace release --space ID` | Verifies boundary safety |
| Force a release | `workspace force-release --space ID --authorize VALUE` | Destructive; explicit authority |
| Declare relationships | `workspace relate --child ID (--parent ID \| --dependency ID [--access ROLE])` | Exact relationship mutation |
| Reconcile | `workspace reconcile --space ID --repository ID [--apply]` | Plan is read-only; apply mutates one path |
| Finalize | `workspace finalize --space ID` | Requires settled reconciliation debt |
| Handoff disposition | `workspace handoff --space ID --disposition VALUE --authorize VALUE` | Destructive; explicit authority |
| Abandon a member | `workspace abandon --space ID --repository ID --authorize VALUE` | Destructive; explicit authority |
| Clean a generated worktree | `workspace cleanup --space ID --repository ID --authorize VALUE` | Destructive; explicit authority |
| Repair preparation | `workspace preparation --space ID [--rollback --authorize VALUE]` | Rollback is destructive |

Registration is automatic for the worktree that establishes a session. What makes
work cross-repository is a declared relationship, so `workspace relate` is the
explicit step before a session may claim another repository.

## Permit sequence

`claim` records the intended surface. `closure` expands it through the authority
graph and reports `lockable`, every conflict, every blocker, every promotion
issue, and a `fingerprint`. `permit` accepts only that fingerprint, so a closure
that changed after it was shown cannot be acquired against.

Read-only work needs none of this. Trait resolution and behavior verification
require no claim and hold no lease.

## Mutation gate

Before invoking a mutating command, preserve an evidence record with:

- the selected ZPP home and the established session;
- the exact workspace, authority, repository, relationship, lease, successor,
  reconciliation path, and filesystem targets affected;
- the current status and closure output, including the fingerprint;
- the proposed command exactly as it will be invoked;
- explicit owner authority covering every affected target;
- the rollback, recovery, or retained-state consequence current evidence reports.

Re-inspect after execution. Do not reuse a closure or reconciliation plan after
its observed state changes. Do not widen an authorized target set, choose a
callback, resolve a conflict, or perform destructive cleanup because another
workflow gate passed. For every destructive command, `--authorize` is validated
by ZPP; nothing written here can satisfy that gate on the owner's behalf.
