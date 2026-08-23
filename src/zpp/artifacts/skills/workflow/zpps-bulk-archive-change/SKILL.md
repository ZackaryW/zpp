---
name: zpps-bulk-archive-change
description: Archive an owner-selected set of OpenSpec changes with cross-change conflict resolution, atomic rule preflight, synchronous spec merges, and truthful partial results.
---

# Bulk archive OpenSpec changes

Coordinate one selected-root batch. This is a substantive archive operation usable
from a playbook or directly; it never decides what the enclosing workflow does next.

## Root and authority

When a registered store is named or the work resolves inside one, run
`openspec store list --json`, resolve its real UUID, and keep `--store <uuid>` sticky
on every store-aware command. Otherwise use the nearest repository-local `openspec/`
root for read-only discovery and as a valid `repo:` trace locator. Never combine
results from an unscoped repository root with a selected store or invent a store UUID.

Read-only selection and validation may precede admission. Before the first canonical
write or change move, require an eligible `zpps-workflow-kernel` assessment with bulk
archive authority. Pass every resolved root and confirmed change name; the kernel
invokes ZPP runtime coordination and returns structured leased or explicitly
authorized bypass evidence for the complete batch. Do not resolve registration,
manifest UUIDs, owner identity, environment overrides, or bundle commands here.
Canonical and archive paths are post-result audit evidence. A direct request may
obtain this bounded guard. Block the whole batch on missing archive authority or any
runtime-reported coordination conflict; never silently remove a target.

Verify that the installed CLI supports public list, structured status, archive/spec
instructions where available, and spec validation. Never run `openspec init`, load or
repair generated `openspec-*` skills, or invoke a ZPP lifecycle command.

## Select the batch

1. Run `openspec list --json` for the selected root. If there are no active changes,
   return `not-applicable`.

2. Always ask the owner to choose one or more changes, even when a playbook supplied a
   candidate set. Show every active change with schema, offer `All changes`, and allow
   any nonempty selection. Never auto-select. Treat an unrecognized answer as another
   question, not permission to archive.

3. After selection, choose one selected change and run
   `openspec instructions archive --change "<selected>" --json` once for this root.
   This lookup is advisory and optional: non-zero exit or invalid JSON proceeds with
   no context/guidance and is not an error. On success, apply relevant `context` as
   required prompt input and consider every `operationGuidance` entry as advisory.
   Explicit choices, conflict analysis, CLI state, resolved paths, and this procedure
   control on conflict. Report ignored guidance; never infer flags, paths, or skipped
   prompts from it and never copy it verbatim into specs, changes, or summaries.

## Validate every selected change

For each selected change run `openspec status --change "<name>" --json` and retain
`schemaName`, `artifacts`, `planningHome`, `changeRoot`, `artifactPaths`, and
`actionContext`.

- Record every artifact as `done`, `skipped`, or incomplete.
- Read only `artifactPaths.tasks.existingOutputPaths`; count complete/incomplete tasks,
  or record `No tasks`.
- Use only `artifactPaths.specs.existingOutputPaths` for delta specs. Preserve every
  complete capability path and extract exact requirement names. Missing/empty specs
  means no sync and no spec-instruction lookup for that change, including in a
  mixed-schema batch. Never infer delta paths from other files.

## Resolve canonical conflicts

Build a map keyed by the exact `<capability-path>` relative to `specs/`. Two or more
selected changes touching the same complete path conflict; identical basenames under
different parent paths do not.

For every conflict:

1. read each competing delta;
2. search product code and tests for concrete implementation evidence for each
   requirement;
3. decide per delta, not merely per change:
   - only one implemented: include that delta and exclude the other;
   - multiple implemented: include them in chronological order, older first and newer
     taking precedence where their accepted behavior overlaps;
   - none implemented: exclude each from sync and warn;
4. record every inclusion/exclusion keyed by change and capability, merge order, and
   evidence-based rationale.

Do not mistake an OpenSpec checkbox, a trace anchor, or descriptive prose for
implementation evidence. Preserve ZPP's single acceptance authority: executable
public-system behavior stays in capability feature scenarios, while canonical specs
retain identical five-field trace-only anchors without concrete acceptance duplicates.

