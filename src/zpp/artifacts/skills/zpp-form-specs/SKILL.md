---
name: zpp-form-specs
description: Form or reconcile canonical OpenSpec specifications for the complete mature green product change, then create a separate change-wide specification-formation zmem checkpoint. Use only after every required feature, fix, and utility is green and the integrated change checkpoint has been committed.
---

# Form specifications from green behavior

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Require all of these inputs before forming specifications:

- the live proposal containing the accepted intent and decisions;
- the complete green public feature/fix scenario set;
- the complete green utility implementation and focused tests, plus a current mature-utility checkpoint only when that pass produced material tracked utility work;
- all implemented public behavior in the product change;
- the change-wide green integration zmem checkpoint.

If any prerequisite is absent or was superseded by a reopened earlier stage, preserve coherent material tracked specification work with a truthful fallback zmem checkpoint before returning to the workflow stage that owns it. When no material tracked specification work exists, return without a commit. Repeat that stage's established checkpoint behavior and rebuild later checkpoints in order. Never form canonical specifications from planned, red, unverified, or historically superseded behavior.

## Reconcile ownership

Canonical specs own mature product behavior only. Do not promote workflow mechanics, trait execution policy, platform choices, diagnostics, or implementation artifacts into product requirements.

1. Read the proposal, executable feature examples, focused utility tests, implementation, and green checkpoints. Use available code-intelligence tools such as CodeGraph when current internal relationships need inspection.
2. Form or update canonical OpenSpec specifications for the complete product change, only for behavior supported by the green evidence.
3. Preserve stable intent, contract, constraints, invariants, and acceptance obligations in OpenSpec.
4. Leave executable public examples and their concrete paths in Gherkin; do not duplicate them in OpenSpec.
5. Leave utility algorithms, adapter details, and internal edge cases with their focused TDD tests unless they establish a public invariant.
6. Resolve contradictions against the live proposal and evidence. Record a newly required decision in the proposal instead of assuming an answer.
7. Validate that the complete formed specification set describes mature behavior and that no mature public obligation was lost during reconciliation.
8. Hand the separate change-wide specification-formation checkpoint to `zpp-commit-zmem` for the current pass. If specification reconciliation is repeated after reopening, create a replacement checkpoint under the same criteria and preserve the earlier one as history.
9. After that checkpoint, hand the validated change to the owning OpenSpec finalization workflow; invoke it immediately when automatic progression or explicit end-to-end delegation applies.

The utility plan from a completed TDD pass must already be discarded. Never reconstruct it for specification formation and never sync, archive, summarize, or translate it into canonical specs.

Do not wire features, add utility behavior, archive the change, or infer a change-closure policy in this skill.
