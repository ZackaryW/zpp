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
selected action and component, exact repository roots, resolved store/change targets
when known, accepted-input revision, whether the action mutates governed state,
predecessor evidence, and owner-granted checkpoint authority. Assess only that
selected action.

Return one of `eligible`, `blocked`, `completed`, or `accepted-not-applicable`, plus
the assessed action identity, reasons, required evidence, authority facts, and any
`durable-owner-required` or `store-registration-required` blocking signal. The result
has no next-step, next-stage, or component-selection field.

For a governed mutation, require a durable owner plus an exact registered store UUID
and exact change member before the first write. The current Bundler CLI cannot lease
a repo-local-only OpenSpec root. Such a root may be inspected and may remain the
`repo:<path>` trace locator, but return `store-registration-required` and `blocked`
until the caller resolves an exact UUID from the public registered-store list. Never
invent or derive a UUID from a name or path.

Once those inputs exist, acquire or confirm one Bundler bundle for the durable owner
and return the exact bundle identity and membership as the mutation guard. Return
`durable-owner-required` when that owner is missing. Never add a member, replace a
bundle, or treat traits, artifacts, skill identity, component output, or end-to-end
mode as mutation authority. A direct component caller may request this assessment;
prior playbook delegation is not required.

## Result assessment

Require the original assessed action, its guard when mutation occurred, the component
status, changed paths, unresolved questions, and verification evidence. Return
`accepted`, `blocked`, `checkpointed`, or `lifecycle-complete`, with reasons and
observed authority facts. Again return no next-step field.

Audit changed paths against the bundle. Record member archives only from observed
archive results and complete the bundle only after every declared member is archived
and every required gate and path audit succeeds. At a material accepted result,
author a checkpoint through `zmem-author-commits` only when the owner supplied
checkpoint authority; otherwise report `accepted` without committing.

Owner-authorized end-to-end execution is interpreted only by the active playbook,
which may follow its own declared branch after this assessment. Never invoke a
`zpps-*` component, implement a phase or OpenSpec operation, infer a stage from
repository state, return a continuation, answer an owner decision, supply missing
mutation/checkpoint/archive authority, skip a component boundary, or declare success
from an unverified component claim.
