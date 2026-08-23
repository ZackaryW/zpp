---
name: zpps-clarify
description: Reconcile accepted owner statements into one read-only product agreement; use exploration first for unresolved factual evidence and never edit artifacts here.
---

# Clarify the product agreement

## Admit agreement clarification

Admit this component only when an active playbook configures this exact clarification
or the caller's immediate operation is to reconcile explicit owner statements and
available evidence into an accepted product agreement. Required readiness is a
bounded agreement question with the relevant owner inputs identified. Unresolved
package, version, API, remote, repository, or integration facts belong to
`zpps-explore`; planning or product edits require a separately admitted mutation.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-clarify`, the `observed_immediate_operation`,
`missing_readiness`, and the `separately_eligible_operation`. Stop before the normal
procedure and never invoke the separately eligible component.

Accept either playbook configuration or a direct partial invocation. Require the
selected outcome, exact repository roots, accepted owner statements, and the current
contract evidence available to reconcile. Ask only for a missing value that changes
this bounded clarification result. Do not require a playbook identity or prior kernel
delegation; clarification is read-only.

Inspect current specifications, active change artifacts, repository evidence, and
relevant non-stale memory at the supplied roots. Classify new information as a
confirmation, correction, recommendation, exploration need, or deferral. Preserve
accepted intent until the owner explicitly supersedes it; recency, existing files,
and recommendations are evidence rather than authority.

Expose every outcome-changing unresolved policy, serialization choice, compatibility
boundary, constraint, and acceptance condition as a focused owner question. Stop
when the agreement is complete or when one unresolved owner decision prevents a
truthful revision.

Return `completed`, `blocked`, or `exploration-required`, together with the accepted
contract revision, unresolved decisions, roots inspected, and evidence. For
`exploration-required`, name the exact question and read-only target so the caller
can explicitly invoke `zpps-explore` and then re-enter clarification. For a requested
planning mutation, return `planning-operation-required` with the exact operation and
known targets; the caller selects and invokes the adapter.

Never invoke another `zpps-*` skill, mutate planning or product artifacts, acquire a
lease, select workflow continuation, authorize a checkpoint, or claim lifecycle
completion.
