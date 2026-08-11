## Why

Feature and utility shaping currently imply derivation from the accepted change but do not explicitly prevent documentation, artifact, configuration, or implementation work from leaking into behavior tests.

## What Changes

- Allow Gherkin only for accepted externally observable behavior in active capability delta specs.
- Exclude proposals, designs, tasks, docs, artifacts, configuration-only work, and implementation details as scenario sources.
- Require artifact-only changes to treat `shape` as not applicable; for behavioral deltas, require complete traceable coverage or a concrete non-BDD classification.
- Restrict TDD to executable behavior, explicitly including artifact processing while excluding tests that merely pin artifact prose or wording.
- Keep the packaged workflow wording concise and add no runtime, CLI, trait, or hook behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Restricts Gherkin shaping to behavior delta specs, restricts TDD to executable behavior rather than artifact wording, and makes their applicability explicit.

## Impact

- Packaged `zpp-workflow` instructions and their canonical specification. No Gherkin feature, binding, or unit-test changes.

## Unresolved — Do Not Assume

None.
