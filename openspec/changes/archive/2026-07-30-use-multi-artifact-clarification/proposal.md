## Why

ZPP clarification currently forces accepted behavior into one temporary
`proposal.md` and forbids OpenSpec delta specs until after implementation. This
collapses overview and capability contracts into one file and prevents a change
from using OpenSpec's normal multi-artifact proposal structure.

## What Changes

- Make `proposal.md` own motivation, scope, capability inventory, impact, and
  unresolved owner decisions rather than the complete behavioral contract.
- Require one OpenSpec delta spec at `specs/<capability>/spec.md` for every new
  or modified capability declared by the proposal.
- Persist settled behavior into its owning capability delta during
  clarification while keeping unresolved decisions in the proposal.
- Make feature shaping consume both the proposal and all declared delta specs,
  then remove only duplicated executable examples after Gherkin owns them.
- Make post-green specification formation reconcile and mature the existing
  delta specs instead of creating specifications for the first time.
- Keep design and task artifacts governed by the selected OpenSpec schema and
  its artifact instructions rather than a universal ZPP one-file prohibition.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Clarification and downstream workflow skills
  SHALL preserve OpenSpec's proposal-plus-capability-deltas artifact model.

## Impact

- Updates the permanent `zpp-clarify-change`, `zpp-shape-feature`, and
  `zpp-form-specs` skill contracts and their installed development projections.
- Updates workflow feature coverage and canonical workflow authority.
- Does not change runtime CLI behavior or introduce platform-specific policy.

## Unresolved — Do Not Assume

None.
