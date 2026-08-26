## Context

See `proposal.md` for motivation. Workflow instruction ownership is distributed deliberately: `zpp-auto` transfers only supplied authority, complete playbooks own continuation, `zpps-clarify` owns agreement reconciliation, and the kernel guards shared lifecycle authority. Traits remain advisory repository context and cannot control workflow stages.

## Goals / Non-Goals

**Goals:**

- Make clarification actively resolve rather than merely record owner decisions.
- Keep question batches focused and small enough for an owner to answer directly.
- Make automatic progression and decision authority distinct and observable in workflow behavior.
- Consume temporary best-decision authority after one Clarify gate while preserving persistent full authority until revocation.
- Identify repository-context gaps without mutating traits during Clarify.
- Preserve hard manual authorization boundaries for remote and cloud operations.
- Restore the pre-existing repository verification baseline with two bounded maintenance repairs.

**Non-Goals:**

- Add a CLI command, persisted autonomy state, runtime question adapter, hook, BDD scenario, utility, or new behavior/wording test.
- Ask the owner about matters current repository evidence already settles.
- Treat ordinary automatic progression as authority to decide an unresolved Clarify question.
- Author or mutate a repository trait from Clarify.
- Permit automatic or full-authority phrases to authorize Git push, GitHub merge actions, or cloud-environment operations.

## Decisions

### Evidence precedes questions

The workflow first reconciles current specifications, accepted input, proposal and deltas, checkpoints, repository evidence, and relevant repository context. It asks only for remaining outcome-changing owner decisions.

### Three explicit authority levels

`Proceed automatically` authorizes the active playbook to continue end to end and covers ordinary in-scope component confirmations after exact proposed effects are shown. It does not answer an unresolved Clarify decision.

`Proceed automatically` together with an unambiguous request to make best decisions delegates the current or next Clarify gate to the agent. That decision authority is consumed when the gate completes; a later return to Clarify pauses for the owner again.

An unambiguous full-authority statement delegates Clarify decisions and end-to-end continuation across later Clarify re-entry until the owner revokes it. Revocation applies prospectively and does not undo completed work.

### Clarification re-entry is a real workflow gate

New evidence, a contradiction, or an outcome-changing decision discovered after an earlier Clarify result invalidates downstream results derived from the older revision. The playbook re-enters Clarify rather than treating earlier automatic authority as a permanent answer. Temporary best-decision authority has already expired; persistent full authority remains usable until revoked.

### Protected operations never inherit workflow authority

Git push, every GitHub merge action, and any access to or mutation of a cloud environment require separate step-by-step owner authorization. Automatic progression, best-decision authority, full authority, checkpoints, and mutation authority do not imply that authorization.

### Repository-context gap assessment remains read-only

Clarify reports one of `not-applicable`, `covered`, or `trait-authoring-required` after inspecting relevant effective repository context. A gap can become an owner question or accepted follow-up, but `zpp-author-trait` remains a separate explicit mutation and traits cannot grant workflow authority.

### Mechanism-independent questions

The workflow uses the active agent's structured user-question mechanism when available and asks the same focused question directly when unavailable. One through three questions form a bounded batch; an unresolved record never substitutes for interaction.

### Verification baseline repairs do not expand behavior

Repository verification discovered two failures already present at the starting `HEAD`: `zpp.__version__` lagged the declared project version, and an existing test pinned wording removed by the latest vendored zmem skill sync. Align the version constant and revise that existing assertion to the current semantic boundary. Neither repair adds a capability delta, new test surface, or wording-only acceptance authority.

## Risks / Trade-offs

- **Authority wording is ambiguous** → Require unambiguous semantic intent and preserve the least permissive applicable level.
- **Temporary authority leaks into later re-entry** → Consume it when the current Clarify gate completes and assess every later gate independently.
- **Automatic mode hides consequential writes** → Require exact proposed effects to be shown before ordinary component confirmations are considered covered.
- **Remote actions inherit broad wording** → Keep push, GitHub merge, and cloud operations outside every broad workflow authority phrase.
- **Trait assessment becomes implicit mutation** → Keep assessment read-only and require a separate explicit authoring operation.
- **Baseline repair grows into adjacent redesign** → Limit edits to the mismatched version constant and the single stale assertion, then rerun the complete repository gates.

## Open Questions

- Persisted workflow command controls for automatic mode, status, and revocation are intentionally deferred to a separate future change.
