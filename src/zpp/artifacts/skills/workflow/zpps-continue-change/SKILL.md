---
name: zpps-continue-change
description: Resolve one OpenSpec change, create exactly its next eligible planning artifact, and return updated status.
---

# Continue one OpenSpec change

Accept a repository or store, optional change name, accepted artifact intent, and any
current kernel guard and Bundler lease from a playbook or direct partial caller. Ask
only for missing values required to produce this one bounded artifact.

## Resolve the store and change

1. For a named or applicable registered store, run `openspec store list --json`,
   resolve exactly one UUID, and retain `--store <uuid>` on every applicable command.
   Reject an unknown or ambiguous store. Otherwise use the nearest repo-local root
   resolved by OpenSpec.
2. Use a supplied change name. Otherwise infer it from accepted conversation context,
   or auto-select only when `openspec list --json` reports exactly one active change.
   When ambiguous, present the three or four most recently modified choices with name,
   schema, status, and `lastModified`, mark the most recent as recommended, and ask the
   caller to choose. Announce the selected change and how to override it.
3. Run `openspec status --change <name> --json`. Use `schemaName`, `planningHome`,
   `changeRoot`, `artifactPaths`, `actionContext`, and the returned artifact graph as
   authority. Never infer an ID or path from a familiar schema.

If the structured list, status, or instruction interface is unavailable, stop with
the failed command and observed error. Do not initialize OpenSpec, install or repair
skills, invoke a generated OpenSpec skill, or attempt compatibility behavior.

## Branch on current status

- If `isPlanningComplete` is true, report the final schema and progress and stop
  without mutation. State that planning is ready for a separately selected apply
  operation; do not invoke it.
- If artifacts are ready, choose the first `ready` artifact in the returned graph.
- If every remaining artifact is blocked, return the full blockers and suggest
  checking the schema/change state. Do not create out of order.

Run `openspec instructions <artifact-id> --change <name> --json`. Parse and retain:

- `context` and artifact-specific `rules`, which constrain creation but must never be
  copied into the output;
- the authoritative `template` and `instruction`;
- `resolvedOutputPath` and any path-selection guidance;
- completed `dependencies`; an entry marked `skipped: true` has no file to read;
- `skipped` or `warning`; when the artifact must not be created, select the next
  reported ready artifact or stop with the observed state.

If accepted intent is materially unclear after reading instructions and dependencies,
ask the caller before mutation.

## Obtain authority and create exactly one artifact

Before the write, accept a current kernel guard or request it for this already
selected `continue-change` operation using the resolved root and change name. The
kernel invokes ZPP runtime coordination and returns structured leased or explicitly
authorized bypass evidence. Do not resolve registration, manifest UUID, owner,
environment overrides, or bundle commands here. Stop on missing product authority or
any runtime-reported coordination conflict. Paths remain post-result audit evidence.

Re-read every non-skipped dependency file from disk. Follow the instruction even when
the artifact has a familiar name. If it identifies a bounded configured creator,
apply that creator's returned content within this operation; never forward the whole
operation to a generated OpenSpec skill. Otherwise fill the template directly. Write
only the concrete `resolvedOutputPath`; if it is a glob, choose one concrete path
using the instruction and change context. Apply context and rules as constraints, not
artifact content. Verify the concrete output exists before reporting success.

Run `openspec status --change <name> --json` again and calculate updated progress and
newly ready artifacts. A failed write, absent output, or invalid status is a blocked
result, not completion.

## Result and stopping boundary

Return roots, store UUID, change and schema identity, created artifact ID and concrete
changed path, refreshed status/progress, newly ready artifacts, guard and lease
identity, command and file evidence, and unresolved questions. Stop after exactly one
artifact. Do not select another operation or playbook step, create later artifacts,
expand the lease, implement, archive, authorize a checkpoint or commit, or claim
lifecycle completion.
