---
name: zpp-new-feature
description: Run the complete ordered ZPP playbook for a new externally observable capability, using explicit bounded components and visible branches.
---

# Deliver a new public capability

## Registered execution

Before the first lifecycle stage or operation, identify the exact repository and
intended OpenSpec change name, then run:

`zpp workflow run start zpp-new-feature --root <root> --change <change>`

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
`zmem-author-commits`; preserve unrelated work. End-to-end mode never supplies an
owner decision or missing mutation, archive, abandonment, or bypass authority.

## Establish the capability agreement

Custom instruction: frame one public capability, its consumers, observable behavior,
compatibility boundary, and acceptance conditions without choosing an implementation.

Use `zpps-clarify` with the request, exact roots, owner statements, and current
contract evidence. On `exploration-required`, use `zpps-explore` with the returned
question and re-enter clarification. On `planning-operation-required`, retain the
signal for planning. On `blocked`, pause. On `completed`, assess the result through
the kernel and return it to registered execution.

## Establish or reconcile the OpenSpec change

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
  complete planning set. In owner-authorized end-to-end mode, return its accepted
  result without requesting fresh permission.
- Owner requested scaffold-only planning -> use `zpps-new-change` and stop after its
  published boundary unless the owner separately authorizes continuation.

Apply pre/post kernel assessments to every mutating use. Pause on adapter blockers.
Return the accepted planning result to registered execution.

## Shape executable behavior

Use `zpps-shape-bdd` with the accepted agreement, exact OpenSpec root, capability
owner, provisional examples, and binding inventory. Require transfer of every
testable example to capability BDD and trace-only OpenSpec anchors. On
`kernel-assessment-required`, obtain the named guard and re-enter. On `blocked`,
pause. Assess `completed` through the kernel and return it.

## Plan utilities

Use `zpps-planning-ponytail` with shaped behavior and dependency evidence. If it
returns `skipped: not applicable`, assess that planning result without treating it as
a maturation result. If it returns a plan, assess its exact revision. Pause on any
contradiction, and return only after this distinct stage is accepted.

## Mature utilities

Use `zpps-mature-utilities` with the exact planning result and relevant RED targets.
For a planning skip, require this stage to independently confirm and return
`skipped: not applicable`. Otherwise require verified utility GREEN. Assess the
distinct maturation result before continuing.

## Wire the public capability

Use `zpps-wire` with approved scenarios, bindings, proven utilities, and the actual
public composition owner. Pause if wiring requires a new owner decision or revised
plan. Return after focused public evidence is accepted.

## Form and synchronize specifications

Use `zpps-form-specs` with delta/canonical paths reported by OpenSpec, bindings, and
mature evidence. On `sync-required`, explicitly use `zpps-sync-specs` with exactly
the returned delta set, then re-enter `zpps-form-specs` with its result. Never let
either component invoke the other. Continue only after the canonical authority audit
returns `completed` and the kernel accepts it.

## Verify repository and change

Use `zpps-verify-repository` with scenario-selected BDD, focused and complete tests,
interpreter/lock, lint, format, and clean-build targets. Resolve
`owner-choice-required` before proceeding. Then use `zpps-verify-change` with the
planning artifacts, implementation, bindings, and supplied repository evidence. On
`repository-evidence-required`, run only the newly requested evidence through
`zpps-verify-repository` and re-enter verification. Pause on any failure.

## Finalize and archive

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
