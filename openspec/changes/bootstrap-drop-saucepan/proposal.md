# Proposal: bootstrap-drop-saucepan

## Why

An in-place 1v2 bootstrap failed with HTTP 404 while fetching saucepan —
a tool the run never needed. Two audit rounds grounded the cut: saucepan is
the lowest-precedence trait source, nothing core depends on it, and
`zpp trait fetch` already lazily fetches the binary at its real point of use
(`cli/trait.py` → `sauce.ensure_binary`). Bootstrap pre-fetching it buys
nothing and makes an optional tool's network failure fatal (`manual` →
exit 2) for every bootstrap.

## What Changes

- `zpp bootstrap` stops handling saucepan entirely: it is never fetched,
  never counted as a manual step, and cannot fail the run. First
  `zpp trait fetch` provisions it, as it already does today.
- `zpp doctor` keeps saucepan visible but as a **non-failing optional row**:
  present/absent with mode and provenance, never contributing to doctor's
  exit-1.
- The toolchain table marks saucepan `optional`; the audited round-1
  "conditional opt-in" logic is explicitly not built (round-2 finding:
  delete beats configure).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `environment-bootstrap`: the Managed tool mode requirement — bootstrap no
  longer provisions managed-optional tools; doctor reports them without
  failing on absence.

## Impact

- `zpp/core/toolchain.py` (bootstrap skip + doctor optional row),
  tests/features for both paths. `zpp/core/sauce.py` unchanged (the
  target-triple fix already landed). Fixes the reported bootstrap 404
  structurally: the fetch no longer happens.
