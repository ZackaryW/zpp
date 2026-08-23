---
name: zpps-update-change
description: Revise exact existing planning artifacts of one resolved OpenSpec change when that mutation is explicitly requested; never discover, scaffold, or implement.
---

# Update existing OpenSpec planning

## Admit planning-artifact revision

Admit this component only when an active playbook configures this exact update or the
caller explicitly requests the immediate mutation of revising existing artifacts of
one OpenSpec change. Required readiness is an identifiable change, an accepted
correction or coherence objective, and resolved evidence needed for the edit. A
request to discover the needed correction, create a missing artifact, implement the
change, or update merely because tasks remain does not admit this component.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-update-change`, the
`observed_immediate_operation`, `missing_readiness`, and the
`separately_eligible_operation`. Stop before the normal procedure and never invoke
the separately eligible component.

Accept playbook configuration or direct partial configuration containing a repository
or store, optional change name, requested planning correction, accepted mutation
authority, and any current guard. Internal coordination identity is runtime-owned.
This operation may revise existing planning files only; it
never creates a missing artifact or edits product code.

## Resolve the store and change

1. Resolve a named or applicable registered store with
   `openspec store list --json` and retain its exact `--store <uuid>` on every
   applicable command. Reject an unavailable or ambiguous store. Otherwise use the
   nearest repo-local root resolved by OpenSpec.
2. Use a supplied change name. Otherwise infer one from accepted context or auto-select
   only when exactly one active change exists. If `openspec list --json` is ambiguous,
   present the three or four most recently modified choices with name, schema, status,
   and `lastModified`, mark the newest as recommended, and ask. Announce the selection
   and how to override it.
3. Run `openspec status --change <name> --json`. Use its `schemaName`, `planningHome`,
   `changeRoot`, `artifactPaths`, `actionContext`, and artifact graph as authority.
   Custom schemas must work unchanged; never branch on familiar artifact names.

The only editable files are the concrete entries in
`artifactPaths.<id>.existingOutputPaths`. Never write to `resolvedOutputPath`, which
may still be a glob, and never invent another file under that glob.

If a required structured interface is unavailable, stop with the command and observed
error. Do not initialize OpenSpec, install or repair skills, invoke generated OpenSpec
skills, or provide compatibility behavior.

## Derive proposed revisions

- For a specific correction, treat it as the starting edit. For a general request to
  update or make the change coherent, perform a coherence review.
- Read every touched artifact, all of its dependency files, and all other existing
  planning artifacts that could contradict or depend on the correction. Re-read them
  from disk even if they appeared earlier in the conversation.
- Reconcile in both directions. A later artifact may reveal that an earlier artifact
  must change; build order is a reading aid, not a restriction on revisions.
- Identify inconsistencies, omissions, duplicated claims, terminology drift, and
  acceptance criteria affected by the request. If the current set is already coherent,
  report a no-op and make no write.
- If coherence requires an artifact or glob member that does not yet exist, defer it
  and identify `zpps-continue-change` as the separately selectable creation operation.
  Do not invoke it.
- If the request replaces the change's intent rather than refining it, stop and
  recommend a separately selected `zpps-new-change` operation with a distinct unused
  identity. Do not convert the existing change silently.

For each affected existing artifact, show the proposed revision and why it is needed.
Obtain explicit owner confirmation for each artifact before writing it. Rejection
leaves that artifact unchanged. When a substantial rewrite is proposed, first run
`openspec instructions <artifact-id> --change <name> --json`, re-read its dependencies,
and apply current `instruction`, `template`, `context`, and `rules`; the latter two are
constraints and must not be copied into the artifact.

## Obtain authority and write confirmed edits

Read-only analysis and proposal of edits does not require coordination. Before the
first confirmed write, accept a current kernel guard or request it for this
already-selected `update-change` operation using the resolved root and change name.
The kernel invokes ZPP runtime coordination and returns structured leased or
explicitly authorized bypass evidence. Do not resolve registration, manifest UUID,
owner, environment overrides, or bundle commands here. Stop on missing product
authority or any runtime-reported coordination conflict. Paths remain post-result
audit evidence.

Apply only confirmed edits to files already listed in `existingOutputPaths`. Verify
each changed file and rerun `openspec status --change <name> --json` after the accepted
set is written. A rejected edit, write failure, missing existing path, or unresolved
contradiction must remain visible in the result; none may be reported as completed.

## Result and stopping boundary

Return roots, store UUID, change/schema identities, guard and lease identity if a
write occurred, proposed revisions with reasons, confirmed changed paths, rejected or
deferred revisions, refreshed status, unresolved contradictions/questions, and
observed command/file evidence. Guidance may name a separately selectable next
operation for missing planning, implementation drift, or eventual archival, but do
not invoke it. Do not create artifacts, implement, select another operation or
playbook step, expand the lease, archive, authorize a checkpoint or commit, or claim
lifecycle completion.