## Present and confirm once

Show one consolidated table with each change's artifact state, task count, delta count,
conflicts, and `Ready`, `Ready*`, or `Warn` status. Show conflict resolutions and every
incomplete-artifact/task warning.

Ask one batch confirmation with intent-equivalent choices:

- archive every selected change, including warned changes;
- archive only ready/ready-with-resolved-conflict changes and skip incomplete ones;
- cancel.

Cancellation returns `cancelled` and mutates nothing. Archive-all preserves every
warning rather than declaring completeness. Ready-only records omitted changes as
`Skipped`; if a skipped change was a conflict partner, re-derive affected resolutions
using only the confirmed set. Anything else requires asking again.

After confirmation and before the first write or move, establish the exact guard and
lease described above. Then fetch all required specs-rule snapshots atomically: for
every confirmed change with included concrete deltas, run
`openspec instructions specs --change "<name>" --json` exactly once. Obtain every
snapshot before any mutation. One non-zero exit or invalid artifact-instruction JSON
blocks the whole batch without writing or moving anything. A valid response without
`rules` is the no-rules case. Rules constrain only canonical output for that change;
they cannot alter conflict decisions, archive paths, or commands.

## Execute the confirmed batch

Carry two per-delta sets through execution:

- `includedDeltas`: every nonconflicting delta plus implemented conflict deltas;
- `excludedDeltas`: conflict deltas excluded because implementation was absent.

A change may have members in both sets. Never collapse these into a single per-change
sync flag or widen a supplied subset.

Process changes in the resolved dependency/chronological order:

1. If a change has included deltas, invoke `zpps-sync-specs` synchronously with exactly
   those paths, explicitly excluding the other paths, and pass its prefetched rules
   snapshot. Wait for completion; never background the sync or refetch instructions.
   Use the same guard/lease scope and do not widen it. With no included deltas, do not
   invoke sync.

2. Before moving that change, independently compare every included delta with the
   canonical spec at
   `<planningHome.root>/openspec/specs/<capability-path>/spec.md`. Require:

   - ADDED requirements present;
   - MODIFIED descriptions/scenarios applied with unaffected scenarios intact;
   - REMOVED requirements absent, including safe file deletion for a retired
     capability rather than an empty Requirements section;
   - RENAMED target present and source absent;
   - exact trace-only bindings preserved and no duplicated executable acceptance.

   Do not verify excluded deltas. If sync, validation, comparison, or binding audit
   fails, record that change as `Failed`, leave its `changeRoot` intact, and continue
   with other changes only where their already recorded conflict ordering and
   canonical inputs remain valid. Never report an excluded delta as an archive skip;
   report `sync skipped` with its change, capability, and reason.

3. Ensure only the parent directory `<planningHome.changesDir>/archive` exists. Derive
   `<target-name>` by retaining a leading `YYYY-MM-DD-` prefix or prepending today's
   date, never both. Before creating or moving anything at the destination, check the
   exact target `<planningHome.changesDir>/archive/<target-name>`. If it exists, record
   `Failed` for that change and preserve its source. Never create the target directory
   before this collision check. Otherwise move its exact `changeRoot`, including
   `.openspec.yaml`, to that exact target.

4. Record `Success`, `Failed`, or `Skipped` independently for each change, plus every
   included sync and excluded `sync skipped` result. A target collision or later
   per-change failure does not erase truthful earlier outcomes.

## Result and stopping boundary

Return the root/store, selected and confirmed members, schema/status table, conflict
decisions and evidence, included/excluded deltas, every exact per-change canonical and
archive path changed for kernel post-result audit, sync/validation results, warnings,
failures, skipped changes, and one aggregate status: `completed`, `partial`,
`cancelled`, `blocked`, `coordination-conflict`, `failed`, or `not-applicable`.

Do not add an unselected change, complete or expand the Bundler bundle, select or
advance a stage, authorize or create a checkpoint/commit, invoke onboarding, or claim
lifecycle completion. Return this bounded result to the direct caller or playbook for
separate kernel result assessment.
