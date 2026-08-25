---
name: zpps-archive-change
description: Preserve one resolved OpenSpec change by normal archive or an explicitly selected eligible memory fold; never infer terminal authority from completion.
---

# Preserve one completed OpenSpec change

Mechanical identity, effect, standalone eligibility, and result vocabulary come
from this skill's validated packaged JSON contract. Apply the substantive
readiness, procedure, failure, and stopping behavior below.

## Admit single-change preservation

Admit this component only when an active playbook configures this exact terminal
operation or the caller explicitly requests the immediate mutation of preserving one
identified OpenSpec change by normal archive or memory fold. Required readiness is
the exact change, available completion and verification evidence, a resolved
preservation mode, and explicit authority for that mode. Normal archive also requires
a resolved specification-sync choice and archive intent. Memory fold requires an
accepted `zpps-finalize` eligibility result, exact proposed zmem content, checkpoint
authority, and explicit owner authority to remove this active change without creating
an archive. Completion, eventual cleanup, or a pending terminal operation does not
independently admit either mode. Missing factual evidence requires a separately
admitted read-only operation.

Preserve one selected change as a bounded playbook component or direct operation.
This skill owns both terminal filesystem procedures; it does not complete Bundler or
the enclosing ZPP lifecycle.

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
the mutation guard. Before any canonical-spec write, change move, removal, or
memory-fold commit, require an eligible `zpps-workflow-kernel` assessment carrying
explicit authority for the selected preservation mode. Pass
the resolved root and change name; the kernel invokes ZPP runtime
coordination and returns structured leased or explicitly authorized bypass evidence.
Do not resolve registration, manifest UUID, owner, environment overrides, or bundle
commands here. Canonical, temporary, archive, and committed paths are post-result
audit evidence. A direct request may obtain this bounded guard. Block before mutation
on missing mode-specific authority or any runtime-reported coordination conflict.

Verify at invocation time that the installed CLI supports public list, structured
status, archive/spec instructions where available, and spec validation. Never run
`openspec init`, load or repair generated `openspec-*` skills, or invoke a ZPP
lifecycle command.

## Procedure

Select exactly one branch: normal archive or memory fold. Never fall back from a
failed memory fold to archive, or from a failed archive to deletion.

### Shared readiness

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
   confirmation before proceeding with normal archive. In memory-fold mode, return
   `blocked` instead; incompleteness cannot be waived. A declared `skipped` artifact
   is satisfied.

3. Read only concrete paths under `artifactPaths.tasks.existingOutputPaths`. Count
   `- [ ]` and `- [x]`. If incomplete tasks exist, show the count and obtain explicit
   confirmation before proceeding with normal archive. In memory-fold mode, return
   `blocked` instead. With no concrete task artifact, continue without a task warning.
   Cancellation at either normal-archive confirmation returns `cancelled` without
   mutation. Confirmed incompleteness remains a warning; never relabel it complete.

### Normal archive

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
   present with sources absent. Also require every executable BDD obligation to retain
   its exact feature-side binding and no corresponding OpenSpec scenario. If sync
   failed or any comparison/binding does not match, return `failed`
   without moving `changeRoot`; it remains available for repair and retry.

6. Ensure only the parent directory `<planningHome.changesDir>/archive` exists. Derive
   `<target-name>` by retaining an existing leading `YYYY-MM-DD-` prefix or prepending
   the current date; never stack dates. Before creating or moving anything at the
   destination, check the exact target
   `<planningHome.changesDir>/archive/<target-name>`. If that target exists, return
   `failed` and suggest a different date or renaming the existing archive. Never
   create the target directory before this collision check. Otherwise move the exact
   `changeRoot`, preserving its `.openspec.yaml`, to that exact target.

### Memory fold

For the memory-fold branch, require every artifact and task from shared readiness to
be complete; unlike normal archive, no warning confirmation can waive incompleteness.
Reperform the finalization eligibility audit and block if any canonical specification
effect, public contract, nested or branching logic, architecture or ownership
boundary, compatibility promise, security or safety constraint, migration, or other
non-foldable decision remains. Validate the complete proposed commit message through
the exact installed `zmem-author-commits` skill before moving the change.

1. Audit `git diff --cached --name-only` and the proposed explicit source/test paths.
   Block if any path under `changeRoot` is staged or would be committed. Active task
   updates are evidence for the fold, never commit content.
2. Create a unique temporary directory through the platform's safe temporary-file
   facility outside the Git worktree. Resolve both the source and destination paths,
   require the source to equal `changeRoot`, require the destination to remain inside
   that temporary directory, and move the exact change root there without broad
   globs or recursive deletion.
3. Create the validated zmem-bearing checkpoint from only the explicit coherent
   source/test paths. When prior checkpoints already contain all source work, create
   an intentional zmem-only commit rather than reintroducing planning files. If
   validation, staging, or commit creation fails, restore the exact temporary change
   to its original `changeRoot` and return `failed`.
4. Inspect the resulting SHA with `zmem show`. Require every proposed entry to be
   valid and require both the original active `changeRoot` and the normal archive
   target to be absent. On inspection failure, restore the change root when doing so
   does not overwrite another path, report the commit as requiring owner repair, and
   return `failed`; never silently discard the recoverable planning artifacts.
5. Only after successful inspection, remove the temporary copy. Return
   `memory-folded` with the commit SHA, annotation indexes, exact removed active path,
   temporary recovery path disposition, explicit authority, source/test paths, and
   proof that no archive path was created.

## Result and stopping boundary

Return the selected root/store/change, schema, selected preservation mode, and every
exact path changed for kernel post-result audit. Normal archive returns its exact
archive/canonical paths, sync evidence, warnings, and `completed`, `cancelled`,
`blocked`, `coordination-conflict`, or `failed`. Memory fold returns the evidence
specified above and `memory-folded`, `blocked`, `coordination-conflict`, or `failed`.
Claim specs were synced only when synchronous sync and independent comparison both
passed.

Do not preserve another change, complete or expand the Bundler bundle, select or
advance a stage, invoke onboarding, or claim lifecycle completion. Outside the exact
memory-fold branch, never authorize or create a checkpoint/commit. Return the bounded
result to the direct caller or playbook for separate kernel result assessment.
