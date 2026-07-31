---
name: zpp-mature-utilities
description: Develop a complete agreed disposable utility plan through strict fail-first TDD before feature wiring. Use only after the companion utility OpenSpec gate accounts for every utility needed by the full product change; discard that gate after green verification and its zmem checkpoint.
---

# Mature utilities through TDD

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Read the complete accepted utility/dependency change. Do not begin from a partial plan, add an unplanned abstraction, or silently change a dependency choice.

Implement only utility policy grounded in that change. Do not import product behavior, framework preferences, or speculative reuse into the utility layer; return each gap to its owning proposal or platform trait.

The root agent exclusively owns every RED/GREEN command, result interpretation, and utility-gate declaration. Subagents may prepare explicitly delegated bounded research or edits, but must not run tests, claim RED or GREEN, or create the checkpoint.

For each utility or adapter:

1. Write one focused test for the next utility behavior.
2. Run that exact target and verify RED fails for the intended missing or wrong behavior.
3. Write the smallest implementation that makes the target green.
4. Re-run the same target.
5. Refactor only while green; add no behavior during refactoring.
6. Repeat for meaningful internal edge cases.

Test a dependency adapter at ZPP's usage boundary. Do not retest the mature dependency's implementation.

Complete TDD for every utility and adapter in the utility change before any product wiring. If a needed utility was omitted, stop and prepare a truthful fallback checkpoint of the current coherent utility work through `zpp-commit-zmem`, then reopen `zpp-plan-utilities`; do not wire around the gap. If implementation invalidates the product proposal or public feature set, create the same fallback checkpoint before returning to the owning earlier gate. Rebuild every displaced downstream gate in order; never resume from RED/GREEN or a checkpoint produced against superseded inputs.

The root agent runs every focused utility suite and the relevant broader unit suite, avoiding duplicate executions when no material state changed. Then hand the complete mature utility foundation to `zpp-commit-zmem` for the current pass. If this stage was reopened, create a replacement mature-utility checkpoint under the same criteria before feature wiring resumes; preserve the earlier checkpoint as history.

After that checkpoint succeeds, delete the disposable companion utility change before feature wiring. Never sync or archive its plan into canonical OpenSpec specs. The green utility implementation, focused tests, and zmem checkpoint are the durable evidence; future visits rediscover the current internal graph from source with available code-intelligence tools such as CodeGraph. Stop before feature wiring.

