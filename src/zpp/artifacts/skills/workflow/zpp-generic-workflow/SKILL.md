---
name: zpp-generic-workflow
description: Run the complete current ZPP playbook for mixed, maintenance-oriented, or otherwise unspecialized product outcomes.
---

# Run the generic current workflow

This playbook owns its complete conditional sequence. Before a governed mutation,
use `zpps-workflow-kernel` for its exact guard. Read-only clarification, exploration,
verification, and finalization run directly; use the kernel afterwards only when
their result is consumed as a lifecycle gate. Its response never selects
continuation.

Owner-authorized end-to-end mode may follow only these declared branches after
accepted results. It never answers owner decisions, supplies missing mutation,
archive, or bypass authority, or skips a component boundary. Explicit end-to-end
delegation carries checkpoint commit authority only for new stage-owned commits
produced by this playbook. Internal coordination identity remains ZPP runtime state.

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

## 1. Clarify the mixed outcome

Custom instruction: decompose the request only enough to form one accepted change
agreement, preserving explicit relationships among capability, defect, scaffold, and
maintenance concerns. Do not silently split changes or select a specialized playbook
after this generic playbook has begun.

Use `zpps-clarify`. On `exploration-required`, explicitly use `zpps-explore` and
re-enter. On `planning-operation-required`, carry the exact signal into step 2. Pause
on unresolved owner boundaries; otherwise assess the agreement and continue.

## 2. Establish or revise planning

Before the first governed mutation, pass the exact resolved repository roots and
change names plus accepted mutation authority to `zpps-workflow-kernel`. Consume the
structured result from ZPP's runtime coordination command. Do not resolve or ask for
store registration, manifest UUID, owner string, environment override, bundle, or
lease commands in this playbook; ZPP owns those mechanics and reports genuine
conflicts.

Use the exact signaled planning adapter. Without a signal: use
`zpps-propose-change` for a fully understood new change, `zpps-update-change` for
existing artifacts, `zpps-continue-change` for exactly one requested next artifact,
or `zpps-new-change` for scaffold-and-stop. Use `zpps-ff-change` only when the owner
explicitly requests fast-forward planning and the intent is already complete. Apply
kernel guard and result assessment to every mutation.

## 3. Shape accepted observable behavior

Use `zpps-shape-bdd` across the accepted effects. For every public-system obligation,
require independent RED and single executable authority. For non-observable policy,
require the stage to return an evidence-backed `skipped: not applicable` and keep the
obligation normative in OpenSpec. Resolve missing guards and re-enter; pause on
binding or agreement failures.

## 4. Plan utilities

Use `zpps-planning-ponytail` across all accepted responsibilities. Assess its plan or
evidence-backed `skipped: not applicable` as the planning result only. A plan
contradiction returns through an explicit clarification or update action, never
through kernel dispatch.

## 5. Mature utilities

Use `zpps-mature-utilities` with the exact planning result. Require relevant RED and
complete GREEN for every plan, or require this stage to independently return
`skipped: not applicable`. Assess this result separately before wiring.

## 6. Wire applicable public behavior

Use `zpps-wire` for accepted public composition. Take an explicit not-applicable
branch for work with no public composition change. Require the kernel to assess the
observed result without naming a next step.

## 7. Form and synchronize specifications

Use `zpps-form-specs`. For `sync-required`, explicitly use `zpps-sync-specs` with the
returned delta selection and re-enter form-specs for canonical audit. Pause on
duplicate or orphan authority.

## 8. Verify repository and change

Use `zpps-verify-repository` for shaped scenarios and every relevant repository gate.
Then use `zpps-verify-change` with the returned evidence. On
`repository-evidence-required`, explicitly run the named evidence and re-enter. Pause
on incomplete tasks, unmet requirements, divergence, or insufficient evidence.

## 9. Finalize and archive

Use `zpps-finalize`. Explicitly satisfy and re-enter for each
`repository-evidence-required` or `change-verification-required` signal. For
`archive-required`, require explicit archive authority and use the selected single or
bulk archive adapter; it performs any selected specification sync synchronously and
returns `completed`, `cancelled`, `blocked`, or `failed`. Never infer archive
authority, and pause on every non-completed result. Submit a `completed` finalization
result to the kernel for path audit, archive recording, checkpoint, bundle completion,
and final assessment.

Report completion only from `lifecycle-complete`.
