## Why

ZPP currently installs Codex's user-global workflow bundle into `~/.agents/skills`, but the owner's Codex installation on macOS failed to consume that global projection and was verified to load the bundle from `~/.codex/skills`. The owner's Windows environment also consumes generated skills from `.codex/skills`. Global workflow installation must therefore target the cross-platform working Codex user directory while preserving the existing repository-local convention.

## What Changes

- Change only Codex's user-global ZPP workflow projection from `~/.agents/skills` to `~/.codex/skills` on every supported platform, resolving `~` from the active user home.
- Keep repository-local Codex workflow skills at `.agents/skills`.
- Allow the ZPP workflow ownership manifest and generated OpenSpec ownership manifest to coexist in `~/.codex/skills` with disjoint owned paths.
- Update global install, update, remove, and top-level update discovery to use the corrected user-global root.
- Leave any historical `~/.agents/skills` projection untouched; this change does not infer authority to delete or migrate existing user files.
- Correct README, canonical specifications, BDD fixtures, and focused projection tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Correct the Codex user-global workflow destination while retaining the repository-local destination and ownership isolation.

## Impact

- Affects platform-neutral Codex global skill projection resolution, workflow lifecycle orchestration, top-level installed-workflow discovery, documentation, BDD fixtures, and projection tests.
- Introduces no new dependency or state format. Existing workflow and OpenSpec manifests already support independent ownership in a shared root.
- Users with a historical global projection under `~/.agents/skills` must run global workflow install again to create the corrected projection; the old projection is not deleted automatically.

## Unresolved — Do Not Assume

None. The owner explicitly selected `~/.codex/skills` for Codex user-global installation, and automatic deletion or relocation of the historical root is outside this correction.
