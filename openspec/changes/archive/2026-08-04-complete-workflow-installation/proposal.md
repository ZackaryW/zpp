## Why

Installing ZPP's workflow bundle can currently leave a selected agent unable to run it: native lifecycle hooks remain a separate initialization step, and the OpenSpec operation skills required by every ZPP stage may be absent. A workflow installation must establish its complete executable agent integration instead of producing a partial projection that fails at the first OpenSpec gate.

## What Changes

- Make `workflow install` configure or reconcile the selected agents' native ZPP lifecycle hooks as part of the same complete installation outcome.
- Recognize exact legacy ZPP-generated hook records as owned upgrade inputs and replace them with the current agent-qualified resolution and codespace-guard hooks, while continuing to reject unmanaged or ambiguous conflicts.
- Make global workflow installation bootstrap OpenSpec's core operation skills for every selected agent by generating them in an isolated temporary OpenSpec environment and copying the generated agent-specific skills into that agent's global skill location.
- Let repository-local workflow installation bootstrap repository-local OpenSpec skills only through an explicit opt-in; without that opt-in, its existing ZPP-only local projection behavior remains unchanged.
- Move Pi workflow skills from the shared `.agents/skills` projection to Pi's native `.pi` locations: `.pi/skills` in a repository and `.pi/agent/skills` in the user-global scope. Codex retains `.agents/skills`, and Claude Code retains `.claude/skills`.
- Record the OpenSpec version used for a generated projection, falling back to `null` only when version detection is unavailable. Workflow update regenerates OpenSpec skills only when the detected version differs from the recorded value and otherwise preserves the existing generated projection.
- Leave shared OpenSpec skills installed when the ZPP workflow bundle is removed.
- Preflight the ZPP workflow projection, native hook configuration, and generated OpenSpec skill destinations before committing selected-agent changes, preserving unrelated agent content and rejecting conflicts without partial installation.
- Keep OpenSpec as the generator and source of its own operation-skill content; ZPP does not copy or reimplement those skill bodies in its packaged workflow bundle.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `global-bootstrap-and-agent-setup`: native lifecycle-hook setup becomes part of complete workflow installation as well as explicit initialization, and exact historical ZPP hook records become safely migratable.
- `workflow-skill-distribution`: workflow installation expands from the ZPP bundle alone to the complete selected-agent integration, including native hooks and generated OpenSpec core skills in global scope, and Pi moves to its native `.pi` skill locations.

## Impact

- Affected command paths: `zpp workflow install`, `zpp workflow update`, and the existing agent bootstrap/reconciliation path.
- Affected projections: selected agents' ZPP workflow skill roots, native hook files or extensions, and global OpenSpec skill roots. New Pi projections use `.pi` without disturbing any co-located Codex projection or ambiguously shared historical content.
- External dependency: the installed OpenSpec CLI remains authoritative for generating its version-matched core skills.
- Temporary generation occurs in a platform-neutral project beneath the operating system's temporary directory and is cleaned up after success or failure.
- Tests must cover complete preflight, isolated generation and cleanup, global and opted-in local projection, version-aware updates, exact legacy-hook migration, idempotency, conflict preservation, and selected-agent atomicity.

## Unresolved — Do Not Assume

None. Exact diagnostic phrasing remains an implementation concern rather than product policy; failure atomicity is already part of the capability contract.
