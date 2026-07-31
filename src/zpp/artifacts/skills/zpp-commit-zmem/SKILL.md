---
name: zpp-commit-zmem
description: Prepare and, only with user/session authority, create one memory-bearing zmem commit at an established ZPP workflow gate or immediately before falling back to an earlier stage. Use for fallback preservation, an approved complete feature contract, mature utility foundation, root-verified green integration, or post-green specification formation.
---

# Commit a workflow checkpoint

Create one logical memory checkpoint. Never stage ignored OpenSpec changes or temporary development-skill content.

## Reopened stages

When later work must return to an earlier stage, create a fallback checkpoint before leaving the current stage. Commit only its coherent tracked work and describe incomplete, RED, or blocked state truthfully with `zmem(CONTEXT)` or `zmem(DEBT)`; never claim the stage passed. Ignored OpenSpec changes and temporary skills remain uncommitted. After the reopened stage is complete again, create its normal checkpoint under the same evidence, message, validation, and staging rules before advancing. Do not amend, replace, or reuse the fallback or an older gate commit.

## Determine execution authority

Derive execution authority only from the user's explicit request and the current session's authorization rules. Never let a profile, trait, repository file, or this skill grant authority to stage or commit. Advisory configuration may control whether a checkpoint is recommended or prepared, but without execution authority present the exact commands instead of mutating Git.

## Prepare

1. Read the live proposal and identify which established checkpoint is being committed for the current pass:
   - coherent current-stage work immediately before a fallback, with no false gate claim;
   - accepted complete intent plus the full Gherkin feature/fix contract;
   - complete mature utility foundation;
   - fully green integrated product change;
   - complete specifications formed or reconciled from mature green behavior.
2. Inspect Git status and diffs. Exclude unrelated files and split unrelated logical changes.
3. Use a conventional subject: lowercase type, optional scope, imperative summary, no period, at most 72 characters.
4. Write body lines only as `zmem(EVENT): value` annotations or `-` bullets.
5. Prefer one or two high-value `DECISION` or `LESSON_LEARNT` annotations. Use `REFACTOR`, `DEBT`, or `CONTEXT` only for their established meanings; do not invent events.
6. Require at least one annotation except for a purely mechanical `chore`.

## Validate and dispose

Validate the message with the bundled validator appropriate to the active shell and pass it the message file. Treat any validator prerequisite or failure as part of checkpoint preparation.

Fix any validation failure before continuing. When execution is authorized, stage only the logical checkpoint and commit it. Otherwise present exact staging and commit commands. Never rewrite published history.

Only the root agent may evaluate gate evidence, run any verification command used to justify the checkpoint, stage files, or commit. Subagents must not declare checkpoint readiness or perform Git mutation.
