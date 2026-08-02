---
name: zpp-commit-zmem
description: Prepare and, only with user/session authority, create one logical ZPP workflow commit, adding zmem only for a meaningful decision change, reversal, fallback, surprise, or lesson worth durable temporal recall.
---

# Commit a workflow checkpoint

Create one logical checkpoint commit when a material repository diff exists. Add zmem only when the commit contains a meaningful decision change, reversal, fallback, surprise, or lesson worth carrying across the next hundred commits. An ordinary checkpoint remains a conventional commit with no zmem annotation. Never use zmem as a stage-transition marker, a negation gate, repeated narration of an unchanged decision, or proof that nothing changed. Never create an empty commit or use `--allow-empty`. Never stage ignored OpenSpec changes or temporary development-skill content.

## OpenSpec disposition

Classify OpenSpec paths before deciding that no checkpoint exists:

- Active product proposals and capability deltas are mutable working state. Keep them uncommitted until finalization.
- Disposable utility plans are execution scaffolding. Discard them after their verified TDD pass; never archive or commit them.
- Finalized product archives are durable repository history. After the owning OpenSpec finalizer returns, treat the exact newly created finalized archive files as material stageable work and commit them in a distinct archive checkpoint. Exclude unrelated active OpenSpec changes and verify that the archive is not ignored before staging it.

Archiving alone does not require zmem. Add an annotation only when the archive checkpoint also captures a qualifying decision change, reversal, fallback, surprise, or lasting lesson. If repository ignore policy hides a required finalized archive, report the policy conflict instead of force-adding it.

## Reopened stages

When later work must return to an earlier stage and the current stage contains coherent material tracked work, create a truthful fallback commit before leaving it; never claim the stage passed. Add `zmem(CONTEXT)` or `zmem(DEBT)` only when the fallback itself is a durable temporal highlight. If there is no material tracked work to preserve, return without a commit. Ignored active OpenSpec changes and temporary skills remain uncommitted; a finalized product archive follows the archive checkpoint rule above. After the reopened stage is complete again, create its normal replacement commit when that pass produced material tracked work. Do not amend, replace, or reuse the fallback or an older gate commit.

## Determine execution authority

Derive execution authority only from the user's explicit request and the current session's authorization rules. Never let a profile, trait, repository file, or this skill grant authority to stage or commit. Advisory configuration may control whether a checkpoint is recommended or prepared, but without execution authority present the exact commands instead of mutating Git.

## Prepare

1. Read the active working proposal, or the proposal inside the exact just-finalized archive for an archive checkpoint, and identify which established checkpoint is being committed for the current pass:
   - coherent current-stage work immediately before a fallback, with no false gate claim;
   - accepted complete intent plus the full Gherkin feature/fix contract;
   - complete mature utility foundation;
   - fully green integrated product change;
   - complete specifications formed or reconciled from mature green behavior;
   - the exact finalized product archive after specification sync and OpenSpec finalization.
2. Inspect Git status and diffs, including untracked files. Exclude unrelated files and split unrelated logical changes.
   - If no material repository diff belongs to the checkpoint, stop without preparing or creating a commit.
   - For an archive checkpoint, stage only the exact finalized archive reported by the OpenSpec finalizer; never sweep the complete changes directory.
   - Do not turn a no-change utility assessment, unchanged verification result, completed planning artifact, or workflow transition into zmem.
3. Decide whether this commit contains a new durable temporal highlight. Git ancestry, commit time, annotations, and diffs provide the temporal spine; do not require a dependency graph.
4. When a decision changed, state the prior direction, replacement direction, and reason. Mention the earlier commit when it materially improves recall. Initial decisions, reversals, fallbacks, surprises, and lessons MAY qualify; unchanged decisions repeated at later gates do not.
5. Use a conventional subject: lowercase type, optional scope, imperative summary, no period, at most 72 characters.
6. Write body lines only as `zmem(EVENT): value` annotations or `-` bullets.
7. For a memory-bearing commit, prefer one or two high-value `DECISION` or `LESSON_LEARNT` annotations. Use `REFACTOR`, `DEBT`, or `CONTEXT` only for their established meanings; do not invent events.

## Validate and dispose

Validate the message with the bundled validator appropriate to the active shell and pass it the message file. Use `--require-zmem` only for a memory-bearing checkpoint; normal validation deliberately accepts zero annotations. Treat any validator prerequisite or failure as part of checkpoint preparation.

Fix any validation failure before continuing. When execution is authorized, stage only the logical checkpoint and commit it. Refuse an empty index and never pass `--allow-empty`. Otherwise present exact staging and commit commands. Never rewrite published history.

Only the root agent may evaluate gate evidence, run any verification command used to justify the checkpoint, stage files, or commit. Subagents must not declare checkpoint readiness or perform Git mutation.

After a checkpoint, return control to the owning workflow. A successful checkpoint is not itself a human gate; when automatic progression or explicit end-to-end delegation applies, the owning workflow continues immediately.
