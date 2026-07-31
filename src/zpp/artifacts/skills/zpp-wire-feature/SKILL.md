---
name: zpp-wire-feature
description: Create the BDD bindings and compose the complete proven utility foundation into every approved feature and fix, then let the root agent verify the integrated set and prepare the change-wide green checkpoint. Use only after all planned utilities are green and checkpointed and their disposable planning change has been discarded.
---

# Wire and integrate the complete change

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Require these inputs before production wiring:

- a fully converged product-change proposal;
- the complete approved feature/fix set, containing no premature bindings;
- every planned utility green with focused tests and the current change-wide utility checkpoint, repeated after any reopening that revised its inputs;
- no retained companion utility-planning change from the completed pass.

## Wiring

Treat the proposal and approved Gherkin scenarios as the complete product authority. Do not convert integration-harness needs, agent adapter mechanics, framework conventions, or implementation discoveries into new product policy.

1. Create thin step definitions and required integration fixtures that bind every approved scenario to the real public system. Never use source inspection, no-op steps, or direct utility calls as substitutes for public behavior.
2. Compose the proven utilities through every real feature/fix path with the smallest integration code.
3. Do not create new utility behavior inside wiring. If any utility logic is missing, stop the entire wiring phase, create a truthful fallback zmem checkpoint of coherent tracked wiring work, inspect the current source graph with available code-intelligence tools such as CodeGraph, and create a fresh disposable utility OpenSpec gate for the reopened TDD pass. Resume wiring only after the revised complete utility foundation receives its replacement checkpoint and that temporary gate is discarded.
4. Keep utility edge-case assertions in TDD; do not repeat them in Gherkin.
5. After all bindings and product paths are assembled, the root agent runs the complete relevant integration suite through the profile-resolved BDD runner. Rerun only after a material correction.
6. If implementation discovers a decision that reopens an earlier stage, create the fallback checkpoint before leaving wiring, then reconcile the decision in its owning proposal stage.
7. Hand the root-verified green integrated product change to `zpp-commit-zmem` for the current pass. If an earlier stage was reopened, repeat every displaced checkpoint in order and create a replacement green-integration checkpoint rather than reusing or amending the old one.

Subagents may prepare explicitly delegated bounded edits, but they must not execute RED/GREEN commands, interpret verification output, declare the integration gate green, or create the checkpoint. The root agent exclusively owns integration verification and gate state.

Do not formalize canonical OpenSpec specs here. That occurs only after mature green behavior is ready for reconciliation.

