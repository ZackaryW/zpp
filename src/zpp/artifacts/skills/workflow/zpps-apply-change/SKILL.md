---
name: zpps-apply-change
description: Implement exact tasks of one existing OpenSpec change only after prerequisites and external evidence are resolved and implementation is explicitly requested; exclude discovery.
---

# Apply one OpenSpec change

## Admit resolved implementation

Admit this component only when an active playbook configures this exact apply action
or the caller explicitly requests the immediate mutation of product or test code for
one existing OpenSpec change. Required readiness is an identifiable change, resolved
task prerequisites, and resolved package, version, API, remote, repository, and
integration evidence needed for the implementation. An active change, pending tasks,
an imperative verb, or eventual adoption intent does not independently admit apply.
When any prerequisite fact still needs discovery, the separately eligible operation
is `zpps-explore`, not apply.

Implement the selected change until its tasks are complete or a real blocker requires
owner input. This is a substantive operation, not a workflow router: it never chooses
an enclosing ZPP stage or what follows this operation.

## Invocation and authority

Accept an exact change from the active playbook or a direct user request. If no change
was supplied, infer it only from unambiguous conversation context or the sole active
change. Otherwise run `openspec list --json`, show the available changes, and ask the
owner to choose. Announce the selected change and how to select another one.

If a registered store was named or the work resolves inside one, run
`openspec store list --json`, resolve its real UUID, and keep `--store <uuid>` sticky
on every store-aware command. Otherwise use the nearest repository-local `openspec/`
root for read-only discovery and as a valid `repo:` trace locator. Never substitute a
store name, directory basename, or invented UUID.

Read-only selection and status discovery may precede the guard. Before the first edit,
obtain the kernel's eligible pre-action assessment for this exact apply action, root,
and change; stop on missing mutation authority or `coordination-conflict`.

At invocation time verify that the installed `openspec` executable supports the
public list, structured status, and structured `instructions apply` interfaces used
below.

## Procedure

1. Run `openspec status --change "<name>" --json` with the selected-store flag when
   applicable. Preserve `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`,
   and `actionContext`; discover the task artifact from the returned graph rather
   than assuming `tasks.md`.

2. Run `openspec instructions apply --change "<name>" --json`. Preserve its
   `contextFiles`, progress, task list and statuses, built-in `instruction`, optional
   `context`, and optional `operationGuidance`.

   - For `state: blocked`, report the missing artifacts and return `blocked`. Do not
     create them or select a planning operation.
   - For `state: all_done`, return `already-completed` with the observed status
     without changing files or selecting archive.
   - Otherwise continue with the implementation contract returned by the CLI.

   Treat `context` as required prompt-level project input and apply relevant facts,
   conventions, and constraints. Treat every `operationGuidance` entry as advisory
   additive guidance. Neither field is completion evidence or permission to bypass a
   blocked state. CLI state, the built-in instruction, explicit owner choices, exact
   paths, the accepted change contract, and ZPP authority boundaries control on
   conflict. Report rejected or inapplicable guidance. Never copy either field
   verbatim into product or planning files unless separately requested.

3. Read every concrete path under every `contextFiles` entry. The schema may expose
   proposal, design, specs, tasks, tests, implementation notes, or other artifacts;
   do not assume artifact IDs, roles, filenames, or locations from a familiar schema.
   Reconcile the task text with its complete accepted context before editing.

4. Show the schema, `N/M` progress, remaining-task overview, and dynamic instruction.
   Then process pending tasks in their declared order until all are complete or the
   operation blocks:

   - announce the exact task;
   - implement the smallest coherent change that fully satisfies its specified
     behavior;
   - run focused verification proportional to that task;
   - mark its concrete task checkbox `- [ ]` to `- [x]` immediately after, and only
     after, the behavior is fully implemented and the focused evidence passes;
   - continue to the next pending task.

   Preserve ZPP's single acceptance authority. A public-system BDD scenario and its
   five-field `# zpp-spec:` trace belong only in the capability-owned feature root;
   OpenSpec retains the normative requirement and no corresponding OpenSpec scenario. Do not
   recreate concrete, trace-only, or target-form acceptance scenarios in OpenSpec,
   remove or guess a feature-side binding, or claim a spec-only obligation from a
   feature. Pure-function case matrices belong in unit tests, with public BDD retained
   only where it observes the public system.

5. Pause and return `blocked` when a task is ambiguous, implementation exposes a
   design contradiction, required work exceeds the accepted artifacts, a proposed
   shortcut would narrow or defer specified behavior, verification fails, or another
   error needs owner judgment. State the exact task, completed work, evidence, added
   scope, and concrete choices. Never guess, silently accept an exception, or mark a
   partial/deferred task complete.

6. On completion or pause, re-read apply instructions/status as needed and report:
   selected root/store/change, schema, tasks completed in this invocation, overall
   progress, every exact changed product/test/task path for kernel post-result audit,
   commands and results, unresolved issues, and one of `completed`, `blocked`,
   `coordination-conflict`, `failed`, or `already-completed`.

## Stopping boundary

Stop when all declared tasks are complete, the operation blocks, or the owner
interrupts. Return the bounded result to the direct caller or active playbook. Do not
create or revise planning artifacts to repair a contradiction, choose another
component, advance or complete a stage, widen or complete the lease bundle, authorize
or create a checkpoint/commit, archive the change, invoke onboarding, or claim
lifecycle completion.
