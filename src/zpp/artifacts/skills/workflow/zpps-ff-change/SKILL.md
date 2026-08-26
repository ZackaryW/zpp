---
name: zpps-ff-change
description: Fast-forward one fully understood new OpenSpec change through all apply-required planning when that exact mutation is explicitly requested; never implement it.
---

# Fast-forward OpenSpec planning

## Admit fast-forward planning

Admit this component only when an active playbook configures this exact fast-forward
or the caller explicitly requests the immediate mutation of scaffolding one new
change and creating its complete apply-required planning set. Required readiness is
complete accepted intent, a target root, and resolved evidence sufficient for every
required artifact. A vague eventual outcome, existing change, or unresolved product,
package, API, repository, or integration fact does not admit fast-forward planning.

Use this component when the intended change is sufficiently understood to create all
planning artifacts required by the schema's apply phase. It accepts playbook-supplied
configuration or direct partial configuration: accepted intent, repository or store,
a proposed kebab-case name, and accepted mutation authority. Internal coordination
identity is runtime-owned. This operation always scaffolds a new
change. Ask for clarification only when missing input would materially change the plan.

## Resolve the target

1. If intent is unclear, ask what the caller wants to build or fix and stop until it
   is understood. Derive a kebab-case name only when one was not supplied. Reject an
   invalid supplied name.
2. Resolve a named or applicable registered store with
   `openspec store list --json` and retain its exact `--store <uuid>` on every
   applicable command. Reject an ambiguous or unavailable store. Without a registered
   store, use the nearest repo-local OpenSpec root resolved by the CLI.
3. If the named change exists, do not scaffold over it. Report the collision and offer
   a separately selected `zpps-continue-change` operation. If an existing change was
   explicitly selected, return that same direction and stop; never fast-forward an
   existing change.

Verify the required structured `new change`, `status`, and `instructions` interfaces
at operation time. Report an unavailable interface and stop.

## Obtain authority and scaffold

Before the first mutation, obtain the kernel's matching pre-action assessment for the
resolved root and proposed change name; stop on missing mutation authority or
`coordination-conflict`.

Run `openspec new change <name>` in the sticky scope. Use the configured default
schema; pass `--schema <name>` only when the caller explicitly selected it. Treat a
collision as a stopped result directing to a separately selected
`zpps-continue-change`, not permission to rename or continue here.

## Compute the required set

Run `openspec status --change <name> --json` and use its `planningHome`, `changeRoot`,
`artifactPaths`, `actionContext`, `applyRequires`, and complete artifact graph as
authority.

Build the required set from every ID in `applyRequires` plus every artifact reachable
transitively through its `requires` edges. Do this even for artifacts whose status is
already `done`: status reflects file existence, so a done artifact may still have a
missing prerequisite. Leave artifacts outside this closure untouched. Track the
closure in dependency order with a todo list.

An artifact already reported `skipped` is satisfied and must not be created. Do not
infer a skip from an artifact's familiar role or filename.

## Create the closure in dependency order

For each missing artifact whose dependencies are satisfied:

1. Run `openspec instructions <artifact-id> --change <name> --json` in the sticky
   scope. Treat `instruction`, `template`, `resolvedOutputPath`, `dependencies`,
   `context`, `rules`, `skipped`, and `warning` as current authority.
2. Re-read every completed non-skipped dependency file from disk. Never use
   conversation memory in place of current files.
3. Skip only when status already says `skipped`, or when this artifact's own
   instruction expressly makes it conditional and the accepted change does not meet
   that condition. Record the deliberate skip, explain it once, and never reconsider
   it. A specification artifact is not optional merely by judgment; only structured
   skip state may suppress it.
4. Treat dependencies as enablers rather than permanent gates. If an artifact remains
   `blocked` solely because of a recorded conditional skip, fetch its instructions
   despite that status and create it when no other dependency is missing.
5. Follow the instruction even for familiar artifact names. A bounded configured
   creator may supply artifact content, but do not forward this operation to a
   generated OpenSpec skill. Otherwise fill the template directly. Apply context and
   rules as constraints and never copy their blocks into the artifact.
6. Write only the reported concrete output. If `resolvedOutputPath` is a glob, select
   a concrete path using the current instruction and change context. Verify the file
   exists, then report brief progress.
7. Re-run structured status, recompute readiness, and continue. Creation can unblock
   later artifacts; a failure or absent output blocks the operation.

Stop when every member of the transitive required set is `done`, CLI-reported
`skipped`, or deliberately conditionally skipped. If the graph is blocked for any
other reason, return the exact missing dependencies. If material artifact content is
unclear, ask the caller and resume only with the accepted answer.

## Result and stopping boundary

Return roots, store UUID, change/schema identities, guard and lease identity, the
required-set graph, every created artifact and concrete changed path, recorded skips
with reasons, final status and implementation-readiness state, command/file evidence,
and unresolved questions. Stop at planning readiness. Do not implement, select another
operation or playbook step, expand the lease, archive, authorize a checkpoint or
commit, or claim lifecycle completion.
