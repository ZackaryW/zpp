# Design: bootstrap-drop-saucepan

## Context

Bootstrap treats every toolchain-table entry as required: a managed tool that
cannot fetch lands in `manual` → exit 2. The owner's in-place update hit
exactly this via the (since-fixed) saucepan asset-name 404. Two lean-audit
rounds converged on removal: the round-1 "opt-in when configured" scope lost
to the round-2 finding that `zpp trait fetch` already lazy-fetches at the
real point of use.

## Goals / Non-Goals

**Goals:**
- Bootstrap can never fail on an optional tool; the saucepan fetch simply
  does not happen there.
- Doctor stays honest: saucepan visible with mode/provenance, exit
  unaffected by its absence.

**Non-Goals:**
- No conditional "is saucepan configured?" logic (audited out).
- No change to `sauce.py`, managed-mode fetching, or `zpp trait fetch`.
- No removal of saucepan from the doctor report.

## Decisions

- **`optional: True` on the table row, not special-casing.** The toolchain
  table stays the single source both commands consume; bootstrap skips
  optional rows, doctor excludes them from its failure predicate. Follows the
  existing `detect_only` pattern.
- **Lazy provisioning is the contract.** First `zpp trait fetch` fetches the
  binary (existing behavior, untouched); bootstrap's job is the required
  toolchain only.

## Risks / Trade-offs

- **First `trait fetch` pays the download** on machines that use remote
  packs. Accepted: one-time, at the moment the user actually asked for the
  feature, with a clear "fetching saucepan release binary" message already in
  place.
