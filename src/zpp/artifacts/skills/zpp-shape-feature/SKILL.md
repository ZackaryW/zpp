---
name: zpp-shape-feature
description: Translate a fully confirmed ZPP product proposal into the complete Gherkin feature and fix set without step definitions, product wiring, or invented policy, then prepare the change-wide feature-contract checkpoint. Use only after the complete product boundary has converged.
---

# Shape the complete public feature set

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

## Policy boundary

- Translate accepted public behavior; never use BDD to complete or redesign the product contract.
- Do not turn test convenience, diagnostics, exact serialization, filenames, ownership markers, adapter internals, or old interfaces into requirements.
- Assert an exact representation only when the accepted proposal makes that representation part of the product outcome.
- Keep utility edge cases in TDD and platform/runner policy in independent traits.

1. Read the selected change's confirmed proposal before editing a feature file.
2. Inventory every accepted user-visible feature and fix obligation in the complete change and map each to its real public entry point. Ignore incidental observability that the proposal does not make contractual.
3. Write the smallest sufficient Gherkin scenario set that covers all mapped obligations. Keep utility edge cases out of the scenarios and avoid duplicate examples.
4. Create or edit only `.feature` files. Do not create step definitions, environment hooks, test harnesses, fixtures, product code, or utility code at this gate.
5. Review the complete feature set for valid Gherkin structure, coherent public paths, coverage, and duplication without invoking the BDD runner or claiming RED/GREEN evidence. Undefined steps are expected until wiring and prove nothing about product behavior.
6. Reconcile ownership immediately:
   - retain intent, scope, constraints, invariants, and acceptance obligations;
   - remove duplicated executable examples now owned by the feature;
   - never dissolve the underlying contract.
7. Hand the accepted complete intent and feature/fix contract to `zpp-commit-zmem` after initial acceptance and after every later reopening. A prior feature checkpoint remains historical and cannot authorize downstream work against revised features.

Subagents may inspect or draft bounded feature text only when explicitly delegated. They must not run RED/GREEN verification, create bindings, declare a workflow gate satisfied, or create a checkpoint. Verification authority remains with the root agent.

Do not begin or resume utility planning until every accepted public boundary in the change is represented in the approved feature set and the current feature pass has its checkpoint. After that checkpoint, hand the complete feature set to `zpp-plan-utilities`; invoke that skill immediately when automatic progression or explicit end-to-end delegation applies. If an outcome-changing public behavior is unclear, return the whole change to `zpp-clarify-change`. Do not reopen clarification for an implementation choice that can remain free.
