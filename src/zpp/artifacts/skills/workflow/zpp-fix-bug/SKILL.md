---
name: zpp-fix-bug
description: Run the complete ordered ZPP playbook for an externally observable defect correction while preserving the regression and avoiding adjacent redesign.
---

# Correct a public defect

This playbook owns every branch below. Before each governed mutation, use
`zpps-workflow-kernel` to assess the already selected action and obtain the exact
guard. Read-only clarification, exploration, verification, and finalization run
directly; use the kernel afterwards only when their result is consumed as a lifecycle
gate. The kernel never selects the next step.

Owner-authorized end-to-end mode may follow only the declared branches after accepted
results. It never answers an owner decision, supplies missing mutation, archive, or
bypass authority, or skips a component boundary. Explicit end-to-end delegation
carries checkpoint commit authority only for new stage-owned commits produced by this
playbook. ZPP runtime-owned coordination identity is not an owner decision.

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

## 1. Reconcile the failure contract

Custom instruction: preserve the observed failure, affected consumer, expected public
behavior, reproduction conditions, and regression boundary. Do not broaden a defect
into redesign without an explicit owner correction.

Use `zpps-clarify` with exact roots, failure evidence, and owner statements. On
`exploration-required`, use `zpps-explore` for the exact reproduction question and
re-enter. On `planning-operation-required`, retain the exact returned operation and
targets for step 2. On `blocked`, pause. On `completed`, obtain the kernel result
assessment when consuming clarification as a lifecycle gate and continue.

## 2. Reconcile the change plan

Before the first governed mutation, pass the exact resolved repository roots and
change names plus accepted mutation authority to `zpps-workflow-kernel`. Consume the
structured result from ZPP's runtime coordination command. The runtime, not this
playbook, owns registration, store manifests, durable coordination identity,
environment overrides, and Bundler transitions. Never ask the owner for those
internal values; pause only on the concrete runtime conflict or missing product
authority.

Use the exact planning adapter returned by `planning-operation-required`. Without
that signal, use `zpps-update-change` for an existing applicable change. Otherwise use
`zpps-propose-change` to create a complete defect plan; use `zpps-new-change` only
when the owner requested scaffold-and-stop, and `zpps-continue-change` only for one
explicitly selected next artifact. Apply pre/post kernel assessments to each mutation.
Continue only when the plan names the regression and excludes unrelated redesign.

## 3. Shape the regression authority

Use `zpps-shape-bdd` to make the observed failure RED through the real public system,
transfer any executable OpenSpec example to the capability feature root, and retain
only trace authority in OpenSpec. Resolve `kernel-assessment-required` and re-enter;
pause on any other blocker. Continue after the kernel accepts the RED and bindings.

## 4. Plan the smallest correction

Use `zpps-planning-ponytail` only for utility responsibilities implicated by the
failure. Assess either its signature-level plan or its evidence-backed
`skipped: not applicable` result. That outcome completes only `plan-utilities` and
continues to step 5; it never skips maturation or authorizes wiring. A plan
contradiction caused by the accepted contract returns explicitly to
`zpps-clarify`; a contradiction between current repository evidence and an existing
planning artifact returns explicitly to `zpps-update-change`. It never triggers
silent redesign or kernel-selected routing.

## 5. Mature the correction utilities

Use `zpps-mature-utilities` with the exact planning result. For a plan, require the
relevant RED, smallest coherent correction, focused GREEN, and complete utility
surface. For a planning skip, require this stage to independently confirm and return
`skipped: not applicable`. Assess that distinct result before continuing.

## 6. Wire and prove public GREEN

Use `zpps-wire` with the regression scenario, accepted correction, proven utilities,
and real public composition owner. Require scenario-specific GREEN. Pause if the
public owner or accepted boundary is wrong. Continue after kernel result assessment.

## 7. Form and synchronize specifications

Use `zpps-form-specs`. On `sync-required`, explicitly use `zpps-sync-specs` for the
returned deltas and re-enter form-specs for canonical audit. Components never invoke
one another. Continue only after duplicate and orphan authority checks pass.

## 8. Verify repository and change

Use `zpps-verify-repository` for the regression scenario, affected tests, relevant
complete suite, interpreter/lock, lint, format, and clean build. Use
`zpps-verify-change` with that evidence; satisfy `repository-evidence-required` by an
explicit repository-verification use and re-entry.

## 9. Finalize and archive

Use `zpps-finalize` with every accepted stage and verification result.

Follow finalization signals visibly: obtain missing repository or change evidence.
For `archive-required`, require explicit archive authority and use the exact single
or bulk archive adapter, which performs any selected specification sync synchronously
and returns `completed`, `cancelled`, `blocked`, or `failed`; never infer archive
authority. Pause on every non-completed archive result. Submit completed evidence to
the kernel for path, checkpoint, archive, bundle, and lifecycle assessment. Declare
completion only from `lifecycle-complete`.
