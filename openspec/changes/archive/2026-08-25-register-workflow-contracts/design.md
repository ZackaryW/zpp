## Context

See `proposal.md` for motivation. Current complete playbooks repeat their ordered
stage sequence in Markdown, the packaged loader statically checks that prose-derived
sequence, and the runtime persists only durable owner and Bundler lease state. The
kernel therefore depends on the caller to preserve playbook identity and predecessor
facts. The existing `zpp workflow` command group manages installed workflow skills,
and product-home state already provides a ZPP-owned persistence boundary.

## Goals / Non-Goals

**Goals:**

- Make packaged JSON the single mechanical source of workflow stages and common
  component metadata.
- Persist a small exact-target reminder checklist across processes and agent turns.
- Produce strong structured in-sequence and out-of-sequence reminders without making
  the runtime a stage dispatcher.
- Surface compact active-workflow status at prompt submission when a selected agent
  exposes a confirmed context-bearing native event.
- Allow direct user customization of the active checklist without revision history or
  approval machinery.
- Preserve existing direct component use and Bundler authority boundaries.
- Remove repeated mechanical wording from playbooks and components while retaining
  their substantive judgment and procedures.

**Non-Goals:**

- Strictly block out-of-sequence work in reminder mode.
- Bind workflow state to an agent, session, thread, or context window.
- Store stages as Bundler lease members or grant authority through registration.
- Add workflow revision history, action receipts, rewind semantics, or a general DAG
  orchestration engine.
- Encode product-specific branch conditions as a JSON expression language.

## Decisions

### Use strict JSON artifacts for mechanical contracts

Add `src/zpp/artifacts/workflow_contracts/` with separate `workflows/`,
`components/`, and `schemas/` directories. One workflow document owns `version`,
`name`, `mode`, and an ordered array of `{id, component}` stages. One component
document owns `version`, `name`, `kind`, `effect`, `standalone`, and `results`.

The Python artifact loader will decode these documents into immutable typed models,
reject unknown fields and invalid values, and cross-check them against the packaged
skill inventory. The JSON schema files provide editor and external validation, while
the Python decoder remains runtime authority. JSON was selected over additional
Markdown parsing because the values are mechanical, typed, and consumed by both CLI
and tests. Duplicating the ordered list in Markdown was rejected because it would
recreate drift.

### Persist a mutable reminder snapshot, not workflow history

Add a ZPP product-home repository for active workflow reminders. Each record contains
an opaque run ID, workflow name, exact resolved root/change targets, ordered stage
snapshots with `pending`, `completed`, or `skipped` status, and an optional observed
bundle UUID. State updates use the repository's established atomic JSON-write pattern.

User edits mutate the active snapshot directly. They do not create revisions or audit
events. Stable unique stage IDs make insert, delete, modify, and upsert predictable.
This intentionally favors a lightweight durable reminder over lifecycle accounting.

### Extend the existing workflow CLI under a nested run group

Preserve `zpp workflow install`, `update`, and `remove`, and add:

```text
zpp workflow run start <workflow> --root <root> --change <change>
zpp workflow run status [--run <uuid>]
zpp workflow run remind [<root>]
zpp workflow run stop --run <uuid>
zpp workflow run check --run <uuid> --component <component>
zpp workflow run record --run <uuid> --component <component> --result <result>
zpp workflow run stage insert ...
zpp workflow run stage delete ...
zpp workflow run stage modify ...
zpp workflow run stage upsert ...
```

`start` is idempotent for the same contract and targets. `check` is read-only and
always returns `allowed: true` in reminder mode, except that a caller explicitly
identifying a complete playbook without registration receives
`workflow-start-required`. `record` advances only an accepted result matching a
registered stage. User-facing stage edit commands validate the full candidate state
before atomic replacement.

`remind` is the prompt-facing read-only form. It resolves the active reminder for
the exact repository target, emits no prompt content when none is active, and emits
only the workflow identity, next stage/component, and remaining-stage count when one
is active. It never creates or advances reminder state.

### Project a separate conditional prompt reminder hook

