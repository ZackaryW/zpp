---
name: zpps-sync-specs
description: Merge a resolved delta-spec selection into canonical specifications only when that exact mutation is explicitly requested; never discover intent or archive the change.
---

# Synchronize one change's specifications

Mechanical identity, effect, standalone eligibility, and result vocabulary come
from this skill's validated packaged JSON contract. Apply the substantive
readiness, procedure, failure, and stopping behavior below.

## Admit canonical specification synchronization

Admit this component only when an active playbook configures this exact sync or the
caller explicitly requests the immediate mutation of merging selected delta specs
from one existing change into canonical specifications. Required readiness is an
identifiable change, a resolved delta/capability selection, accepted semantics, and
resolved binding evidence. Unknown product, repository, or authority facts require
separate exploration or specification formation; a future archive does not itself
admit synchronization.

Read delta specs and edit canonical specs directly. Merge semantically rather than
copying delta documents. Stop after validation; this operation never archives or
continues the enclosing workflow.

## Invocation, target, and authority

Accept an exact change from a playbook, an archive sub-operation, or a direct request.
Otherwise infer it only from unambiguous context or the sole active change containing
delta specs. If ambiguous, run `openspec list --json`, show changes that have delta
specs, and ask the owner to select. Announce the selected change.

When a registered store is named or the work resolves inside one, run
`openspec store list --json`, resolve its UUID, and keep `--store <uuid>` sticky on
every store-aware command. Otherwise use the nearest repository-local `openspec/`
root for read-only discovery and as a valid `repo:` trace locator. A
`<capability-path>` is the complete path relative to `specs/`; preserve nested paths
such as `identity/user-auth` and never collapse them to a basename.

After successful component admission, read-only discovery may occur before obtaining
the mutation guard. Before the first canonical-spec write or capability retirement,
require an eligible `zpps-workflow-kernel` assessment for this exact sync request.
Pass the resolved root and change name; the kernel invokes ZPP
runtime coordination and returns structured leased or explicitly authorized bypass
evidence. Do not resolve registration, manifest UUID, owner, environment overrides,
or bundle commands here. Canonical filesystem paths are post-result audit evidence.
A direct request may obtain this bounded guard. Block before mutation on missing
product authority or any runtime-reported coordination conflict. Verify the installed
CLI supports public list, structured status, structured spec instructions, and spec
validation. Never run `openspec init`, load or repair generated `openspec-*` skills,
or invoke a ZPP lifecycle command.

## Resolve the delta set

1. Run `openspec status --change "<name>" --json`. Use its `planningHome.root` as
   the canonical root; canonical specs are under
   `<planningHome.root>/openspec/specs/`. Never hardcode the caller's repository when
   a selected store owns the planning home.

2. Use only `artifactPaths.specs.existingOutputPaths` as delta-spec authority. If the
   entry is absent or empty, return `not-applicable` without fetching spec
   instructions or writing anything. Never infer delta specs from directories,
   familiar filenames, or other artifacts.

3. By default select every complete path in `existingOutputPaths`. A direct caller or
   archive operation may supply an explicit subset, but every supplied path must
   exactly equal an entry from that list. Preserve the subset throughout the run;
   never widen it, silently drop an invalid member, or sync excluded deltas. An empty
   supplied subset is `not-applicable`.

## Capture rules before mutation

Before the first write, obtain exactly one current specs-instruction snapshot:

- reuse a valid `openspec instructions specs --change "<name>" --json` snapshot
  supplied synchronously by archive; otherwise run that command once with the same
  store flag;
- a non-zero exit or invalid artifact-instruction JSON blocks before any write;
- a valid response with no `rules` is the no-rules case;
- apply rules only to the content and form of canonical specs produced by this merge.

Artifact rules cannot change selected roots, delta paths, commands, authority, or the
operation sequence. Do not copy rule text into a spec or summary.

## Merge every selected capability

Read both the delta and its canonical
`<planningHome.root>/openspec/specs/<capability-path>/spec.md` before editing. Apply:

- **ADDED**: add a missing requirement; when it already exists, reconcile it as an
  implicit modification rather than duplicating it.
- **MODIFIED**: replace the requirement body and named scenarios as described while
  preserving every unaffected scenario and other normative content. A modified block
  carries the whole surviving requirement; never drop an existing scenario merely
  because the delta omitted a change to it.
- **REMOVED**: remove the whole named requirement block.
- **RENAMED**: resolve the exact `FROM` requirement and rename it to exact `TO`, leaving
  no old heading.
- **Purpose**: an existing canonical Purpose is authoritative. For a new capability,
  copy a delta Purpose when present; otherwise write a brief `TBD` placeholder and
  report it.

Canonical documents must have one `## Purpose`, one `## Requirements`, and ordinary
`### Requirement:` blocks. Never leave delta operation headers in canonical specs and
never copy a delta file wholesale.

Preserve ZPP's single acceptance authority during every merge. A public-system
executable example remains only in its capability feature file. Canonical OpenSpec
retains the identical five-field trace-only conformance anchor (`root`, `capability`,
`requirement`, `feature`, `scenario`) and no duplicate concrete behavior steps. Do not
invent or rewrite either side of a binding to make it resolve. Preserve exact
trace-only anchors through modification and rename; block and report any ambiguous,
orphaned, one-way, or duplicate acceptance authority rather than canonizing it.

### Capability retirement

When selected removals leave no requirement blocks, delete the canonical `spec.md`
and then its empty directory only if all of these are true:

1. this run actually removed requirements and left none;
2. the remaining file is well formed and still has `## Purpose`;
3. the spec was not already empty before this run;
4. every nonblank line is accounted for by the title, Purpose, Requirements header,
   canonical requirements, scenarios, or fenced examples;
5. the change's `.openspec.yaml` declares `retire_capabilities: true`;
6. the file resolves within the real specs root and no capability-directory symlink
   redirects deletion outside it.

Any other section or failed condition blocks that capability without modifying its
canonical spec. Never leave an empty `## Requirements`. Name the failed condition and,
when only the marker is missing, state that it can be added. A successful retirement
summary names the deleted spec and Purpose and supplies a pasteable `git checkout`
only when the file belonged to the caller's checkout; otherwise give checkout-scoped
recovery guidance.

## Validate and return

Run `openspec validate --specs` with the same selected-store flag after all selected
merges. Validation failure yields `failed`; report diagnostics and never claim the
sync succeeded. The operation is idempotent: a second run against the same inputs
must make no further semantic change.

Return the root/store/change, exact selected and excluded delta paths, rules snapshot
provenance, every exact changed/created/deleted canonical path for kernel post-result
audit, requirements
added/modified/removed/renamed, binding or retirement blockers, validation command and
result, TBD Purpose warnings, and one status: `completed`, `not-applicable`, `blocked`,
`coordination-conflict`, or `failed`.

Stop without archiving the change. Do not select another operation or stage, widen or
complete the lease bundle, authorize or create a checkpoint/commit, invoke onboarding,
or claim lifecycle completion. When invoked synchronously by archive, return control
only after writes and validation have finished.
