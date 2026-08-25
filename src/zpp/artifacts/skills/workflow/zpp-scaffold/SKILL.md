---
name: zpp-scaffold
description: Run the complete ordered ZPP playbook for product-bearing repository or capability structure, with behavior stages applied only when observable behavior exists.
---

# Establish product-bearing structure

## Registered execution

Before the first lifecycle stage or operation, identify the exact repository and
intended OpenSpec change name, then run:

`zpp workflow run start zpp-scaffold --root <root> --change <change>`

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

## 1. Define the structural outcome

Custom instruction: distinguish structure required to host accepted product behavior
from artifact-only maintenance, installation, or compatibility work. Identify the
owning package/application, public composition boundary, required files, and explicit
non-goals.

Use `zpps-clarify` with the request, roots, conventions evidenced in the repository,
and owner decisions. Satisfy `exploration-required` through one explicit
`zpps-explore` use and re-enter. Pause on unresolved structure ownership.

## 2. Establish the OpenSpec planning boundary

Before the first governed mutation, pass the exact resolved repository roots and
change names plus accepted mutation authority to `zpps-workflow-kernel`. Consume the
structured result from ZPP's runtime coordination command. Do not resolve or ask for
store registration, manifest UUID, owner string, environment override, bundle, or
lease commands in this playbook; ZPP owns those mechanics and reports genuine
conflicts.

Use `zpps-new-change` and stop at its published scaffold boundary when the owner asked
only to start planning. For an understood end-to-end scaffold, use
`zpps-propose-change`; for an existing change, use `zpps-update-change` or one
explicit `zpps-continue-change` action. Guard and assess every mutation. Continue
when the plan names the product-bearing owner and excludes OpenSpec installation,
generated skills, and backwards-compatibility aliases.

## 3. Shape behavior when the scaffold is observable

Use `zpps-shape-bdd` with the accepted scaffold effects. When the scaffold exposes or
changes public behavior, resolve any `kernel-assessment-required` and require an
independent RED capability feature with single executable authority. Otherwise
require the stage itself to return an evidence-backed `skipped: not applicable`;
never let the playbook manufacture that outcome or fabricate BDD for filesystem
wording or prompt policy.

## 4. Plan reusable structure

Use `zpps-planning-ponytail` for any reusable bootstrap utility. Assess its plan or
evidence-backed `skipped: not applicable` as the planning result only. Pause if the
requested structure conflicts with the repository's real ownership model.

## 5. Mature reusable structure

Use `zpps-mature-utilities` with the exact planning result. Require exact RED/GREEN
targets for a plan, or require this stage to independently return
`skipped: not applicable` when planning found no utility responsibility.

## 6. Wire the owning surface

Use `zpps-wire` when the scaffold has an accepted public composition point. If the
scaffold is structure-only, require the stage to return `skipped: not applicable` and
preserve focused structural verification evidence. Assess either result through the
kernel before continuing.

## 7. Form and synchronize specifications

Use `zpps-form-specs`; on `sync-required`, explicitly use `zpps-sync-specs` and
re-enter for canonical audit.

## 8. Verify repository and change

Use `zpps-verify-repository` for affected and complete tests plus interpreter/lock,
lint, format, and clean build, then use `zpps-verify-change`, supplying any additional
repository evidence it signals.

## 9. Finalize and archive

Use `zpps-finalize` with all results. Explicitly satisfy
`repository-evidence-required` or `change-verification-required` and re-enter. For
`archive-required`, require explicit archive authority and use the exact single or
bulk archive adapter; it performs any selected specification sync synchronously and
returns `completed`, `cancelled`, `blocked`, or `failed`. Never infer archive
authority, and pause on every non-completed result. Submit completed final evidence
to the kernel; declare completion only from `lifecycle-complete`.
