## Why

The clarification contract can identify and retain an unresolved owner decision without reliably requiring a concrete owner question, and it does not distinguish automatic progression from temporary or persistent decision authority. This permits both silent agent assumptions and unnecessary approval pauses, while repository-context gaps can pass through clarification without an explicit trait-impact assessment.

## What Changes

- Require `clarify` to identify every outcome-changing decision that repository evidence and accepted input do not settle.
- Require one to three focused owner questions at a time, with the decision and meaningful consequences made concrete.
- Distinguish automatic end-to-end progression, one-Clarify-gate best-decision authority, and persistent full authority until revocation.
- Treat ordinary in-scope component confirmations as covered by automatic progression after the exact proposed effects are shown.
- Preserve manual gates for unresolved Clarify decisions unless the corresponding decision authority is active.
- Always require step-by-step owner authorization for Git pushes, GitHub merge actions, and cloud-environment access or mutation.
- Require Clarify to classify repository-context coverage as `not-applicable`, `covered`, or `trait-authoring-required`; keep actual trait authoring a separate explicit operation.
- Preserve automatic progression when evidence settles the issue or clarification has converged.
- Restore repository verification by aligning the exported package version with project metadata and repairing one stale vendored-skill assertion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Strengthen clarification convergence, define bounded automatic decision authority, preserve protected-operation gates, and add repository-context gap assessment.

## Impact

The change affects packaged workflow, clarification, kernel, and routing instructions plus the canonical consolidated-workflow capability. It also aligns the existing public version constant with `pyproject.toml` and updates one stale test assertion after a vendored skill sync. It adds no CLI or runtime autonomy state, dependency, BDD feature, utility, or new behavioral test. Persisted command controls for enabling, inspecting, or revoking automatic mode remain a deferred follow-up rather than part of this change.
