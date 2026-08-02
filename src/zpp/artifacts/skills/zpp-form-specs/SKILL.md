---
name: zpp-form-specs
description: Form or reconcile canonical OpenSpec specifications as current authority for the complete mature green product change, then checkpoint the formed specifications before OpenSpec finalization.
---

# Form specifications from green behavior

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Require all of these inputs before forming specifications:

- the live proposal containing the accepted overview and any remaining deferrals;
- one existing capability delta for every new or modified capability declared by the proposal;
- the complete green public feature/fix scenario set;
- the complete green utility implementation and focused tests, plus a current mature-utility checkpoint commit only when that pass produced material tracked utility work;
- all implemented public behavior in the product change;
- the change-wide green integration checkpoint commit.

If any prerequisite is absent or was superseded by a reopened earlier stage, preserve coherent material tracked specification work with a truthful fallback zmem checkpoint before returning to the workflow stage that owns it. When no material tracked specification work exists, return without a commit. Repeat that stage's established checkpoint behavior and rebuild later checkpoints in order. Never form canonical specifications from planned, red, unverified, or historically superseded behavior.

## Reconcile ownership

Canonical specs own the current mature product behavior only. Zmem retains the meaningful temporal sequence that produced it. Do not promote abandoned or superseded chronology, workflow mechanics, trait execution policy, platform choices, diagnostics, or implementation artifacts into product requirements.

1. Read the proposal, every status-reported capability delta, executable feature examples, focused utility tests, implementation, and green checkpoints. Use available code-intelligence tools such as CodeGraph when current internal relationships need inspection.
2. Reconcile each existing capability delta against the complete mature green evidence through `openspec-update-change`. Do not create a declared capability's delta for the first time at this stage; a missing delta reopens clarification.
3. Use `openspec-sync-specs` to promote the reconciled deltas into canonical OpenSpec specifications for the complete product change, only for behavior supported by the green evidence.
4. Preserve stable intent, contract, constraints, invariants, and acceptance obligations in OpenSpec.
5. Leave executable public examples and their concrete paths in Gherkin; do not duplicate them in OpenSpec.
6. Leave utility algorithms, adapter details, and internal edge cases with their focused TDD tests unless they establish a public invariant.
7. Resolve contradictions among canonical baseline, active planning artifacts, and green evidence. Record a newly required decision in the proposal and affected delta instead of assuming an answer; retain earlier directions and the reason for changing them in zmem.
8. Validate that the complete formed specification set describes mature behavior and that no mature public obligation was lost during reconciliation.
9. After specification formation, hand the complete formed specification diff to `zpp-commit-zmem` for a separate checkpoint commit. Add zmem only when formation surfaced a new durable decision, reversal, surprise, or lesson; never repeat an already recorded decision merely to mark specification adoption. If reconciliation is repeated after reopening, create a replacement commit and preserve the earlier one as history.
10. After that commit, hand the validated change explicitly to `openspec-archive-change`; invoke it immediately when automatic progression or explicit end-to-end delegation applies.
11. After finalization returns, require the exact finalized archive path reported by the OpenSpec finalizer. Hand that archive to `zpp-commit-zmem` as a distinct material repository-history checkpoint, and exclude unrelated active changes and disposable utility plans. Do not add zmem merely because finalization moved the change.
12. Re-list active changes and audit the session-local related change set. Require the product change to be archived, every utility companion to be absent, and every consumed internal anchor whose consumer condition is satisfied to be discarded. A genuinely unfinished related change may remain active only under an identified owning stage. Leave unrelated active changes untouched.
13. If any consumed related change remains active without an owning stage, the workflow is incomplete. Report that change and return to its owner; never report overall completion.

The utility plan from a completed TDD pass must already be discarded. Never reconstruct it for specification formation and never sync, archive, summarize, or translate it into canonical specs.

Do not wire features, add utility behavior, or perform the product archive inside this skill. The owning OpenSpec finalizer performs that mutation before this skill evaluates the closure postcondition.
