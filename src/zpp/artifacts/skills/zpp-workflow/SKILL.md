---
name: zpp-workflow
description: Run the complete ZPP product-change workflow through explicit stages while preserving OpenSpec, OpenLease, Agent Router, verification, and commit authority boundaries.
---

# ZPP workflow

Run one product change from clarification through finalization. This skill is the
only ZPP workflow authority. Traits advise the selected stage; they never invoke
a stage, authorize a mutation, satisfy a gate, or establish completion.

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

## Verify repository behavior

When an accepted shaped BDD obligation requires integration verification, apply
the complete injected `bdd-execution` body as advisory selection policy and use
only a command declared by the repository's root `zpp.behave.yaml`:

- `manual`: pause for an explicit command and selection choice.
- `disabled`: omit `zpp behave` only when independently observed alternate
  relevant verification exists and no shaped BDD obligation remains unsatisfied.
- `complete`: invoke `zpp behave COMMAND --all`.
- `targeted`, including the default: when the chosen command declares the
  `zpp-workflow` gate, invoke `zpp behave COMMAND --gate zpp-workflow`; otherwise
  invoke `zpp behave COMMAND` for deterministic affected selection.

The trait never supplies the command, targets, gate binding, process arguments,
callback selection, stage skip, or completion result. A failed or insufficient
behavior command leaves verification unsatisfied. Do not alias or migrate a
former `zpp-flow-*` gate identity.

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
