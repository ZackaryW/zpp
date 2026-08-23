## Why

One generic workflow entry makes agents reconcile product intent, stage routing, and OpenSpec operation rules at the same time, while generated OpenSpec skills can introduce a second set of lifecycle instructions. ZPP needs discoverable outcome workflows and bounded phase skills without duplicating the authority that keeps clarification, leases, verification, checkpoints, and finalization coherent.

## What Changes

- Define `zpp-*` as complete user-facing workflow skills and `zpps-*` as bounded subordinate skills that cannot select or advance a workflow by themselves.
- Add thin `zpp-new-feature`, `zpp-fix-bug`, and `zpp-scaffold` entries, while retaining `zpp-workflow` as the explicit generic entry.
- Add `zpp-auto` as a non-mutating triage entry that routes an unambiguous request and falls back to `zpp-workflow` at `clarify` when the outcome is mixed or unresolved.
- Move shared stage orchestration and all lifecycle authority into the delegated `zpps-workflow-kernel` skill.
- Add initial `zpps-plan` and `zpps-archive` component skills as ZPP-owned boundaries around public OpenSpec planning and archive operations.
- Add `zpp-legacy-workflow` as a narrow translator for the previous consolidated `zpp-workflow` invocation contract, with no ZPP 1.x `zpp-flow-*` compatibility or independent policy.
- Keep traits advisory; neither traits nor subordinate skills may select a workflow kind, grant mutation, establish verification, or declare completion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Replace the single distributed entry-skill contract with a role-separated skill family governed by one delegated workflow authority.

## Impact

- Packaged ZPP skill inventory, skill descriptions, references, and Agent Router projection expectations.
- Canonical consolidated-workflow requirements and its capability-owned Behave surface.
- OpenSpec operation integration changes from generated operation skills as workflow owners to ZPP-owned bounded component skills using public OpenSpec interfaces.
- No trait format, Bundler lease format, Python public API, or third-party runtime dependency change.
