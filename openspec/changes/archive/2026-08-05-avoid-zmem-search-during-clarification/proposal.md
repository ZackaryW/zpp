## Why

Clarification currently requires temporal-history investigation without bounding how records are discovered, which can lead an agent to invoke a broad `zmem search` that stalls an otherwise focused product investigation. Clarification should retain its authority check while using bounded history access that cannot become an open-ended search gate.

## What Changes

- Require `zpp-clarify-change` to discover relevant temporal history only through bounded `zmem recall` filters.
- Prohibit `zmem search` during clarification, while allowing `zmem show` for an already identified relevant record.
- Continue from canonical OpenSpec and current repository evidence when bounded recall yields no relevant history.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Narrow the clarification workflow's temporal-history lookup contract without weakening its comparison against current authority.

## Impact

- Updates the packaged `zpp-clarify-change` skill and its workflow-contract verification.
- Does not change the `zpp-use-zmem` teaching surface, the zmem CLI, application APIs, dependencies, or persisted state.

## Unresolved — Do Not Assume

None. The owner explicitly prohibited `zmem search` during clarification and asked that the workflow skill retain that restriction.
