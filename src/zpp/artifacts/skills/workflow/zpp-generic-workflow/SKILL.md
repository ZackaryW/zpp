---
name: zpp-generic-workflow
description: Run the complete current ZPP playbook for mixed, maintenance-oriented, or otherwise unspecialized product outcomes.
---

# Run the generic current workflow

## Registered execution

Before the first lifecycle stage or operation, identify the exact repository and
intended OpenSpec change name, then run:

`zpp workflow run start zpp-generic-workflow --root <root> --change <change>`

Starting is mandatory and idempotent. It creates only target-scoped reminder
state; it grants no mutation, checkpoint, archive, abandonment, or bypass
authority and does not acquire a Bundler lease.

Treat the returned checklist, including direct user edits, as the current stage
order. For each pending stage, select its mapped component and apply only the
matching custom configuration and branches below. Ask `zpps-workflow-kernel` to
check that already selected action and later assess its actual result. Preserve any
out-of-sequence warning visibly, but do not treat reminder state or the kernel as a
dispatcher.

Owner-authorized end-to-end mode may follow these declared branches after accepted
results and carries checkpoint authority only for new coherent stage-owned diffs.
Checkpoint each material accepted stage through the kernel and
`zmem-author-commits`; preserve unrelated work and keep every path under the active
OpenSpec `changeRoot` out of checkpoint commits while continuing to update its tasks
in the working tree. End-to-end mode never supplies an
owner decision or missing mutation, archive, abandonment, or bypass authority.

## Clarify the mixed outcome

Custom instruction: decompose the request only enough to form one accepted change
agreement, preserving explicit relationships among capability, defect, scaffold, and
maintenance concerns. Do not silently split changes or select a specialized playbook
after this generic playbook has begun.

Use `zpps-clarify`. On `exploration-required`, explicitly use `zpps-explore` and
re-enter. On `planning-operation-required`, carry the exact signal into planning. Pause
on unresolved owner boundaries; otherwise assess the agreement and continue.

## Establish or revise planning

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

## Shape accepted observable behavior

Use `zpps-shape-bdd` across the accepted effects. For every public-system obligation,
require independent RED and single executable authority. For non-observable policy,
require the stage to return an evidence-backed `skipped: not applicable` and keep the
obligation normative in OpenSpec. Resolve missing guards and re-enter; pause on
binding or agreement failures.

## Plan utilities

Use `zpps-planning-ponytail` across all accepted responsibilities. Assess its plan or
evidence-backed `skipped: not applicable` as the planning result only. A plan
contradiction returns through an explicit clarification or update action, never
through kernel dispatch.

## Mature utilities

Use `zpps-mature-utilities` with the exact planning result. Require relevant RED and
complete GREEN for every plan, or require this stage to independently return
`skipped: not applicable`. Assess this result separately before wiring.

## Wire applicable public behavior

Use `zpps-wire` for accepted public composition. Take an explicit not-applicable
branch for work with no public composition change. Require the kernel to assess the
observed result without naming a next step.

## Form and synchronize specifications

Use `zpps-form-specs`. For `sync-required`, explicitly use `zpps-sync-specs` with the
returned delta selection and re-enter form-specs for canonical audit. Pause on
duplicate or orphan authority.

## Verify repository and change

Use `zpps-verify-repository` for shaped scenarios and every relevant repository gate.
Then use `zpps-verify-change` with the returned evidence. On
`repository-evidence-required`, explicitly run the named evidence and re-enter. Pause
on incomplete tasks, unmet requirements, divergence, or insufficient evidence.

## Finalize and archive

Use `zpps-finalize`. Explicitly satisfy and re-enter for each
`repository-evidence-required` or `change-verification-required` signal. For
`archive-required`, require explicit archive authority and use the selected single or
bulk archive adapter; it performs any selected specification sync synchronously and
returns `completed`, `cancelled`, `blocked`, or `failed`. Never infer archive
authority, and pause on every non-completed result. Submit a `completed` finalization
result to the kernel for path audit, archive recording, checkpoint, bundle completion,
and final assessment.

Report completion only from `lifecycle-complete`.
