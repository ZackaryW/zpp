---
name: zpps-archive-change
description: Archive one resolved OpenSpec change only with explicit archive intent or exact playbook configuration and ready completion evidence; never infer authority from completion.
---

# Archive one OpenSpec change

## Admit single-change archival

Admit this component only when an active playbook configures this exact archive or
the caller explicitly requests the immediate mutation of archiving one identified
OpenSpec change. Required readiness is the exact change, available completion and
verification evidence, resolved specification-sync choice, and explicit archive
intent; completed tasks, eventual cleanup, or a pending archive does not independently
admit it. Missing factual evidence requires a separately admitted read-only operation.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-archive-change`, the
`observed_immediate_operation`, `missing_readiness`, and the
`separately_eligible_operation`. Stop before the normal procedure and never invoke
the separately eligible component.

Archive one selected change as a bounded playbook component or direct operation. This
skill preserves the complete archive decision and safety procedure; it does not
complete the Bundler bundle or the enclosing ZPP lifecycle.

## Resolve target and authority

Accept an exact change when supplied. Otherwise infer it only from unambiguous context
or the sole active change. If ambiguous, run `openspec list --json`, show only active
changes with schema names, and ask the owner to choose. Announce the selected change.

When a registered store is named or the work resolves inside one, run
`openspec store list --json`, resolve its UUID, and keep `--store <uuid>` sticky on
every store-aware command. Otherwise use the nearest repository-local `openspec/`
root for read-only discovery and as a valid `repo:` trace locator. Preserve the full
capability path relative to `specs/`.

After successful component admission, read-only inspection may occur before obtaining
the mutation guard. Before any canonical-spec write or change move, require an
eligible `zpps-workflow-kernel` assessment carrying explicit archive authority. Pass
the resolved root and change name; the kernel invokes ZPP runtime
coordination and returns structured leased or explicitly authorized bypass evidence.
Do not resolve registration, manifest UUID, owner, environment overrides, or bundle
commands here. Canonical and archive paths are post-result audit evidence. A direct
request may obtain this bounded guard. Block before mutation on missing archive
authority or any runtime-reported coordination conflict.

Verify at invocation time that the installed CLI supports public list, structured
status, archive/spec instructions where available, and spec validation. Never run
`openspec init`, load or repair generated `openspec-*` skills, or invoke a ZPP
lifecycle command.

## Procedure

1. After resolving the change/root, run
   `openspec instructions archive --change "<name>" --json`. This advisory lookup is
   optional and never blocks archive when it exits non-zero or returns invalid JSON;
   continue with no `context` or `operationGuidance` and do not report it as an error.
   On a valid response, treat `context` as required prompt input and every
   `operationGuidance` entry as advisory additive guidance. Explicit owner choices,
   resolved paths, CLI state, commands, and this procedure control on conflict. Report
   ignored/inapplicable guidance; never infer skipped prompts or replacement paths,
   and never copy either field verbatim into specs, artifacts, or summaries.

2. Run `openspec status --change "<name>" --json`. Preserve `schemaName`,
   `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, and every artifact
   state. If any artifact is neither `done` nor `skipped`, list it and obtain explicit
   confirmation before proceeding. A declared `skipped` artifact is satisfied.

3. Read only concrete paths under `artifactPaths.tasks.existingOutputPaths`. Count
   `- [ ]` and `- [x]`. If incomplete tasks exist, show the count and obtain explicit
   confirmation before proceeding. With no concrete task artifact, continue without a
   task warning. Cancellation at either confirmation returns `cancelled` without
   mutation. Confirmed incompleteness remains a warning; never relabel it complete.

4. Use only `artifactPaths.specs.existingOutputPaths` as the delta-spec set. If absent
   or empty, do not infer deltas or fetch spec instructions. Otherwise read each delta
   and corresponding canonical spec under
   `<planningHome.root>/openspec/specs/<capability-path>/spec.md`, determine pending
   ADDED/MODIFIED/REMOVED/RENAMED effects, and show one combined sync assessment.

   Ask exactly one sync-choice question:

   - pending differences: `Sync now (recommended)` or `Archive without syncing`;
   - already synchronized: `Archive now`, `Sync anyway`, or `Cancel`.

   Route by selected intent. Anything unrecognized requires asking again. `Cancel`
   returns without mutation. An explicit skip is preserved as `sync skipped`.

5. When sync is selected, first run
   `openspec instructions specs --change "<name>" --json` exactly once with the same
   store flag. A non-zero exit or invalid artifact-instruction JSON blocks before any
   canonical write or move. A valid response without `rules` is the no-rules case.
   Rules constrain only canonical specs and never archive behavior or paths.

   Invoke `zpps-sync-specs` synchronously for this exact change and full concrete delta
   set, passing the already fetched rules snapshot so it does not fetch it again. Wait
   for completion; never run it in the background. The sub-operation uses the same
   kernel assessment/lease scope and may not widen them.

   After it returns, independently compare every original delta—not only reported
   changed paths—with its canonical spec. Require ADDED requirements present,
   MODIFIED descriptions/scenarios applied with unaffected scenarios intact, REMOVED
   requirements gone (including verified capability retirement), and RENAMED targets
   present with sources absent. Also require all executable BDD obligations to retain
   their exact trace-only OpenSpec anchors without duplicated concrete acceptance
   behavior. If sync failed or any comparison/binding does not match, return `failed`
   without moving `changeRoot`; it remains available for repair and retry.

6. Ensure only the parent directory `<planningHome.changesDir>/archive` exists. Derive
   `<target-name>` by retaining an existing leading `YYYY-MM-DD-` prefix or prepending
   the current date; never stack dates. Before creating or moving anything at the
   destination, check the exact target
   `<planningHome.changesDir>/archive/<target-name>`. If that target exists, return
   `failed` and suggest a different date or renaming the existing archive. Never
   create the target directory before this collision check. Otherwise move the exact
   `changeRoot`, preserving its `.openspec.yaml`, to that exact target.

## Result and stopping boundary

Return the selected root/store/change, schema, exact archive path and every exact
canonical/archive path changed for kernel post-result audit, whether specs were
absent/synced/skipped, validation and post-sync comparison evidence, confirmed
incomplete-artifact/task warnings, and `completed`, `cancelled`, `blocked`,
`coordination-conflict`, or `failed`. Claim specs were synced only when
synchronous sync and independent comparison both passed.

Do not archive another change, complete or expand the Bundler bundle, select or
advance a stage, authorize or create a checkpoint/commit, invoke onboarding, or claim
lifecycle completion. Return the bounded archive result to the direct caller or
playbook for separate kernel result assessment.
