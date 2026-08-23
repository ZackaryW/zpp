---
name: zpps-workflow-kernel
description: Guard an exact caller-selected ZPP action and its result; never choose a component, resolve an ambiguous operation, or dispatch workflow work.
---

# Guard one selected workflow action

## Admit one selected guard assessment

Admit this component only when an active playbook configures a guard for an exact
action or the caller's immediate operation is pre-action or post-result assessment
of an already selected component. Required readiness includes the selected action,
component, targets, effect class, predecessor evidence, and relevant authority facts.
Requests to choose a component, discover missing facts, perform the selected action,
or continue a workflow do not admit the kernel.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-workflow-kernel`, the
`observed_immediate_operation`, `missing_readiness`, and the
`separately_eligible_operation`. Stop before the normal guard procedure and never
invoke the separately eligible component.

Act as a lifecycle guard, never as a workflow or stage dispatcher. Accept either a
pre-action assessment request or a post-action result assessment. The caller, not
this skill, selects the playbook action and component.

## Pre-action assessment

Require the caller to provide the playbook or direct-invocation identity, outcome,
selected action and component, exact repository roots and change names, accepted-input
revision, whether the action mutates governed state, predecessor evidence, and
owner-granted mutation, checkpoint, archive, abandonment, and bypass authority.
Assess only that selected action.

Treat explicit owner-authorized end-to-end playbook delegation as checkpoint commit
authority only for new stage-owned commits produced by that playbook. A standalone
component or stage requires separately granted checkpoint authority. Neither form
authorizes amend, merge, rebase, push, conflict resolution, or unrelated paths.

Return one of `eligible`, `blocked`, `completed`, or `accepted-not-applicable`, plus
the assessed action identity, reasons, required evidence, authority facts, and any
runtime coordination conflict. The result has no next-step, next-stage, or
component-selection field.

For a governed mutation with accepted mutation authority, invoke `zpp lease acquire`
with one matching `--root` and `--change` pair per exact target. ZPP's Python runtime
owns OpenSpec registration, Bundler manifest preparation, product-home owner
identity, `ZPP_WORKFLOW_COORDINATION` parsing, topology resolution, and atomic bundle
acquisition. Do not duplicate those algorithms, inspect the environment variable, or
ask the owner for any internal coordination value.

Accept `coordination: leased` only when the structured result contains the exact
targets, resolved store UUID members, and bundle identity. Accept
`coordination: bypassed` only when the assessment input carries explicit owner bypass
authority for this action; bypass grants no other authority. Return `blocked` with
the runtime diagnostic on invalid override, registration, manifest, topology,
ownership, or lease conflict. Never add a target, replace a bundle, fall back to
unleased mutation, or treat traits, artifacts, skill identity, component output, or
end-to-end mode as mutation authority. A direct component caller may request this
assessment; prior playbook delegation is not required.

## Result assessment

Require the original assessed action, its guard when mutation occurred, the component
status, changed paths, unresolved questions, and verification evidence. Return
`accepted`, `blocked`, `checkpointed`, or `lifecycle-complete`, with reasons and
observed authority facts. Again return no next-step field.

For leased execution, submit changed paths to ZPP's runtime audit operation, record
member archives only from observed archive results, and complete the bundle only
after every declared member is archived and every required gate and path audit
succeeds. For explicitly bypassed execution, retain structured bypass evidence and do
not claim an audit or bundle transition occurred.

At every material accepted result with a non-empty coherent stage-owned diff, require
checkpoint authority and invoke the exact installed `zmem-author-commits` skill before
returning stage completion. Supply the accepted contract revision, exact paths or
hunks, passing stage verification, and authority. Require dependency-ordered commits,
zmem validation of each complete message, preservation of unrelated work, and
`zmem show` inspection of every resulting SHA. Return `checkpointed` only after all
required checkpoint evidence succeeds. Without authority, return `blocked` with
`checkpoint-authority-required`; do not call the gate accepted or defer its diff to
finalization. A skipped action or empty diff returns `accepted` without an empty
commit.

Delegate annotation choice to `zmem-author-commits`. A durable accepted architecture,
policy, constraint, or tradeoff and its rationale merits a selective `DECISION`; a
verified reusable lesson merits `LESSON_LEARNT`. Routine implementation, sync, and
archive narration needs no annotation, and later checkpoints must not duplicate
memory already retained by an earlier commit.

Owner-authorized end-to-end execution is interpreted only by the active playbook,
which may follow its own declared branch after this assessment. Never invoke a
`zpps-*` component, implement a phase or OpenSpec operation, infer a stage from
repository state, return a continuation, answer an owner decision, supply missing
mutation/checkpoint/archive authority, skip a component boundary, or declare success
from an unverified component claim.
