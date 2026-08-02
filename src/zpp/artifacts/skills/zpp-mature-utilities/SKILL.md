---
name: zpp-mature-utilities
description: Develop a complete agreed disposable utility plan through strict fail-first TDD before feature wiring, checkpoint material utility work, and discard the temporary gate after verification.
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

Complete TDD for every utility and adapter in the utility change before any product wiring. If a needed utility was omitted, stop and preserve coherent material tracked utility work through `zpp-commit-zmem`, using zmem only for a durable temporal highlight, then reopen `zpp-plan-utilities`; do not wire around the gap. If implementation invalidates the product proposal or public feature set, apply the same material-work condition before returning to the owning earlier gate. Rebuild every displaced downstream gate in order; never resume from RED/GREEN or a checkpoint produced against superseded inputs.

The root agent runs every focused utility suite and the relevant broader unit suite, avoiding duplicate executions when no material state changed. If the pass produced material tracked utility work, hand the complete mature utility foundation to `zpp-commit-zmem` for one checkpoint commit; add zmem only for a new durable temporal highlight. If the accepted plan requires no utility changes, create no checkpoint; the negative conclusion is not durable zmem. If this stage was reopened, create a replacement mature-utility checkpoint only when the revised pass produced material tracked utility work; preserve any earlier checkpoint as history.

After any required checkpoint succeeds—or immediately when no material utility work required one—perform this skill's explicit verified discard of the disposable companion before feature wiring; no installed OpenSpec skill owns disposal. Re-list active changes and require that companion to be absent. Never sync or archive its plan into canonical OpenSpec specs. The green utility implementation, focused tests, and checkpoint are the durable evidence; future visits rediscover the current internal graph from source with available code-intelligence tools such as CodeGraph. Do not hand off while the disposed companion remains active. Then hand the complete utility foundation to `zpp-wire-feature`; invoke that skill immediately when automatic progression or explicit end-to-end delegation applies.
