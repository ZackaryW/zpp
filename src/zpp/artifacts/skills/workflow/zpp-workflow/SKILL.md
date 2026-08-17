---
name: zpp-workflow
description: Run the complete ZPP product-change workflow through explicit stages while preserving OpenSpec, OpenLease, Agent Router, verification, and commit authority boundaries.
---

# ZPP workflow

Run one product change from clarification through finalization. This skill is the
only ZPP workflow authority. Traits advise the selected stage; they never invoke
a stage, authorize a mutation, satisfy a gate, or establish completion.

## Route artifact-only maintenance

Before requiring a workflow stage, classify the requested outcome. When the
entire change is limited to ungoverned non-runtime artifacts such as README or
reference docs, repository-local ZPP traits or context, or commit metadata, use
the owning artifact guidance and edit directly. Do not create an OpenSpec
change, Gherkin, a utility plan, TDD, or workflow-stage outcomes. Run only
relevant structural, format, resolution, and diff validation, then create an
authorized commit when requested.

This route never covers a spec-governed artifact. The packaged workflow skill
document, a packaged trait document, and a canonical OpenSpec specification are
spec-governed, because canonical requirements describe their content as
observable behavior. Change them through the product workflow and reconcile
canonical specifications before finalization, even when no executable behavior
changes.

Classify by effect, not filename. Artifact loading, parsing, validation, class
conversion, or any artifact-backed change to executable or public behavior uses
the product workflow. For a mixed change, apply the workflow to its behavioral
portion while keeping supporting ungoverned artifact text out of BDD and TDD
obligations.

## Establish the invocation

1. Identify the exact repository target and the user's requested product outcome.
2. Require an explicit current stage. If no stage was supplied, ask for it; do not
   infer it from files, stored context, prior messages, or resolved traits.
3. Apply complete trait bodies already injected by the agent-native ZPP hook as
   contextual policy. The hook is stage-neutral and its bodies remain advisory.
4. Treat canonical OpenSpec specifications as current product authority, the
   active proposal and capability delta specifications as mutable authority for
   the change, and zmem as temporal evidence that must be checked against current
   authority.

## Reconcile the complete agreement

During `clarify`, and again whenever a newer prompt changes or appears to change
the contract:

1. Classify the new input as an explicit confirmation, correction,
   recommendation, exploration, or deferral.
2. Reconcile it against canonical specifications, every older accepted owner
   statement for the change, the proposal overview, every capability delta, and
   every downstream checkpoint already formed.
3. Preserve older accepted requirements unless the owner explicitly corrects or
   supersedes them. Recency alone is not authority. A recommendation is not confirmation.
4. Record unconfirmed outcome-changing input under `Unresolved — Do Not Assume`.
   Clarification has not converged while that section contains a product decision.
5. If reconciliation exposes a contradiction or an assumed decision, reopen
   clarification and supersede downstream checkpoints derived from it. Replace
   those gates only after the complete contract converges again.

Automatic end-to-end authority permits ordinary progression; it never answers an
unresolved product decision. Do not shape, plan, wire, form specifications, or
finalize from an assistant-inferred choice.

## Run the stages

Each stage is a distinct, visible action. Use the installed skill that owns the
OpenSpec operation. Use OpenLease only through its public coordination and
configuration contracts, and Agent Router only through its public discovery and
projection contracts.

1. `clarify`: settle the complete product boundary, constraints, decisions, and
   deferrals in one coherent proposal and capability-delta contract.
2. `shape`: translate that confirmed contract into the complete capability-owned
   behavior feature and fix set without product wiring or invented policy.
3. `plan-utilities`: inspect the approved feature set and form a disposable,
   complete utility plan with signature-level boundaries. If no utility work is
   required, record that conclusion explicitly.
4. `mature-utilities`: prove required utility behavior fail-first, implement only
   the agreed utility seams, verify them independently, checkpoint material work,
   and remove the disposable utility gate.
5. `wire`: bind each approved behavior through public product boundaries and
   compose the proven utilities into the complete feature set. Keep bindings thin
   and capability-local.
6. `form-specs`: reconcile the mature green behavior and current change contract
   into canonical OpenSpec specifications, then checkpoint them.
7. `finalize`: run the complete verification set, inspect every retained OpenLease
   successor cohort, reconcile or explicitly dispose of it, archive the OpenSpec
   change, and create only an authorized logical commit.

