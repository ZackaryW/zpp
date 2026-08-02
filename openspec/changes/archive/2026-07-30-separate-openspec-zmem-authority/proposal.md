## Why

The workflow currently blurs current product authority, temporary change planning, and durable history: the live proposal is described as a state of record, while ordinary commits are forced to carry zmem annotations even when no long-lived decision changed. ZPP needs one explicit authority model so current truth and decision evolution remain useful without duplicating each other.

## What Changes

- Make canonical OpenSpec specifications the long-standing authority for current accepted product behavior.
- Treat an active OpenSpec proposal as mutable working state for the change being clarified and implemented, not as long-standing authority.
- Make zmem the temporal record of meaningful decision changes, reversals, fallbacks, surprises, and lessons, including the prior direction, the replacement direction, and why it changed when applicable.
- Require clarification to inspect relevant zmem history and compare later temporal decisions with canonical OpenSpec before recording the current working proposal.
- Prevent stage checkpoints from repeating an unchanged decision merely to mark progression; create a zmem checkpoint only when material tracked work and a durable temporal highlight coexist.
- Allow the bundled commit-message validators to validate ordinary conventional commits without a zmem annotation, while providing an explicit memory-bearing mode that requires at least one canonical zmem annotation for `zpp-commit-zmem`.
- Form canonical OpenSpec specifications from final mature green behavior only; keep abandoned or superseded chronology in zmem rather than copying it into the canonical specification.
- Keep temporal recall as an entry responsibility of `zpp-clarify-change`; do not add a separate recall skill or require graph/dependency semantics.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `standard-workflow-traits`: Define the non-overlapping current-authority, working-state, and temporal-history boundaries used across the workflow.
- `workflow-skill-distribution`: Require permanent workflow skills and the zmem validator to apply the corrected authority and checkpoint semantics.

## Impact

- Packaged and development projections of `zpp-clarify-change`, `zpp-commit-zmem`, and `zpp-form-specs`.
- Other packaged and development workflow skills wherever checkpoint wording currently implies mandatory stage-marker commits.
- The default automatic-workflow trait if a concise shared authority statement prevents repetition across skills.
- PowerShell and POSIX zmem commit-message validators and focused utility tests.
- Public workflow Gherkin scenarios, step bindings, and the two affected canonical OpenSpec specifications after mature green verification.

## Unresolved — Do Not Assume

None. The owner has confirmed the authority split and clarified that zmem's “decision tree” means the temporal lineage of changed decisions and important highlights, not a dependency graph.
