---
name: zpp-scaffold
description: Run the complete ordered ZPP playbook for product-bearing repository or capability structure, with behavior stages applied only when observable behavior exists.
---

# Establish product-bearing structure

This playbook owns the sequence and every conditional use. Use
`zpps-workflow-kernel` before a governed mutation for its exact guard. Read-only
clarification, exploration, verification, and finalization run directly; use the
kernel afterwards only when their result is consumed as a lifecycle gate. Never ask
the kernel which component follows.

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
