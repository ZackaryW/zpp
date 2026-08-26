---
name: zpps-propose-change
description: Reconcile and create the complete planning set for one resolved proposed change when that exact planning mutation is requested; never implement the product.
---

# Propose an OpenSpec change

## Admit complete proposal planning

Admit this component only when an active playbook configures this exact proposal or
the caller explicitly requests the immediate planning mutation of reconciling,
scaffolding, and completing one proposed OpenSpec change. Required readiness is
accepted product intent, owner decisions, target scope, and evidence sufficient to
form a coherent planning set. Eventual build/fix intent, an imperative verb, or facts
still requiring exploration do not admit proposal planning.

Accept playbook configuration or a direct partial request containing the intended
change, repository or store, optional name and schema, accepted owner decisions, and
mutation authority. Internal coordination identity is runtime-owned. This operation authorizes planning only. Even when the selecting request
says to build or fix the product, do not edit product code or begin apply work. A
standalone invocation stops after presenting this result and requires a later owner
request for apply. When an owner-authorized end-to-end `zpp-*` playbook selected this
component, return the bounded result; that playbook may follow its already-declared
next component under its existing authority. This adapter never performs or selects
that continuation.

## Reconcile input and scope

1. If intent is unclear, ask what the caller wants to build or fix. Derive a
   kebab-case name only when one was not supplied; reject an invalid supplied name.
2. Ask before scaffolding when ambiguity would materially affect scope, externally
   observable behavior, compatibility, or acceptance criteria. Make reasonable minor
   assumptions and record them in the appropriate planning artifact.
3. Resolve a named or applicable registered store with
   `openspec store list --json`; retain the exact `--store <uuid>` on every applicable
   command. Reject an ambiguous or unavailable store. Otherwise use the nearest
   repo-local root resolved by OpenSpec.
4. Preserve the configured default schema by omitting `--schema` unless the caller
   explicitly names one. If asked which workflows exist, run
   `openspec context --json` in the selected scope and then
   `openspec schemas --json` from the returned `root.path`; retain an explicitly
   selected store UUID on both. Fall back to the current directory only when context
   reports `no_openspec_root`, never for an invalid store, and ask the caller to choose.
5. If the selected name already exists, ask whether to use an explicitly selected
   existing-change operation or choose a distinct unused name. Do not overwrite or
   silently rename the change.

Verify the required structured interfaces at operation time. On an unavailable or
invalid interface, return the command and error and stop.

## Obtain authority and scaffold

Before mutation, obtain the kernel's matching pre-action assessment for the resolved
root and proposed change name; stop on missing mutation authority or
`coordination-conflict`.

Run `openspec new change <name>` in the sticky scope, passing
`--schema <schema-name>` only for an explicitly selected schema. The CLI scaffold and
its `.openspec.yaml` are required; never create a change directory manually.

## Compute planning closure

Run `openspec status --change <name> --json`. Use `schemaName`, `planningHome`,
`changeRoot`, `artifactPaths`, `actionContext`, `applyRequires`, and the full artifact
graph rather than assuming proposal, specification, design, task, or filename
identities.

The planning set is every `applyRequires` ID plus its complete transitive closure
through `requires` edges. Follow edges even when an artifact is reported `done`,
because status is based on file existence and does not prove that its dependencies
exist. Leave artifacts outside this closure untouched and track the closure in
dependency order.

## Create the coherent planning set

For each missing member whose dependencies are ready:

1. Run `openspec instructions <artifact-id> --change <name> --json`. Treat its
   `instruction`, `template`, `resolvedOutputPath`, `dependencies`, `context`, `rules`,
   `skipped`, and `warning` as authoritative.
2. Re-read every completed non-skipped dependency file from disk. Preserve an existing
   capability's full path relative to the resolved specs root and follow established
   organization for a new capability; do not hard-code a flat path.
3. An artifact already reported `skipped` is satisfied and must have no file. A
   further skip is allowed only when that artifact's own instruction expressly makes
   it conditional and the accepted change does not satisfy the condition. Record and
   explain the deliberate skip once. Never suppress specifications by judgment.
4. If a required artifact is blocked solely by a recorded conditional skip, treat the
   dependency as an enabler: obtain its instructions and create it when no other
   dependency is missing.
5. Follow the schema instruction even for familiar artifact names. A bounded
   configured creator may supply content, but do not forward the operation to a
   generated OpenSpec skill. Otherwise fill the template directly. Apply context and
   rules as constraints without copying them into output.
6. Write to the reported concrete path; resolve a glob only with the instruction and
   accepted change context. Verify that output exists, report brief progress, rerun
   structured status, and recompute readiness before the next artifact.

If content becomes materially ambiguous, pause for the owner decision. A failed write,
missing output, invalid instruction, or dependency deadlock is a blocked result with
the exact observed cause. Stop successfully only when every member is `done`,
CLI-reported `skipped`, or deliberately conditionally skipped.

## Result and stopping boundary

Return resolved roots and store UUID, change/schema identities, accepted decisions and
recorded assumptions, guard and lease identity, required-set graph, every artifact and
concrete changed path, skip reasons, final status and planning-readiness state,
observed evidence, and unresolved questions. Present the artifacts for review and
stop. Do not apply them, select another operation or playbook step, expand the lease,
archive, authorize a checkpoint or commit, or claim lifecycle completion.
