---
name: zpps-new-change
description: Scaffold one OpenSpec change and report its first artifact instructions without creating a planning artifact.
---

# Scaffold one OpenSpec change

Accept configuration from a playbook or a direct partial invocation: the intended
change, repository or registered store, optional proposed name, optional schema, and
accepted mutation authority. Internal coordination identity is runtime-owned. The
operation ends after the scaffold, status, and first ready artifact instructions.

## Resolve input and scope

1. If intent is unclear, ask what the caller wants to build or fix. Do not scaffold
   until the outcome is understood. Derive a kebab-case name from a description only
   when the caller did not supply one; reject an invalid supplied name and ask for a
   valid one.
2. If a registered store is named or the work lives in one, run
   `openspec store list --json`, resolve exactly one UUID, and retain
   `--store <uuid>` on every applicable command. Reject an unavailable or ambiguous
   store. Otherwise use the nearest repo-local OpenSpec root resolved by the CLI.
3. Use the configured default schema by omitting `--schema` unless the caller names a
   schema. If the caller asks which workflows exist, run `openspec context --json` in
   the selected scope, then run `openspec schemas --json` from its `root.path` and ask
   the caller to choose. With an explicitly selected store, retain its UUID on both
   commands. Only when context reports `no_openspec_root` may schema discovery fall
   back to the current directory; do not use that fallback for an invalid store.
4. Check the active change list. If the name already exists, stop and offer
   `zpps-continue-change`; do not silently invent a unique replacement.

Verify at operation time that the installed `openspec` supports the structured
interfaces this operation needs. On a missing or incompatible interface, report the
command and error and stop. Do not initialize OpenSpec, install or repair skills, use
generated OpenSpec skills, or provide compatibility behavior.

## Obtain mutation authority

Scaffolding is governed mutation. Accept a current kernel guard or request it for this
already selected `new-change` operation using the resolved root and proposed change
name. The kernel invokes ZPP runtime coordination and returns structured leased or
explicitly authorized bypass evidence. Do not resolve registration, manifest UUID,
owner, environment overrides, or bundle commands here. Stop before mutation on
missing product authority or any runtime-reported coordination conflict. Paths remain
post-result evidence and the request does not let the kernel select another operation.

## Scaffold and inspect

1. Run `openspec new change <name>`, adding `--schema <schema>` only for an explicitly
   selected non-default schema and retaining the sticky store UUID.
2. If creation reports a collision or invalid name, make no alternate scaffold and
   return the failure with the appropriate correction or continue recommendation.
3. Run `openspec status --change <name> --json`. Use its `schemaName`, `planningHome`,
   `changeRoot`, `artifactPaths`, `actionContext`, artifact graph, and `nextSteps` as
   authority; never assume a repo-local path, artifact ID, or familiar filename.
4. Select the first artifact reported `ready` and run
   `openspec instructions <artifact-id> --change <name> --json` in the same sticky
   scope. Preserve its template, instruction, resolved output path, context/rules
   presence, dependencies, and warnings for the result. Do not write the artifact.
   If no artifact is ready, report the structured status and blocker instead of
   guessing.

## Result and stopping boundary

Return the resolved root and planning home, store UUID if any, change name and root,
schema and artifact sequence, scaffolded paths, progress, first-ready artifact ID and
instructions/template, kernel guard and lease identity used, observed command
evidence, changed paths for later kernel audit, and unresolved questions. Stop before
creating the first artifact. Do not
select another operation or playbook step, expand the lease, implement, archive,
authorize a checkpoint or commit, or claim lifecycle completion.
