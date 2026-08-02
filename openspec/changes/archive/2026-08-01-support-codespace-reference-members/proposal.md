## Why

Codespace claims currently record only writable checkouts, so a repository used
as context cannot participate in the codespace view without being incorrectly
claimed for exclusive writes. ZPP needs an explicit non-owning member type that
keeps reference repositories visible while preserving the claim model's single
purpose: preventing simultaneous writes.

## What Changes

- Let `zpp codespace lock` accept explicitly selected read-only repository paths
  separately from writable paths.
- Let an explicit codespace edit atomically replace the current writable and
  read-only shape, recalculate its identity from that successor shape, and
  retire the superseded active identity without retaining another active view.
- Replace the narrower `zpp codespace add` command with repeatable `edit`
  operations for adding writable or read-only paths, removing paths, and
  promoting or demoting access roles as one atomic shape transition.
- Require two confirmations before an interactive edit replaces an existing
  lock: one for the successor shape and one for releasing the superseded lock;
  let explicit `--yes`/`-y` authority preauthorize both confirmations.
- Retain read-only repositories as codespace view members without adding their
  checkouts or OpenSpec stores to the exclusive writable claim closure.
- Require each read-only repository to have a committed `HEAD`, include its
  recorded commit and access role in successor identity, and never change that
  identity merely because a participating checkout later advances.
- Resolve only explicitly selected read-only repositories, allow one to appear
  in multiple codespaces, and require an explicit codespace identity or active
  environment when the current directory belongs only to read-only context.
- Include read-only members in codespace status and in the optional OpenSpec
  workset projection created by `zpp codespace open`.
- Exclude read-only members from conflict mitigation, generated worktrees,
  writable private-store registration, cleanup debt, and reconciliation.
- Transfer retained generated worktrees to the successor identity, while
  preserving removed generated work and demoted generated branches as released
  reconciliation debt under the superseded identity without deleting content.
- Make supported ZPP agent guards reject direct mutations into read-only members
  of the associated codespace while retaining the existing documented limits of
  cooperative enforcement.
- Preserve the existing positional-path behavior as writable membership.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codespace-locking`: Distinguish exclusive writable claim members from
  non-owning read-only view members throughout acquisition, inspection,
  projection, and cooperative write guarding.

## Impact

- Affects the `zpp codespace lock`, edit confirmation, and codespace membership
  CLI surface.
- Affects codespace target resolution, durable state, identity, projection,
  inspection, private OpenSpec environments, and agent guard evaluation.
- Affects codespace BDD coverage and utility contracts for member planning,
  serialization, conflict detection, and guard decisions.
- Does not introduce filesystem permissions, OS sandboxing, editor ownership, or
  cross-machine enforcement.

## Unresolved — Do Not Assume

None.
