---
name: zpp-new-feature
description: Run the complete ordered ZPP playbook for a new externally observable capability, using explicit bounded components and visible branches.
---

# Deliver a new public capability

This playbook owns the sequence below. Before a governed mutation, use
`zpps-workflow-kernel` for a pre-action assessment of the action already selected
here and pass its exact guard to the component. Read-only clarification, exploration,
repository verification, semantic verification, and finalization run directly.
Use the kernel afterwards only when a component result is consumed as a lifecycle
gate. Kernel results contain no next step; follow only the branches written below.

Owner-authorized end-to-end mode may follow these declared branches automatically
after accepted results, including continuing after a completed proposal. It never
answers an owner decision, supplies missing mutation/archive/bypass authority, or
skips a component boundary. Explicit end-to-end delegation carries checkpoint commit
authority only for new stage-owned commits produced by this playbook. Internal
coordination identity is resolved by the ZPP runtime and is not an owner decision.

## Component admission invariant

Before invoking a declared `zpps-*` component, choose its exact configuration from
the immediate necessary operation and its evidence readiness, not the eventual
product outcome, current change or task status, or imperative wording. Unresolved
evidence admits `zpps-explore`; unresolved outcome-changing owner policy admits
`zpps-clarify`. Every configured component remains subject to its own readiness and
authority contract. Consume `component-mismatch` as failed admission, report it
immediately, and select no continuation from inside the rejected component.

## Visible stage progression invariant

Execute every primary stage below as a distinct visible `zpps-*` action. Before each
one, ask `zpps-workflow-kernel` to assess that already selected stage using the current
contract revision, complete ordered predecessor outcomes, invalid or stale evidence,
accepted effects, stage-owned output, and authority. After it runs, submit its actual
status, verification, and changed paths for result assessment. A result from one stage
never supplies, skips, or completes another stage. Only this playbook selects the next
declared action after the current result is accepted.

## Incremental checkpoint rule

Before advancing past any stage or operation result that owns a non-empty coherent
diff, submit its accepted contract revision, exact paths or hunks, and passing
stage-appropriate verification to `zpps-workflow-kernel`. Do not defer stage-owned
work into one final commit. With checkpoint authority, require `checkpointed` after
the kernel follows `zmem-author-commits`, validates every message, creates only
dependency-ordered coherent commits, and inspects every resulting SHA through
`zmem show`. Preserve unrelated working-tree changes.

Let `zmem-author-commits` decide whether durable memory is warranted. Retain an
accepted architecture, policy, constraint, or tradeoff and its reason as a selective
`DECISION`; retain a verified reusable lesson as `LESSON_LEARNT`; leave routine
implementation and archival checkpoints unannotated. Do not duplicate an earlier
memory merely because a later checkpoint implements or synchronizes it. Without
checkpoint authority, return `checkpoint-authority-required` and leave the material
gate incomplete. A skipped or empty stage records evidence without an empty commit.

## 1. Establish the capability agreement

Custom instruction: frame one public capability, its consumers, observable behavior,
compatibility boundary, and acceptance conditions without choosing an implementation.

Use `zpps-clarify` with the request, exact roots, owner statements, and current
contract evidence. On `exploration-required`, use `zpps-explore` with the returned
question and re-enter clarification. On `planning-operation-required`, retain the
signal until step 2. On `blocked`, pause. On `completed`, assess the result through
the kernel and continue to step 2.

## 2. Establish or reconcile the OpenSpec change

Custom instruction: preserve an explicitly selected change; otherwise create one
whose name and scope reflect the accepted capability.

Before the first governed mutation, pass the exact resolved repository roots and
change names plus accepted mutation authority to `zpps-workflow-kernel`. The kernel
invokes ZPP's runtime coordination command, which owns registration, manifest and
owner identity, environment overrides, and exact bundle acquisition. Consume its
structured coordinated, bypassed, or blocked result; never ask the owner for an
internal store, UUID, owner string, environment value, bundle, or lease command.

