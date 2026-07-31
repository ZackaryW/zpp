---
name: zpp-clarify-change
description: Clarify a complete ZPP change against canonical OpenSpec and temporal zmem history, persisting owner-grounded working decisions into one temporary gating proposal. Use before feature shaping when requirements, constraints, or deferrals remain unsettled.
---

# Clarify a change

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Treat canonical OpenSpec specifications as the long-standing authority for currently accepted product behavior. Treat the active proposal as mutable working state for the current change. Treat zmem as chronological evidence of meaningful decision changes and temporal highlights, never as current product truth or a required dependency graph.

At workflow entry, list the active OpenSpec changes and keep a session-local related set containing the selected product change plus every change this workflow creates, selects, or consumes. Keep unrelated active changes outside that set. Never persist this lifecycle tracking in the product proposal or authored traits.

Before writing the working proposal, identify the affected canonical specifications and recall relevant zmem decisions and lessons by capability, path, and change language. Order relevant records temporally, distinguish later revisions from earlier directions, and compare the latest relevant direction with canonical OpenSpec. A later zmem record signals history that may require reconciliation; it does not silently replace current authority.

## Authority boundary

- Treat canonical OpenSpec as the current baseline and explicit owner corrections as authority for the active change; persist those corrections into its working proposal.
- Use zmem to explain how decisions evolved, including abandoned directions and reversals, without promoting history into current requirements.
- Treat rejected designs, superseded documentation, old implementations, test-harness needs, and deferred capabilities as non-authoritative unless the owner adopts them again.
- Govern how decisions are captured; never choose product behavior merely to complete a proposal or make it easier to test.
- Never promote diagnostics, serialization, filenames, adapter internals, framework conventions, or workflow execution preferences into product requirements without an owner-grounded need.
- Keep platform and framework policy in independent traits. Keep mutation authority with the user/session, never with a trait or this skill.

## Loop

1. Select the relevant active change explicitly. If selection is ambiguous, list changes and ask; never guess.
2. Read its current `proposal.md`. If absent, use the proposal-creation portion of `openspec-propose`, obtain OpenSpec's proposal instructions, and immediately write everything already established from the request and repository evidence. Use `openspec-update-change` for later proposal revisions.
3. Keep an `Unresolved — Do Not Assume` section in the proposal.
4. Ground every remaining decision branch in canonical OpenSpec, explicit owner corrections, and the relevant temporal record. Do not treat an earlier, rejected, or superseded direction as current evidence.
5. Synthesize the complete remaining product decisions into one review batch at behavioral granularity. Recommend an answer only when an accepted requirement logically supports it or the owner requests a recommendation; label every unaccepted option explicitly.
6. Do not request approval after each command, field, filename, behavior group, or edge case. After a partial response, persist every settled correction and present the complete remaining unresolved architecture again, not merely the next small group.
7. Isolate one question only when its answer genuinely changes which major architecture branches exist; after that answer, return to the consolidated review.
8. After the owner answers, update the proposal before asking anything else:
   - incorporate the decision into the relevant section;
   - remove or narrow the resolved item;
   - add newly exposed unresolved branches explicitly.
9. Repeat from grounding.

## Convergence

Before convergence, inventory every required feature, fix, constraint, acceptance obligation, and explicitly deferred item for the whole change. Do not require implementation details that do not change the accepted product outcome.

When no outcome-changing branch remains across the complete change, present a short restatement. Converge only after the owner confirms it. After convergence, hand the complete proposal to `zpp-shape-feature`; invoke that skill immediately when automatic progression or explicit end-to-end delegation applies.

If this stage was reopened from later work, require that the later stage first preserved any coherent material tracked work through a truthful fallback zmem checkpoint. When no such work exists, require no commit. Invalidate its gate state. Do not resume utility TDD, wiring, or specification formation from prior checkpoints. Send the revised complete proposal through feature shaping again; the revised complete feature contract must receive a replacement feature checkpoint before the workflow can cross that boundary.

Do not create specs, design, tasks, feature files, or implementation. Specifications are formalized only after behavior is mature and green.
