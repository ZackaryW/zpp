---
name: zpp-workflow
description: Run the complete ZPP product-change workflow through explicit stages while preserving OpenSpec, workspace coordination, Agent Router, verification, and commit authority boundaries.
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
3. Before executing the requested stage, read and apply the complete
   [stage assessment contract](references/stage-assessment.md). Present its
   eligibility assessment explicitly. A stage name is dispatch input only; it
   never satisfies that stage, a predecessor gate, verification, or mutation
   authority.
4. Apply complete trait bodies already injected by the agent-native ZPP hook as
   contextual policy. The hook is stage-neutral and its bodies remain advisory.
5. Treat canonical OpenSpec specifications as current product authority, the
   active proposal and capability delta specifications as mutable authority for
   the change, and zmem as temporal evidence that must be checked against current
   authority.

If the assessment finds a missing, stale, failed, or superseded predecessor,
block the requested stage. Identify the earliest unsatisfied predecessor, but do
not execute it without a new explicit invocation unless separate end-to-end
progression authority is already in force. A changed contract reopens
clarification and invalidates every downstream assessment derived from the older
contract revision.

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

Each stage is a distinct, visible action. Follow the exact installed skill that
owns each OpenSpec operation:

- `openspec-explore` for exploration;
- `openspec-propose` for creating a change and its planning artifacts;
- `openspec-update-change` for revising existing planning artifacts;
- `openspec-apply-change` for implementing change tasks;
- `openspec-sync-specs` for synchronizing delta specifications without archival;
- `openspec-archive-change` for archiving a completed change.

These skills are component operation integrations, not ZPP stage authorities or
one-to-one stage aliases. Before performing a cross-repository topology,
workspace lifecycle, lock, successor, reconciliation, handoff, recovery,
abandonment, or cleanup operation, name and follow the installed
`zpp-workspace-management` companion skill. Keep provider-specific operation
guidance out of this general workflow. Use Agent Router only through its public
discovery and projection contracts.

The six OpenSpec operation skills must already be available through the
initialized ZPP agent integration. During a workflow run, never invoke or
authorize `openspec init`, generate or vendor an OpenSpec skill tree, install or
project an OpenSpec operation skill, repair one, or create a substitute operation
owner in the target repository or any other location.

When an operation required by the current stage is absent, unreadable, invalid,
stale, or requires local initialization, leave that stage blocked and identify
the exact operation skill. Direct the owner to root `zpp init` when the agent has
no ZPP integration or root `zpp sync` when an integration already exists. Never
invoke either lifecycle command on the owner's behalf; workflow progression does
not grant user-scope integration mutation authority.

This prohibition covers operation skills, not product planning state. An
installed operation skill may create, update, validate, synchronize, or archive
ordinary repository-local OpenSpec artifacts under `openspec/`. Never treat that
planning directory as a skill installation or use it to justify skill bootstrap.

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
7. `finalize`: run the complete verification set, delegate inspection and
   authorized disposition of every retained cross-repository successor or
   reconciliation item to `zpp-workspace-management`, archive the OpenSpec change,
   verify the retained checkpoint series, and checkpoint only remaining
   finalization-owned work. Finalization remains incomplete for every blocked
   retained item.

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

## Form specifications without duplicated scenarios

During `form-specs`, replace an OpenSpec scenario's repeated executable body with
an exact BDD target only when all of these facts are observed:

- the target is `features/<capability>/<capability>.feature::<scenario name>` and
  belongs to the same capability owner as the requirement;
- that exact feature scenario exists and traces to the requirement;
- its scenario-selected bindings exercise the behavior it names through the
  public system rather than recording phrases, asserting wording, or sharing one
  capability-wide assertion; and
- relevant verification for that exact scenario passes.

Use this retained OpenSpec form:

```markdown
#### Scenario: BDD target — <scenario name>
- **WHEN** executable behavior is covered by `features/<capability>/<capability>.feature::<scenario name>`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
```

Every scenario without qualifying BDD coverage remains a complete OpenSpec
WHEN/THEN scenario. A missing, stale, cross-capability, untraced, recorder-only,
capability-wide, wording-only, or unverified target blocks `form-specs`; it never
justifies removing or redirecting the specification scenario.

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

## Checkpoint every material gate

Before declaring a stage `completed`, decide from the observed stage-owned diff
whether its gate is material. A material gate owns a non-empty coherent diff. A
skipped stage or a completed stage with no owned diff records its outcome without
an empty commit.

For every material gate, invoke the exact installed `zmem-author-commits` skill
and complete its workflow before declaring the stage complete:

1. Record the checkpoint evidence required by the
   [stage assessment contract](references/stage-assessment.md), including the
   accepted contract revision, stage-owned diff, applicable verification and
   observed result, commit authority, and exact paths or hunks proposed for
   staging.
2. Preserve unrelated working-tree changes. Split distinct responsibilities in
   dependency order only when every intermediate commit is independently
   coherent and verifiable; do not create a split known to break the repository.
3. Run stage-appropriate verification before each commit, validate the complete
   proposed message with zmem, and create the commit only under checkpoint commit
   authority.
4. Record every resulting SHA and inspect it with `zmem show`. Let
   `zmem-author-commits` decide whether durable memory warrants an annotation;
   never manufacture an annotation merely to label a checkpoint.

Explicit end-to-end workflow delegation grants checkpoint commit authority for
the new commits produced by its automatically progressed stage series. A
standalone stage action requires separately granted commit authority. Missing
authority or any failed verification, zmem validation, commit, or resulting-
commit inspection leaves a material gate incomplete.

Checkpoint authority never includes amend, merge, rebase, push, callback
selection, conflict reconciliation, inclusion of unrelated work, or any other
component-owned mutation. At `finalize`, verify that every material completed
gate has its checkpoint evidence, archive the OpenSpec change, and commit only
the remaining finalization-owned diff. Do not collapse or replace the preceding
checkpoint series.

## Automatic progression

Under explicit end-to-end delegation, continue through a satisfied checkpoint to
the next stage without asking for ordinary approval. Invoke the next stage as a
new explicit action without delegating stage choice to the trait hook. Pause only
for unresolved clarification, a contradiction with accepted input, a new or
changed product boundary, a missing or changed utility shape, missing authority,
a failed gate, or a component-owned conflict that requires the owner.

Apart from the narrow checkpoint commit authority carried by explicit end-to-end
delegation, automatic progression does not itself run verification, choose
callbacks, reconcile retained work, stage files, commit, merge, rebase, or grant
authority. Those actions remain subject to their owning stage and component
contracts.

Ignore retained ZPP 1.x stage skills. Do not invoke, translate, or treat them as
migration sources.