Add a packaged native hook identity named `zpp-workflow-reminder`; do not add
workflow behavior to `zpp-traits`. For a selected agent, the hook is eligible only
when Agent Router's adapter confirms a prompt-submission event whose successful
command output becomes model context. The hook invokes the read-only `zpp workflow
run remind` boundary for the current repository.

The hook must remain silent without an active workflow and must not start, stop,
replace, customize, check, record, acquire, or transition anything. Root and grouped
workflow lifecycle commands project, inspect, update, and remove it through Agent
Router as a conditional member of the shared owned inventory. Agents without the
confirmed event receive no speculative native hook; kernel checks remain their
portable reminder path. A separate hook was selected over extending `zpp-traits` so
trait resolution remains independent from product-home workflow state.

### Keep reminder checks separate from leases

Starting or editing a reminder does not acquire a bundle. Existing kernel-controlled
lease acquisition remains immediately before governed mutation. After acquisition,
the kernel may associate the observed bundle UUID with the reminder for status output,
but the workflow repository never invokes lease transitions and the lease repository
never interprets stages.

This separation avoids holding resources during read-only clarification and avoids
expanding the external Bundler model with prompt-coordination metadata.

### Make the kernel surface reminders without selecting continuation

The kernel skill will call the runtime reminder check before assessing a configured
playbook action or a direct component targeting an active reminder. It will include
the structured reminder in its result. An out-of-sequence request remains allowed but
must expose the expected stage, expected component, and unfinished checklist.

After accepting a matching completed or not-applicable component result, the kernel
records it. Blocked, failed, unrelated, or read-only exploratory results do not
advance state. The playbook continues to own every branch and next invocation.

### Reduce skill prose only where runtime contracts replace it

Complete playbooks will retain a short mandatory start instruction, custom outcome
agreement, stage-specific inputs, and branch conditions. Reusable components retain
their readiness rules, substantive ordered procedures, domain-specific failures, and
result meaning. Repeated identity, effect, standalone, result-vocabulary, stage-order,
and generic no-dispatch wording moves to validated JSON and common kernel behavior.

The artifact validator will ensure every complete current playbook and every packaged
component has exactly one matching contract. This prevents prose reduction from
silently dropping mechanical coverage.

## Risks / Trade-offs

- [Agents may ignore reminder warnings] → Return prominent typed warning evidence on
  every mismatched kernel assessment and retain explicit optional strict enforcement
  as a future capability rather than silently introducing it now.
- [JSON and skill identity may drift] → Validate the complete cross-referenced
  inventory during packaging and focused tests.
- [Direct checklist edits may invalidate useful prior context] → Treat the checklist
  as an owner-controlled reminder only; validate structure but intentionally avoid
  claiming lifecycle audit or historical truth.
- [Concurrent processes may overwrite reminder state] → Use atomic replacement and
  reject stale writes using the repository's observed file token without exposing a
  user-facing revision model.
- [The workflow CLI already manages installed assets] → Nest runtime operations under
  `zpp workflow run` and preserve existing command names and behavior.
- [Prompt-submit events differ across agents] → Project the reminder hook only
  from explicit Agent Router adapter capability and retain kernel reminders as the
  fallback; do not infer support from agent name.
- [A hook could accidentally become a dispatcher] → Give it only the silent,
  read-only `remind` command and test that all reminder and lease state is unchanged.
- [Moving too much prose into JSON could weaken component procedures] → Move only
  mechanical metadata; retain component-specific readiness, procedure, and stopping
  boundaries in Markdown.

## Migration Plan

1. Add strict contract models, schemas, packaged resources, and inventory validation
   alongside the existing Markdown-derived checks.
2. Add product-home reminder persistence and focused state-transition tests.
3. Add nested workflow-run CLI commands and behavior bindings for start, resume,
   customization, prompt-ready status, reminders, recording, and stop.
4. Add the conditional `zpp-workflow-reminder` artifact and reconcile it through the
   shared Agent Router-owned lifecycle inventory without changing `zpp-traits`.
5. Update the kernel to consume reminder checks and record accepted matching results.
6. Register every complete playbook and component, then remove superseded repeated
   mechanical wording from skills while retaining custom procedures.
7. Replace Markdown stage-order validation with contract-inventory validation, run
   affected and complete verification, and preserve the old behavior on rollback by
   removing the new contracts/state integration together.
