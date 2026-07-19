# Proposal: config-empty-hint

## Why

The in-place bootstrap feedback: "self-governed, but `zpp config resolve`
returns an empty configuration" and "No zpp.toml exists… I did not create it
automatically." Both behaviors are correct (self-governed = local `openspec/`
root; owner-authored config is doctrine) — but the owner is told nothing
about *how* to proceed. Lean audit cut the proposed `zpp init` command
(yagni: one-time action, new command surface); what remains is the on-ramp:
a hint at the moment of emptiness, and a template to copy.

## What Changes

- `zpp config resolve` (human output), when the effective config is empty,
  appends a one-line hint: no `zpp.toml` found — author one; see the
  documented template. JSON output is unchanged (agents get the empty object
  as today).
- README gains a commented, copy-paste `zpp.toml` template section
  (governance binding, `[tdd]`/`[bdd]` stack, `[traits] apply`, `[doctor]`) —
  the authoring on-ramp, owner-authored by doctrine.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `governance-resolution`: Layered config resolution — an empty effective
  config carries an authoring hint on the human surface.

## Impact

- `zpp/cli/config.py` (hint on empty), README template section, tests for
  hint presence/absence. No new command, no auto-authoring.
