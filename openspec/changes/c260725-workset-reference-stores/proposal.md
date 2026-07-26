## Why

A workset today knows about exactly one kind of store: the dedicated
governance store that rules its members. But a project often has a second
store worth consulting — a production-environment setup store, for example —
that is useful *knowledge* for certain tasks and not an authority over any
repo. There is nowhere to record that relationship. openspec's registry knows
every store on the machine (7 on this one) but carries no signal about which
are relevant to a given workset, so an agent either ignores them or guesses.

The result is that durable, curated knowledge sits one command away
(`openspec list --specs --store <id>` already works from anywhere) while
being invisible at the moment an agent needs it.

## What Changes

- A workset MAY have **reference stores** assigned to it: registered OpenSpec
  stores that serve as read-only knowledge corpora for tasks.
- Assignment is durable and machine-local, recorded in the sidecar
  (`~/.zpp/worksets/<name>.toml`), with explicit commands to assign and
  unassign by registered store id.
- A reference store is deliberately outside the governance cycle: no traits,
  no config, no policy, no lease, no isolated worktree. Agents read it through
  openspec's own `--store <id>` commands.
- A reference store need NOT be a member of the workspace, so the existing
  at-most-one-dedicated-store rule is untouched.
- `zpp resolve` reports assigned reference stores distinctly from the
  governing store, so a listing can never be read as governance.
- `zpp workset doctor` reports an assignment whose store is unregistered or
  whose root has gone missing; healthy assignments are not reported.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workset-management`: gains reference-store assignment — durable
  machine-local record, assign/unassign commands, non-participation in
  governance, and a doctor anomaly check.
- `governance-resolution`: resolution reports assigned reference stores
  distinctly from the governing store without affecting any resolution
  outcome.

## Impact

- `zpp/core/sidecar.py` — sidecar schema gains the assignment record
  (`version = 2` bump).
- `zpp/core/worksets.py` — assign/unassign, status, doctor anomaly check.
- `zpp/core/governance.py`, `zpp/cli/root.py` — resolve reporting.
- `zpp/cli/workset.py` — new subcommands.
- Consumers: this store's mount script lists what resolve reports (separate
  change in `governance-of-agents-1v2`).

## Governance Provenance

- Decision branch: `governance/c260725-workset-reference-stores`
- Decision ref: `refs/heads/governance/c260725-workset-reference-stores`
- Intended base: `main`
