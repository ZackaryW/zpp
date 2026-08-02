## Why

The current default-profile requirement says the profile "activates" its base
traits, which can be misread as automatic participation after `zpp init`.
Runtime behavior already keeps the initialized global layer neutral and requires
an explicit profile selection or global activation, so the contract should state
that boundary without ambiguity.

## What Changes

- Define `default` as a persistent reusable preset that is provisioned but does
  not automatically participate in trait resolution.
- State that its `trait.json` selects the three platform-neutral base traits
  only when the profile explicitly participates.
- Require `zpp global activate default` for persistent activation in the global
  layer; retain `ZPP_PROFILE=default` as an explicit temporary profile overlay.
- Replace ambiguous feature and specification wording without changing runtime
  implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `standard-workflow-traits`: Clarify that the persistent default profile is
  inactive until explicitly selected or copied into global.

## Impact

- Updates the standard-workflow-traits delta, canonical specification, and
  executable feature wording.
- Does not change initialization, resolution, profile, or global-activation code.

## Unresolved — Do Not Assume

None.
