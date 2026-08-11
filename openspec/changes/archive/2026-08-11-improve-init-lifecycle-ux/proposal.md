## Why

Root initialization and reset currently dump complete Agent Router lifecycle JSON into ordinary terminal use, obscuring whether the operation succeeded. Initialization also lacks an explicit way to reproject already-current owned integrations.

## What Changes

- Render one concise human summary line by default for `zpp init` and confirmed `zpp reset`.
- Add explicit `--json` output to both commands for the complete deterministic lifecycle report.
- Add `zpp init --force` to reproject every selected agent's workflow skill, hook, packaged authoring skills, and generated OpenSpec skills instead of accepting current projections as no-ops.
- Preserve Agent Router ownership and conflict authority during forced reprojection.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-skill-provisioning`: Adds forced complete initialization and concise/default versus explicit/JSON reporting.
- `product-home-lifecycle`: Replaces confirmed reset's default JSON dump with a concise summary while retaining explicit structured output.

## Impact

- Root initialization and reset CLI options and rendering.
- Agent Router lifecycle orchestration for selected user integrations.
- Capability-owned CLI behavior features and unit coverage for summary aggregation and force routing.

## Unresolved — Do Not Assume

None.
