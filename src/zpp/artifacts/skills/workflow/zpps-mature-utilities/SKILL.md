---
name: zpps-mature-utilities
description: Implement already planned utility seams from relevant RED to GREEN only when that exact code mutation is explicitly requested; exclude utility discovery and wiring.
---

# Mature planned utilities

## Admit utility implementation

Admit this component only when an active playbook configures this exact maturation or
the caller explicitly requests the immediate mutation of implementing already
planned utility seams. Required readiness includes an accepted utility plan or an
evidence-backed same-revision planning skip. A plan additionally requires relevant
RED evidence, resolved dependencies, and explicit utility implementation intent.
Unknown package, API, repository, or integration evidence belongs to exploration;
missing utility boundaries belong to planning; public composition belongs to wiring.

Require the accepted contract revision, exact repository roots, current planning result, and
repository test context. For a plan, also require selected RED observations and the
kernel's matching pre-action assessment for every exact root and change target.
Return `kernel-assessment-required` or `coordination-conflict` before editing when it
is absent, stale, or blocked.

When the planning result is `skipped: not applicable`, independently verify that the
accepted responsibilities require no utility implementation and return this stage's
own `skipped: not applicable` result. Do not infer the result merely from the planning
label, and do not require a mutation guard for a verified no-op.

Reconcile a plan with current repository evidence. Establish a relevant failing
observation before implementation. If it does not fail for the expected reason, stop
with `blocked` and report the contradiction rather than changing production code.

Implement the smallest coherent slice that satisfies the planned boundary. Keep the
public contract and failure behavior explicit, reuse accepted dependencies, and avoid
unplanned adjacent redesign. Run the focused verification to GREEN, then the relevant
complete utility test surface. After all required implementation and evidence
succeed, update only supplied OpenSpec tasks whose text and scope are each fully
satisfied by this utility result. Never mark a partial, adjacent, inferred, or
unrelated task.
Apply injected `tdd` content only as language and framework advice; it cannot waive
RED or GREEN.

Return `completed`, `skipped: not applicable`, or `blocked`, with
`kernel-assessment-required` or `coordination-conflict` when applicable, plus exact
RED and GREEN commands and observations, changed paths, and any plan contradiction.
Never create wording tests, wire the public product, or revise specifications.
