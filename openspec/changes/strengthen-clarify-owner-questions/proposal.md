## Why

The clarification contract can identify and retain an unresolved owner decision without requiring the agent to ask a concrete question that can resolve it. This permits weak, open-ended clarification responses and leaves convergence dependent on the owner guessing what information is missing.

## What Changes

- Require `clarify` to identify every outcome-changing decision that repository evidence and accepted input do not settle.
- Require the workflow to ask one to three focused owner questions at a time, with the decision and meaningful consequences made concrete.
- Prefer the active agent's structured user-question mechanism when available and require a direct focused question when it is unavailable.
- Reject vague clarification requests and treat `Unresolved — Do Not Assume` as a blocking record rather than a substitute for asking.
- Reconcile each explicit owner answer across the complete change contract and repeat the question loop until no owner decision remains.
- Preserve automatic progression when repository evidence already settles the issue or clarification has converged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Strengthen complete agreement reconciliation with an explicit, bounded owner-question loop and convergence gate.

## Impact

The change affects the packaged `zpp-workflow` instructions and the canonical consolidated-workflow capability. It changes no CLI, runtime implementation, dependency, BDD feature, or testable utility behavior.
