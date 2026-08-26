---
name: zpps-workflow-kernel
description: Guard an exact caller-selected ZPP action and its result; never choose a component, resolve an ambiguous operation, or dispatch workflow work.
---

# Guard one selected workflow action

## Shared component lifecycle

Packaged JSON contracts own component identity, effect, standalone eligibility, and
result vocabulary. Each bounded component owns only its operation-specific admission,
inputs, procedure, evidence, failure conditions, and result fields.

For every selected component, compare the immediate operation with that component's
readiness. On mismatch, stop before its procedure and return `component-mismatch`
with the selected component, observed operation, missing readiness, and separately
eligible operation. A component may accept complete playbook configuration or a
direct invocation; direct use does not require prior playbook delegation.

Read-only work runs without mutation coordination. Before governed mutation, the
selected component supplies its exact action, roots, change targets, accepted
revision, predecessor results, intended effects, and owner authority to this kernel.
The kernel and ZPP runtime own reminder checks, leases, internal coordination values,
changed-path audit, checkpoints, archive recording, and lifecycle completion. A
component returns its bounded status, changed paths, unresolved questions, and
verification evidence, then stops. It never duplicates those lifecycle algorithms,
selects continuation, or treats a reminder as authority.

An OpenSpec component validates only the public structured interfaces its operation
uses and stops when one is unavailable. It never initializes OpenSpec, installs or
repairs generated operation skills, emulates a compatibility interface, or invokes a
ZPP lifecycle command for the owner.

## Admit one selected guard assessment

Admit this component only when an active playbook configures a guard for an exact
action or the caller's immediate operation is pre-action or post-result assessment
of an already selected component. Required readiness includes the selected action,
component, targets, effect class, predecessor evidence, and relevant authority facts.
Requests to choose a component, discover missing facts, perform the selected action,
or continue a workflow do not admit the kernel.

Act as a lifecycle guard, never as a workflow or stage dispatcher. Accept either a
pre-action assessment request or a post-action result assessment. The caller, not
this skill, selects the playbook action and component.

## Pre-action assessment

Require the caller to provide the playbook or direct-invocation identity, outcome,
selected action and component, exact repository roots and change names, accepted-input
revision, whether the action mutates governed state, complete ordered predecessor
outcomes, invalid or stale evidence, accepted effects, stage-owned output, and
owner-granted mutation, checkpoint, archive, abandonment, and bypass authority.
Assess only that selected action.

Before assessing it, run `zpp workflow run check` for the exact root, change, and
selected component. Include `--workflow` when the caller identifies a complete
playbook. A complete playbook without matching active registration returns
`workflow-start-required`; stop that assessment until the playbook starts its
reminder. A direct standalone component with no active reminder remains eligible as
`untracked`. For an active reminder, carry the complete structured check into the
assessment. A sequence mismatch remains allowed in reminder mode, but prominently
report its expected stage, expected component, unfinished stages, and warning.

For a workflow stage, require every declared predecessor to have a distinct actual
result for the same accepted-input revision. Block on the earliest missing, stale,
failed, contradicted, or superseded result. In particular, `plan-utilities` and
`mature-utilities` are separate actions: a planning result or skip never supplies a
maturation result, and wiring is ineligible until both have been independently
assessed. Report the invalid predecessor without selecting or invoking its component.

Treat explicit owner-authorized end-to-end playbook delegation as checkpoint commit
authority only for new stage-owned commits produced by that playbook. A standalone
component or stage requires separately granted checkpoint authority. Neither form
authorizes amend, merge, rebase, push, conflict resolution, or unrelated paths.
Git push, every GitHub merge action, and any access to or mutation of a cloud
environment always require separate step-by-step owner authorization for that exact
operation. Automatic progression, best-decision delegation, full authority,
mutation authority, checkpoint authority, and bypass authority never supply it.

Return one of `eligible`, `blocked`, `completed`, or `accepted-not-applicable`, plus
the assessed action identity, reasons, required evidence, authority facts, and any
runtime coordination conflict. The result has no next-step, next-stage, or
component-selection field.

