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
accepted results. It never answers owner decisions, supplies missing durable-owner,
mutation, checkpoint, or archive authority, or skips a component boundary.

## 1. Define the structural outcome

Custom instruction: distinguish structure required to host accepted product behavior
from artifact-only maintenance, installation, or compatibility work. Identify the
owning package/application, public composition boundary, required files, and explicit
non-goals.

Use `zpps-clarify` with the request, roots, conventions evidenced in the repository,
and owner decisions. Satisfy `exploration-required` through one explicit
`zpps-explore` use and re-enter. Pause on unresolved structure ownership.

## 2. Establish the OpenSpec planning boundary

Before the first governed mutation, require the durable Bundler owner, exact
registered store UUID, and exact change member. A repo-local root may be inspected
and used as `repo:<path>` trace identity, but pause with
`store-registration-required` until the current Bundler CLI can lease the exact
registered member. Never infer the owner or UUID.

Use `zpps-new-change` and stop at its published scaffold boundary when the owner asked
only to start planning. For an understood end-to-end scaffold, use
`zpps-propose-change`; for an existing change, use `zpps-update-change` or one
explicit `zpps-continue-change` action. Guard and assess every mutation. Continue
when the plan names the product-bearing owner and excludes OpenSpec installation,
generated skills, and backwards-compatibility aliases.

## 3. Shape behavior when the scaffold is observable

Condition: the accepted scaffold exposes or changes public behavior. Use
`zpps-shape-bdd`, resolve any `kernel-assessment-required`, and require an independent
RED capability feature with single executable authority.

Otherwise record a truthful specification-only obligation and an accepted
`not-applicable` assessment; never fabricate BDD for filesystem wording or prompt
policy.

## 4. Plan and mature reusable structure

Use `zpps-planning-ponytail` for any reusable bootstrap utility. On a returned plan,
use `zpps-mature-utilities` with exact RED/GREEN targets. On
`skipped: not applicable`, continue without manufacturing a utility. Pause if the
requested structure conflicts with the repository's real ownership model.

## 5. Wire the owning surface

Use `zpps-wire` when the scaffold has an accepted public composition point. If the
scaffold is structure-only, take the playbook's explicit not-applicable branch and
preserve focused structural verification evidence. Assess either result through the
kernel before continuing.

## 6. Form, verify, and finalize

Use `zpps-form-specs`; on `sync-required`, explicitly use `zpps-sync-specs` and
re-enter for canonical audit. Use `zpps-verify-repository` for affected and complete
tests plus interpreter/lock, lint, format, and clean build, then use
`zpps-verify-change`, supplying any additional repository evidence it signals.

Use `zpps-finalize` with all results. Explicitly satisfy
`repository-evidence-required` or `change-verification-required` and re-enter. For
`archive-required`, require explicit archive authority and use the exact single or
bulk archive adapter; it performs any selected specification sync synchronously and
returns `completed`, `cancelled`, `blocked`, or `failed`. Never infer archive
authority, and pause on every non-completed result. Submit completed final evidence
to the kernel; declare completion only from `lifecycle-complete`.
