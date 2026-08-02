## Why

Adding a permanent workflow skill changed the current manifest validator so an older, legitimately ZPP-managed seven-skill projection is now classified as an unmanaged conflict. This prevents the `workflow update` command from performing the safe migration it exists to provide.

## What Changes

- Accept structurally valid historical workflow manifests as ownership evidence even when their owned skill set differs from the current bundle.
- Classify a historical managed projection as outdated so `workflow update` can atomically replace only its manifest-owned paths with the current bundle.
- Continue rejecting malformed manifests, content that differs from its manifest, unmanaged collisions, and unsafe paths without mutation.
- Distinguish a missing selected projection from unmanaged or conflicting state in lifecycle diagnostics.
- Preserve explicit scope: repository-local remains the default and `--global` selects the user-global projection.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Permit safe updates from historical managed bundle manifests while retaining exact ownership validation and explicit scope selection.

## Impact

- Affects workflow manifest decoding, projection inspection, update planning diagnostics, utility tests, and workflow lifecycle behavior examples.
- Enables the existing global seven-skill Codex/Pi projection to migrate to the current eight-skill version without manual manifest edits or deletion.
- Does not broaden `--force`, overwrite unmanaged skills, infer scope, or alter authored profiles and traits.

## Unresolved — Do Not Assume

None.
