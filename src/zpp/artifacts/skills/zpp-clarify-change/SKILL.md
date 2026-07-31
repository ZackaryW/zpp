---
name: zpp-clarify-change
description: Clarify a complete ZPP change by persisting owner-grounded product decisions into one gating OpenSpec proposal and reconciling consolidated review batches. Use before feature shaping when requirements, constraints, or deferrals remain unsettled.
---

# Clarify a change

## OpenSpec operation prerequisite

Before running any OpenSpec command or reading, creating, updating, validating, syncing, discarding, or archiving an OpenSpec artifact, locate and read the complete installed `openspec-*` skill that owns that operation. Consult it before acting, never afterward. Use `openspec-propose` for change/proposal creation, `openspec-update-change` for artifact revision, `openspec-sync-specs` for promotion, and `openspec-archive-change` for finalization; consult another installed OpenSpec skill when it more precisely owns the operation. Apply its command, resolved-path, artifact-instruction, validation, and safety contracts without widening this ZPP stage. When an OpenSpec skill bundles later artifacts or operations, explicitly defer those later parts and perform only the operation this ZPP stage owns. Stop and report only when the current operation's contracts conflict.

Maintain zero assumptions. The proposal is the state of record for product intent, requirements, constraints, and deferrals—not workflow-session state.

## Authority boundary

- Treat explicit owner decisions and the live accepted proposal as authoritative.
- Treat rejected designs, superseded documentation, old implementations, test-harness needs, and deferred capabilities as non-authoritative unless the owner adopts them again.
- Govern how decisions are captured; never choose product behavior merely to complete a proposal or make it easier to test.
- Never promote diagnostics, serialization, filenames, adapter internals, framework conventions, or workflow execution preferences into product requirements without an owner-grounded need.
- Keep platform and framework policy in independent traits. Keep mutation authority with the user/session, never with a trait or this skill.

## Loop

1. Select the relevant active change explicitly. If selection is ambiguous, list changes and ask; never guess.
2. Read its current `proposal.md`. If absent, obtain OpenSpec's proposal instructions and immediately write everything already established from the request and repository evidence.
3. Keep an `Unresolved — Do Not Assume` section in the proposal.
4. Ground every remaining decision branch in accepted evidence and recorded decisions. Do not treat explicitly rejected or superseded repository material as evidence.
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

When no outcome-changing branch remains across the complete change, present a short restatement. Converge only after the owner confirms it. Stop with the proposal updated.

If this stage was reopened from later work, require that the later stage first created its truthful fallback zmem checkpoint. Invalidate its gate state. Do not resume utility TDD, wiring, or specification formation from prior checkpoints. Send the revised complete proposal through feature shaping again; the revised complete feature contract must receive a replacement feature checkpoint before the workflow can cross that boundary.

Do not create specs, design, tasks, feature files, or implementation. Specifications are formalized only after behavior is mature and green.