Create or change Gherkin only from accepted externally observable behavior in
active capability delta specs. Never translate proposals, designs, tasks, docs,
artifacts, configuration-only work, or implementation details into scenarios;
when no delta behavior remains, record `shape` as not applicable. Otherwise cover
every delta behavior or mark it non-BDD with a concrete reason.
Reject every untraced scenario or coverage gap.

Bind every scenario to executable verification that exercises the behavior it
names through the public system, selected by that scenario. A step that records
its own phrase, asserts only that it ran, or relies on one capability-wide
assertion block running after every scenario is not a binding and establishes no
coverage. Record an obligation with no executable public-system observation as a
canonical specification requirement or a concrete non-BDD classification instead
of an unbound scenario. Never assert the literal wording of an artifact whose
content a canonical requirement already governs.

Create or change TDD tests only for executable behavior. Artifact loading,
unloading, parsing, validation, and conversion into runtime classes are eligible.
Never add tests merely to pin prose or arbitrary artifact wording; when no
executable utility behavior remains, record `mature-utilities` as not applicable.

In a monorepo, shape and bind Gherkin only at each established public application
or composition owner through its real composed entry point. Reusable implementation
subpackages own focused fail-first unit TDD, not feature-level acceptance
contracts. Public BDD may compose those packages but never replaces their unit
tests. Inspect package topology and dependency direction directly instead of
encoding repository structure as behavior tests; expose unresolved ownership.

## Verify repository behavior

When an accepted shaped BDD obligation requires integration verification, apply
the complete injected `bdd-execution` body as advisory selection policy. Select
an established native BDD command from repository configuration or an explicit
owner choice. The absence of `zpp.behave.yaml` never blocks native BDD:

- `manual`: pause for an explicit command and selection choice.
- `disabled`: omit BDD only when independently observed alternate
  relevant verification exists and no shaped BDD obligation remains unsatisfied.
- `complete`: run the complete established native BDD suite. When the repository
  explicitly selects `zpp behave` coordination, invoke its command with `--all`.
- `targeted`, including the default: run the relevant established native feature
  surface directly. When the repository explicitly selects a declared
  `zpp behave` command, use its `zpp-workflow` gate when present and its
  deterministic affected selection otherwise.

`zpp.behave.yaml` remains complete authority whenever `zpp behave` is selected,
but it is optional coordination rather than a BDD prerequisite. The trait never
supplies the command, targets, gate binding, process arguments, callback
selection, stage skip, or completion result. A failed or insufficient native or
coordinated BDD command leaves verification unsatisfied. Do not alias or migrate
a former `zpp-flow-*` gate identity.

## Declare each stage outcome

`clarify` and `finalize` are mandatory and must finish as `completed`. For each of
the five middle stages, the acting agent must declare exactly one outcome:
`completed` or `skipped: not applicable`.

Accept `skipped: not applicable` only after independently verifying that the stage
owns no required output for the complete accepted change:

- `shape`: no public, integration, or fix behavior requires an executable feature
  contract.
- `plan-utilities`: the accepted feature set requires no new or changed utility
  boundary.
- `mature-utilities`: the settled utility plan contains no behavior to prove or
  implement.
- `wire`: no approved behavior requires a binding or product composition change.
- `form-specs`: no mature behavior or accepted delta requires canonical
  specification reconciliation.

A trait body, context value, repository declaration, failed command, incomplete
implementation, or failed verification cannot establish not-applicability. If the
evidence is insufficient, run the stage normally. Record the verified outcome
before continuing to the next stage as a distinct, visible action.

At every stage, preserve current specifications, accepted intent, and repository
evidence. Expose any outcome-changing unresolved product policy or ownership
boundary to its owner instead of inventing an answer.

## Automatic progression

Under explicit end-to-end delegation, continue through a satisfied checkpoint to
the next stage without asking for ordinary approval. Invoke the next stage as a
new explicit action without delegating stage choice to the trait hook. Pause only
for unresolved clarification, a contradiction with accepted input, a new or
changed product boundary, a missing or changed utility shape, missing authority,
a failed gate, or a component-owned conflict that requires the owner.

Automatic progression does not itself run verification, choose callbacks,
reconcile retained work, stage files, commit, merge, rebase, or grant authority.
Those actions remain subject to their owning stage and component contracts.

Ignore retained ZPP 1.x stage skills. Do not invoke, translate, or treat them as
migration sources.
