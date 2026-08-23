---
name: zpps-workflow-kernel
description: Assess a caller-selected ZPP action, govern its exact Bundler lease and checkpoints, and assess its result without choosing or dispatching workflow steps.
---

# Guard one selected workflow action

Act as a lifecycle guard, never as a workflow or stage dispatcher. Accept either a
pre-action assessment request or a post-action result assessment. The caller, not
this skill, selects the playbook action and component.

## Pre-action assessment

Require the caller to provide the playbook or direct-invocation identity, outcome,
selected action and component, exact repository roots and change names, accepted-input
revision, whether the action mutates governed state, predecessor evidence, and
owner-granted mutation, checkpoint, archive, abandonment, and bypass authority.
Assess only that selected action.

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
not claim an audit or bundle transition occurred. At a material accepted result,
author a checkpoint through `zmem-author-commits` only when the owner supplied
checkpoint authority; otherwise report `accepted` without committing.

Owner-authorized end-to-end execution is interpreted only by the active playbook,
which may follow its own declared branch after this assessment. Never invoke a
`zpps-*` component, implement a phase or OpenSpec operation, infer a stage from
repository state, return a continuation, answer an owner decision, supply missing
mutation/checkpoint/archive authority, skip a component boundary, or declare success
from an unverified component claim.
