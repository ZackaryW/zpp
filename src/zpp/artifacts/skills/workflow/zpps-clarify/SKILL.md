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

Require the selected outcome, exact repository roots, accepted owner statements, the
current contract evidence available to reconcile, and any active playbook-supplied
decision authority. Ask only for a missing value that changes this bounded
clarification result. Do not require a playbook identity or prior kernel delegation;
clarification is read-only.

Inspect current specifications, active change artifacts, repository evidence, and
relevant non-stale memory at the supplied roots. Classify new information as a
confirmation, correction, recommendation, exploration need, or deferral. Preserve
accepted intent until the owner explicitly supersedes it or applicable delegated
decision authority resolves it; recency, existing files, recommendations, and
selected traits are evidence rather than authority.

Expose every outcome-changing unresolved policy, serialization choice, compatibility
boundary, constraint, and acceptance condition. Without applicable delegated
decision authority, ask one to three focused owner questions at a time, identify the
exact missing decision and meaningful consequences, use concrete mutually exclusive
choices when bounded alternatives exist, and otherwise ask one precise open
question. Use the active agent's structured user-question mechanism when available
and ask the same question directly when it is unavailable. Wait for an explicit
answer; an unresolved record, vague request, recommendation, or default never
substitutes for interaction. With applicable best-decision or full-authority
delegation, make the bounded decision visibly with its rationale and reconcile the
whole agreement again. The active playbook, not this component, consumes temporary
authority or retains persistent authority.

Classify repository-context coverage for the accepted change as `not-applicable`,
`covered`, or `trait-authoring-required`. When traits cannot affect the change,
report `not-applicable` without resolving them. Otherwise inspect relevant effective
repository context read-only and report `covered` or the concrete missing guidance.
Never invoke `zpp-author-trait`, edit a trait document, grant workflow authority, or
treat selected trait content as an owner decision; actual authoring remains a
separate explicit operation.

Stop when the agreement is complete or when one unresolved owner decision prevents
a truthful revision. Re-enter this procedure whenever new evidence or a contradiction
supersedes the accepted revision, invalidating every downstream result derived from
that older revision.

Return `completed`, `blocked`, or `exploration-required`, together with the accepted
contract revision, unresolved decisions, roots inspected, evidence, delegated
decisions and rationales, and repository-context classification. For
`exploration-required`, name the exact question and read-only target so the caller
can explicitly invoke `zpps-explore` and then re-enter clarification. For a requested
planning mutation, return `planning-operation-required` with the exact operation and
known targets; the caller selects and invokes the adapter.

This read-only stage never mutates planning or product artifacts or acquires a lease.
