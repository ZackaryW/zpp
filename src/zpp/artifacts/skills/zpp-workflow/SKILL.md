---
name: zpp-workflow
description: Run the complete ZPP product-change workflow through explicit stages, resolving repository traits as contextual policy while preserving OpenSpec, OpenLease, Agent Router, verification, and commit authority boundaries.
---

# ZPP workflow

Run one product change from clarification through finalization. This skill is the
only ZPP workflow authority. Traits advise the selected stage; they never invoke
a stage, authorize a mutation, satisfy a gate, or establish completion.

## Establish the invocation

1. Identify the exact repository target and the user's requested product outcome.
2. Require an explicit current stage. If no stage was supplied, ask for it; do not
   infer it from files, stored context, prior messages, or resolved traits.
3. Run `zpp resolve TARGET --stage STAGE` and preserve the returned `ZPP_CONTEXT`
   for the same target. Apply every retained body in returned order as contextual
   policy for this invocation.
4. Treat canonical OpenSpec specifications as current product authority, the
   active proposal and capability delta specifications as mutable authority for
   the change, and zmem as temporal evidence that must be checked against current
   authority.

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

At every stage, preserve current specifications, accepted intent, and repository
evidence. Expose any outcome-changing unresolved product policy or ownership
boundary to its owner instead of inventing an answer.

## Automatic progression

Under explicit end-to-end delegation, continue through a satisfied checkpoint to
the next stage without asking for ordinary approval. Invoke the next stage as a
new explicit action and pass that exact stage to trait resolution. Pause only for
unresolved clarification, a new or changed product boundary, a missing or changed
utility shape, missing authority, a failed gate, or a component-owned conflict
that requires the owner.

Automatic progression does not itself run verification, choose callbacks,
reconcile retained work, stage files, commit, merge, rebase, or grant authority.
Those actions remain subject to their owning stage and component contracts.

Ignore retained ZPP 1.x stage skills. Do not invoke, translate, or treat them as
migration sources.
