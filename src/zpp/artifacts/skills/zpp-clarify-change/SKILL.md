---
name: zpp-clarify-change
description: Clarify a complete ZPP change against canonical OpenSpec and temporal zmem history, maintaining the OpenSpec proposal overview and capability-specific delta specs as one coherent working contract. Use before feature shaping when requirements, constraints, or deferrals remain unsettled.
---

# Clarify a change

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Treat canonical OpenSpec specifications as the long-standing authority for currently accepted product behavior. Treat the active proposal and capability delta specs as mutable working state for the current change. Treat zmem as chronological evidence of meaningful decision changes and temporal highlights, never as current product truth or a required dependency graph.

At workflow entry, list the active OpenSpec changes and keep a session-local related set containing the selected product change plus every change this workflow creates, selects, or consumes. Keep unrelated active changes outside that set. Never persist this lifecycle tracking in the product proposal or authored traits.

Before writing the working artifacts, identify the affected canonical specifications and recall relevant zmem decisions and lessons by capability, path, and change language. Order relevant records temporally, distinguish later revisions from earlier directions, and compare the latest relevant direction with canonical OpenSpec. A later zmem record signals history that may require reconciliation; it does not silently replace current authority.

## Authority boundary

- Treat canonical OpenSpec as the current baseline and explicit owner corrections as authority for the active change; persist overview and unresolved decisions in the proposal and settled behavior in its owning capability delta.
- Use zmem to explain how decisions evolved, including abandoned directions and reversals, without promoting history into current requirements.
- Treat rejected designs, superseded documentation, old implementations, test-harness needs, and deferred capabilities as non-authoritative unless the owner adopts them again.
- Govern how decisions are captured; never choose product behavior merely to complete a proposal or make it easier to test.
- Never promote diagnostics, serialization, filenames, adapter internals, framework conventions, or workflow execution preferences into product requirements without an owner-grounded need.
- Keep platform and framework policy in independent traits. Keep mutation authority with the user/session, never with a trait or this skill.

## Loop

1. Select the relevant active change explicitly. If selection is ambiguous, list changes and ask; never guess.
2. Read the selected schema status and every existing planning artifact. If the change is absent, use `openspec-propose` and follow the selected schema's complete artifact graph and instructions; do not impose ZPP-specific artifact omissions. Use `openspec-update-change` for later revisions.
3. Keep motivation, scope, capability inventory, impact, and an `Unresolved — Do Not Assume` section in `proposal.md`. Require one status-reported delta at `specs/<capability>/spec.md` for every new or modified capability declared by the proposal.
4. Immediately write everything already established from the request and repository evidence: change-wide overview belongs in the proposal, while settled normative behavior belongs in its owning capability delta. Never duplicate the complete contract into both.
5. Ground every remaining decision branch in canonical OpenSpec, explicit owner corrections, and the relevant temporal record. Keep unresolved branches in the proposal and out of normative deltas until the owner settles them.
6. Synthesize the complete remaining product decisions into one review batch at behavioral granularity. Recommend an answer only when an accepted requirement logically supports it or the owner requests a recommendation; label every unaccepted option explicitly.
7. Do not request approval after each command, field, filename, behavior group, or edge case. After a partial response, persist every settled correction across the proposal and affected deltas, then present the complete remaining unresolved architecture again.
8. Isolate one question only when its answer genuinely changes which major architecture branches exist; after that answer, return to the consolidated review.
9. After the owner answers, update the proposal and every affected capability delta before asking anything else:
   - incorporate settled behavior into its owning delta;
   - remove or narrow the resolved proposal item;
   - add newly exposed unresolved branches explicitly;
   - reconcile every declared capability so no accepted obligation remains only in the overview.
10. Repeat from grounding.

## Convergence

Before convergence, inventory every required feature, fix, constraint, acceptance obligation, and explicitly deferred item across the proposal and every declared capability delta. Do not require implementation details that do not change the accepted product outcome.

When no outcome-changing branch remains across the complete change, present a short restatement. Converge only after the owner confirms it. After convergence, hand the complete proposal to `zpp-shape-feature`; invoke that skill immediately when automatic progression or explicit end-to-end delegation applies.

If this stage was reopened from later work, require that the later stage first preserved any coherent material tracked work through a truthful fallback zmem checkpoint. When no such work exists, require no commit. Invalidate its gate state. Do not resume utility TDD, wiring, or specification formation from prior checkpoints. Send the revised complete proposal through feature shaping again; the revised complete feature contract must receive a replacement feature checkpoint before the workflow can cross that boundary.

Do not create feature files or implementation. Create or update proposal, delta-spec, design, and task artifacts only as the selected OpenSpec schema and owning OpenSpec skills require. Canonical specification promotion remains post-green.
