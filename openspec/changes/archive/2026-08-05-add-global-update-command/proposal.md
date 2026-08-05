## Why

After upgrading the ZPP executable, users currently need separate initialization and workflow commands to reconcile global hooks, packaged default-profile entries, workflow bundles, and generated OpenSpec skills. A dedicated `zpp update` command should refresh existing ZPP-owned global state safely while keeping `zpp init` focused on first-time bootstrap.

## What Changes

- Add a top-level, option-free `zpp update` command that requires initialized user state and atomically refreshes existing ZPP-owned global state across Pi, Codex, and Claude Code.
- Additively update the persistent `default` profile with missing packaged trait files and trigger entries while preserving all existing authored values, same-name files, and custom traits.
- Discover every installed managed global ZPP workflow bundle, update it to the current packaged bundle, and maintain its complete integration: current native hooks plus version-aware generated OpenSpec core skills. An absent ZPP workflow bundle remains absent.
- Reconcile a recognizable existing ZPP native hook even when that agent has no managed workflow bundle; leave agents with neither owned surface untouched.
- Preflight the default profile and every discovered owned agent surface before any mutation. Reject malformed, unmanaged, or conflicting state without partial changes or overwrite.
- Keep `zpp update` global-only: do not mutate repository-local skills or `.zpp` layers, create project state, install absent workflows, resolve traits, or upgrade the currently running executable.
- Update Typer help so `zpp init` is described as bootstrap and selected-hook configuration, while `zpp update` is described as maintenance of initialized global ZPP state and installed integrations.
- Replace the documented post-executable-upgrade sequence with `uv tool upgrade zpp` followed by `zpp update`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `global-bootstrap-and-agent-setup`: Add the top-level update surface, preserve bootstrap-only initialization, reconcile recognizable existing hooks, and distinguish both commands in help.
- `standard-workflow-traits`: Allow global update to add missing packaged standard entries to an existing valid persistent `default` profile while preserving authored content.
- `workflow-skill-distribution`: Auto-discover and atomically update every installed managed global workflow integration without installing absent bundles or touching local projections.

## Impact

- Affects the root Typer command hierarchy, initialization helper text, global user-state validation, packaged-default upgrade planning, agent integration inspection, workflow/OpenSpec projection discovery, and atomic filesystem mutation composition.
- Reuses existing ownership manifests, historical-hook recognition, packaged-default merge rules, OpenSpec version detection/generation, and rollback-capable mutation planning; no new dependency or state format is introduced.
- Requires public help, initialized/absent state, additive profile, hook-only, complete workflow, version-aware OpenSpec, conflict atomicity, idempotence, and local-isolation feature coverage.

## Unresolved — Do Not Assume

None. The owner confirmed the dedicated global update boundary and automatic discovery of all existing ZPP-owned global surfaces.
