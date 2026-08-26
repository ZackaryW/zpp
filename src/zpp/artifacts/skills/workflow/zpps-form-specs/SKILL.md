---
name: zpps-form-specs
description: Audit resolved OpenSpec-to-BDD authority and optionally remove BDD-owned OpenSpec scenarios; do not discover missing behavior evidence or synchronize canonical specs.
---

# Form specifications without duplicate acceptance authority

## Admit specification formation

Admit this component only when an active playbook configures this exact formation or
the caller's immediate operation is to audit resolved OpenSpec/BDD authority and
prepare its single-authority specification form. Required readiness includes an accepted
contract, identified change, binding inventory, and mature evidence. A read-only
authority audit needs no mutation intent; any scenario-removal edit additionally requires
explicit intent for that exact write or exact playbook configuration. Unresolved
behavior or integration evidence belongs to exploration, and canonical merging is a
separate synchronization operation.

Require the accepted contract revision, exact repository and OpenSpec roots, resolved store and
change identities, current binding inventory, mature GREEN evidence, and canonical
and delta paths reported by OpenSpec. For edits, obtain the kernel's matching
pre-action assessment for the exact roots and change names; otherwise return
`kernel-assessment-required` or `coordination-conflict` with the unresolved inputs.

When the accepted contract has no mature behavior and no accepted delta requiring
canonical specification reconciliation, return `skipped: not applicable` with that
evidence. A governed prose or declarative delta is applicable even without BDD and
therefore cannot use this skip.

Resolve every feature-side binding to its exact OpenSpec requirement. Each executable
obligation must have one or more scenario-selected public-system feature authorities
and no corresponding OpenSpec scenario of any form. A specification-only
obligation must have no feature claiming executable authority. Reject stale,
cross-capability, unverified, self-recording, execution-only, literal-text-only,
pure-counting, capability-wide, or orphaned bindings. Counts are acceptable only as
supplemental constraints on an independently observed behavior.

Require the feature-side `# zpp-spec:` declaration to contain compact JSON with
ordered `root`, `capability`, `requirement`, `feature`, and `scenario` keys. Use `store:<uuid>` only
for an exact discovered registered-store UUID; otherwise use a normalized
`repo:<git-root-relative-path-to-openspec-root>`. Require the feature path and
scenario title to resolve uniquely to the named requirement. Require the corresponding
OpenSpec scenario to be absent; the feature-side declaration is the complete trace.

On the first pass, make only the allowed delta-spec authority corrections and perform
the semantic duplicate/orphan audit. If canonical deltas remain, return
`sync-required` with the exact selected delta paths, rules/input snapshot needs, and
pre-sync audit evidence. The caller must explicitly invoke `zpps-sync-specs` and then
re-enter this skill with the sync result. On re-entry, audit the resulting canonical
specifications and return `completed` only when every binding and authority resolves.
After all exact specification edits and the final audit succeed, update only supplied
OpenSpec tasks whose text and scope are each fully satisfied by this formation result.
Never mark a partial, adjacent, inferred, or unrelated task complete.

Return `completed`, `skipped: not applicable`, `blocked`, or `sync-required`, with
`kernel-assessment-required` or `coordination-conflict` when applicable, plus changed
paths and the complete audit. This stage never performs canonical synchronization or
archival.
