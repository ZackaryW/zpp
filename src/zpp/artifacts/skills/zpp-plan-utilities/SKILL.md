---
name: zpp-plan-utilities
description: Create a disposable complete utility OpenSpec gate for an already shaped ZPP change. Use to inspect the current code, investigate mature dependencies across the approved feature/fix set, present justified utility changes with signature-only prototypes, and settle the whole temporary plan before TDD.
---

# Plan utilities and dependencies

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

## Resolve the mode

Use the selected profile's resolved trait configuration as advisory workflow policy for automatic versus manual planning and whether utility-only work requires prior clarification. Do not read an arbitrary config file or invent a default. If ZPP cannot yet resolve the setting, ask which behavior applies for this run; do not record session workflow mode as a product requirement.

Manual planning is a bounded design review, not a one-question interview. Present several related dependency and utility candidates together so the owner can accept, reject, or revise each candidate in one response. Reserve one-at-a-time questioning for a decision that blocks forming the batch.

## Discovery

Keep ownership strict: this skill plans utilities from accepted product needs but does not add product behavior. Record project-specific dependency choices in the companion utility change, never in this platform-neutral skill or its future workflow trait.

1. Read the fully converged product-change proposal and its complete approved Gherkin feature/fix set. Require the current feature-contract checkpoint, including a replacement checkpoint when that stage was reopened. Refuse a partial or revised-but-uncheckpointed product boundary or feature set.
2. Inspect existing utilities, dependencies, adapters, tests, and project conventions before proposing new code. On later visits, use available code-intelligence tools such as CodeGraph to reconstruct current structure and consumers from source; never treat a prior utility plan as durable architecture documentation.
3. Open or update one disposable companion utility OpenSpec change that gates every utility to add, modify, replace, or remove before product wiring. Add it to the workflow's related change set with disposal after its complete verified TDD pass as its owning terminal condition.
4. For each needed responsibility across the complete product change, investigate whether a maintained dependency already provides it. Use current primary evidence when package maturity can change.
5. Report maturity evidence and trade-offs without inventing an acceptance threshold. If evidence does not establish the choice, ask.
6. Propose a custom utility only when justified by reuse, a nontrivial invariant, or a valuable test seam.
7. Present multiple related candidates in one bounded plan. For each candidate, state its responsibility, justification, focused test boundary, intended consumers across the feature set, and dependency choice.
8. Show the minimal shape of every proposed function or adapter in a language-appropriate fenced code block. Include signatures or declarations only—never bodies, algorithms, or speculative implementation.
9. Prefer a thin adapter when a dependency fits. Plan tests for ZPP's usage contract, not the dependency's internals.

After the owner responds to a batch, persist every accepted, rejected, and revised decision before presenting another batch. Converge only when the utility change accounts for the entire product change. Do not write tests, create feature bindings, run RED/GREEN verification, or write production code, and never start TDD from a partial utility plan.

After the complete utility plan is accepted, hand it to `zpp-mature-utilities`; invoke that skill immediately when automatic progression or explicit end-to-end delegation applies.

The companion change is temporary execution scaffolding. Never sync, archive, transform, or quote it into canonical specifications. Its only downstream consumers are the current TDD pass and any fallback reconciliation before that pass reaches maturity. After root-owned verification and any justified mature-utility zmem checkpoint, discard the complete companion change. When the accepted plan requires no material utility changes, discard it without creating a negation checkpoint.

If TDD or wiring reopens this plan, preserve downstream work with a truthful fallback zmem checkpoint only when coherent material tracked work exists. Otherwise return without a commit. Then suspend that stage and reconcile the complete utility change again. When revised utilities later regain complete maturity, create a replacement mature-utility checkpoint only if that pass produced material tracked utility work. Any justified fallback and earlier utility checkpoint remain historical only.

Subagents may perform explicitly delegated research or inspection, but they must not execute RED/GREEN commands, interpret gate evidence, or declare a workflow gate satisfied. Verification authority remains with the root agent.