- Existing change with planning artifacts -> use `zpps-update-change` for the exact
  accepted revision. If it reports missing artifacts deferred to continuation, use
  guarded `zpps-continue-change` for exactly one ready artifact, assess the result,
  and repeat that explicit one-artifact branch until the required set is complete or
  blocked.
- Existing scaffold without the next artifact -> use `zpps-continue-change` once and
  repeat this branch as explicitly required.
- No change and intent is fully understood -> use `zpps-propose-change` to create the
  complete planning set. In owner-authorized end-to-end mode, continue to step 3
  after its accepted result without requesting fresh permission.
- Owner requested scaffold-only planning -> use `zpps-new-change` and stop after its
  published boundary unless the owner separately authorizes continuation.

Apply pre/post kernel assessments to every mutating use. Pause on adapter blockers.
When the planning set represents the accepted capability, continue to step 3.

## 3. Shape executable behavior

Use `zpps-shape-bdd` with the accepted agreement, exact OpenSpec root, capability
owner, provisional examples, and binding inventory. Require transfer of every
testable example to capability BDD and trace-only OpenSpec anchors. On
`kernel-assessment-required`, obtain the named guard and re-enter. On `blocked`,
pause. Assess `completed` through the kernel, then continue to step 4.

## 4. Plan utilities

Use `zpps-planning-ponytail` with shaped behavior and dependency evidence. If it
returns `skipped: not applicable`, assess that planning result without treating it as
a maturation result. If it returns a plan, assess its exact revision. Pause on any
contradiction, and continue to step 5 only after this distinct stage is accepted.

## 5. Mature utilities

Use `zpps-mature-utilities` with the exact planning result and relevant RED targets.
For a planning skip, require this stage to independently confirm and return
`skipped: not applicable`. Otherwise require verified utility GREEN. Assess the
distinct maturation result before continuing.

## 6. Wire the public capability

Use `zpps-wire` with approved scenarios, bindings, proven utilities, and the actual
public composition owner. Pause if wiring requires a new owner decision or revised
plan. After focused public evidence is accepted, continue to step 7.

## 7. Form and synchronize specifications

Use `zpps-form-specs` with delta/canonical paths reported by OpenSpec, bindings, and
mature evidence. On `sync-required`, explicitly use `zpps-sync-specs` with exactly
the returned delta set, then re-enter `zpps-form-specs` with its result. Never let
either component invoke the other. Continue only after the canonical authority audit
returns `completed` and the kernel accepts it.

## 8. Verify repository and change

Use `zpps-verify-repository` with scenario-selected BDD, focused and complete tests,
interpreter/lock, lint, format, and clean-build targets. Resolve
`owner-choice-required` before proceeding. Then use `zpps-verify-change` with the
planning artifacts, implementation, bindings, and supplied repository evidence. On
`repository-evidence-required`, run only the newly requested evidence through
`zpps-verify-repository` and re-enter verification. Pause on any failure.

## 9. Finalize and archive

Use `zpps-finalize` with all accepted evidence. Follow its visible result:

- `repository-evidence-required` -> use `zpps-verify-repository`, then re-enter;
- `change-verification-required` -> use `zpps-verify-change`, then re-enter;
- `archive-required` -> use the exact `zpps-archive-change` or
  `zpps-bulk-archive-change`, which performs any selected specification sync
  synchronously and returns `completed`, `cancelled`, `blocked`, or `failed`; require
  explicit archive authority before this use and never infer it, then re-enter
  finalization only after `completed`;
- `blocked` -> pause;
- `completed` -> ask the kernel to assess final evidence, path audit, archive records,
  checkpoints, and bundle completion.

Report lifecycle completion only when the final kernel assessment says
`lifecycle-complete`. End-to-end continuation is limited to this playbook's declared
branches; no hidden sequence, owner-decision answer, inferred authority,
compatibility alias, or component-selected next action is permitted.