For a governed mutation with accepted mutation authority, invoke `zpp lease acquire`
with one matching `--root` and `--change` pair per exact target. ZPP's Python runtime
owns OpenSpec registration, Bundler manifest preparation, product-home owner
identity, `ZPP_WORKFLOW_COORDINATION` parsing, topology resolution, and atomic bundle
acquisition. Do not duplicate those algorithms, inspect the environment variable, or
ask the owner for any internal coordination value.

Accept `coordination: leased` only when the structured result contains the exact
targets, resolved store UUID members, and bundle identity. Accept
`coordination: bypassed` only when the assessment input carries explicit owner bypass
authority for this action; bypass grants no other authority. Return `blocked` with
the runtime diagnostic on invalid override, registration, manifest, topology,
ownership, or lease conflict. Never add a target, replace a bundle, fall back to
unleased mutation, or treat traits, artifacts, skill identity, component output, or
end-to-end mode as mutation authority. A direct component caller may request this
assessment; prior playbook delegation is not required.

## Result assessment

Require the original assessed action, its guard when mutation occurred, the component
status, changed paths, unresolved questions, and verification evidence. Return
`accepted`, `blocked`, `checkpointed`, or `lifecycle-complete`, with reasons and
observed authority facts. Again return no next-step field.

When the result matches the reminder's first pending component and the component
result is an accepted completion or not-applicable result in its packaged contract,
run `zpp workflow run record` for the exact root, change, component, and result. Pass
an observed bundle only when one already exists. Never record blocked, failed,
unrelated, exploratory, or mismatched results. Recording is reminder progress only;
it supplies no authority and selects no continuation.

For leased execution, submit the component's complete changed-path inventory to ZPP's
runtime audit operation. Accept held OpenSpec paths as audited and repository-local
non-OpenSpec paths as explicitly ignored; block on unknown-root or unheld-OpenSpec
violations. Record member archives only from observed archive results, and complete
the bundle only after every declared member is archived and every required gate and
path audit succeeds. For explicitly bypassed execution, retain structured bypass
evidence and do not claim an audit or bundle transition occurred.

For an observed `memory-folded` result, require the exact inspected zmem-bearing SHA,
owner authority, removed active path, temporary recovery disposition, and proof that
no archive path exists. Audit those paths through the retained bundle, then invoke
`zpp lease abandon --bundle <bundle-uuid>` for that exact bundle under its durable
owner identity. Accept only the structured successful abandonment result. Record no
member archive and do not call bundle completion. A later completed finalization may
yield `lifecycle-complete` only from that inspected fold and abandonment evidence;
missing, mismatched, or failed evidence blocks without reacquiring or fabricating a
bundle.

At every material accepted result with a non-empty coherent stage-owned diff, require
checkpoint authority and invoke the exact installed `zmem-author-commits` skill before
returning stage completion. Supply the accepted contract revision, exact paths or
hunks, passing stage verification, and authority. Resolve every active OpenSpec
`changeRoot` from current structured status before staging. Require dependency-ordered
commits that stage explicit coherent source, test, and non-change artifacts while
excluding every path under each active `changeRoot`; task updates remain in the
working tree. Audit `git diff --cached --name-only` before message validation and
block if an active-change path is present. An OpenSpec change becomes checkpoint
eligible only at its observed archive path after archival. Require zmem validation of
each complete message, preservation of unrelated work, and `zmem show` inspection of
every resulting SHA. Return `checkpointed` only after all required checkpoint evidence succeeds. Without authority, return `blocked` with
`checkpoint-authority-required`; do not call the gate accepted or defer its diff to
finalization. A skipped action or empty diff returns `accepted` without an empty
commit.

Delegate annotation choice to `zmem-author-commits`. A durable accepted architecture,
policy, constraint, or tradeoff and its rationale merits a selective `DECISION`; a
verified reusable lesson merits `LESSON_LEARNT`. Routine implementation, sync, and
archive narration needs no annotation, and later checkpoints must not duplicate
memory already retained by an earlier commit.

Owner-authorized end-to-end execution is interpreted only by the active playbook,
which may follow its own declared branch after this assessment. Never invoke a
`zpps-*` component, implement a phase or OpenSpec operation, infer a stage from
repository state, return a continuation, answer an owner decision, supply missing
mutation/checkpoint/archive authority, skip a component boundary, or declare success
from an unverified component claim.
