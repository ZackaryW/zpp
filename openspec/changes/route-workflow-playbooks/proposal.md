## Why

The current generic ZPP 2 playbook is named `zpp-legacy-workflow`, so automatic
triage conflates genuinely mixed product work with compatibility and arbitrary
non-matches. The public entry names should reveal whether a request is current
generic work, an explicit compatibility invocation, or not a ZPP workflow at all.

## What Changes

- Add `zpp-generic-workflow` as the complete current playbook for mixed,
  maintenance-oriented, or otherwise unspecialized product workflows.
- Make `zpp-auto` route only workflow-shaped fallback requests to the generic
  playbook and return without a ZPP handoff for genuine non-matches.
- Retain the established direct route for ungoverned artifact-only maintenance.
- Restrict `zpp-legacy-workflow` to explicit invocation and one compatibility
  handoff into `zpp-generic-workflow`, with no lifecycle policy of its own.
- Update the installed workflow inventory and ownership-safe lifecycle projections.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Distinguish the current generic entry, explicit
  legacy compatibility, and non-workflow triage outcomes.

## Impact

Affected areas are packaged workflow skills, automatic routing policy, deterministic
skill inventory and lifecycle projection, focused artifact tests, the consolidated
workflow BDD inventory surface, and its canonical specification. No runtime
dependency, CLI command, trait format, or Bundler state format changes.
