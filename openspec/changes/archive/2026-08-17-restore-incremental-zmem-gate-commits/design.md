## Context

The consolidated workflow currently uses “checkpoint” as an outcome label but
does not define a checkpoint as Git history. Its automatic-progression boundary
also withholds staging and commit authority, so an end-to-end run can leave every
stage in one final working-tree diff. ZPP already installs
`zmem-author-commits`, whose contract supplies commit decomposition, explicit
staging, message validation, selective durable-memory annotations, and post-
commit inspection.

This change affects the packaged workflow instructions, their internal stage-
assessment reference, and the canonical specification governing both artifacts.
It changes no runtime or public-system behavior, so it creates no Gherkin, BDD,
utility-plan, unit-TDD, or product-wiring obligation.

## Goals / Non-Goals

**Goals:**

- Make every material stage gate end in an independently coherent, verified
  zmem-aware commit before the gate can complete.
- Define materiality, commit authority, exact staging scope, verification, and
  post-commit evidence so an agent cannot declare the gate from intuition.
- Carry checkpoint commit authority through an explicitly delegated end-to-end
  workflow while preserving all other Git authority boundaries.
- Keep skipped and no-diff gates visible without manufacturing empty commits.
- Make finalization verify the incremental series and commit only work that the
  finalization stage itself still owns.

**Non-Goals:**

- Reimplement commit-message or zmem policy inside `zpp-workflow`.
- Require a zmem annotation when a commit contains no durable repository memory.
- Grant amend, merge, rebase, push, callback, conflict-reconciliation, or
  unrelated-working-tree authority.
- Introduce executable tests for prose-only governed artifacts.

## Decisions

### A material gate is a commit boundary

A stage gate is material when its stage-owned output leaves a non-empty coherent
diff. The gate cannot be recorded as `completed` until every commit needed for
that diff has succeeded. A skipped stage or an eligible stage with no owned diff
records its observed outcome without an empty commit.

This uses the stage boundary because the workflow already assesses and reports
each stage independently. Alternatives considered were one final commit, which
loses stage provenance, and unconditional per-stage commits, which manufacture
empty history for legitimate skips.

### Each material gate has an explicit evidence record

Before completion, the acting agent records the stage, accepted contract
revision, stage-owned diff, applicable verification and its result, checkpoint
commit authority, exact paths or hunks to stage, proposed commit series, zmem
validation result, resulting SHA, and `zmem show` inspection result. Missing
authority, failed verification, message-validation failure, commit failure, or
post-commit inspection failure leaves the stage incomplete.

The record makes the decision reproducible and prevents a requested stage name,
dirty working tree, or confident assertion from substituting for gate evidence.

### `zmem-author-commits` owns checkpoint commit mechanics

For every material gate, `zpp-workflow` invokes the exact installed
`zmem-author-commits` skill. That skill owns repository-convention inspection,
dependency-ordered decomposition, explicit path or hunk staging, commit-message
validation, annotation choice, commit creation when authorized, and resulting-
commit inspection. The workflow owns when that operation is mandatory and
whether the stage gate can complete.

Duplicating those mechanics in the workflow was rejected because it would
create two commit-policy authorities. Hiding them behind an unnamed “checkpoint”
operation was rejected because the installed operation owner would again be
guessable.

### Commit authority is narrow and explicit

Explicit end-to-end workflow delegation grants authority to create the
checkpoint commit series produced by the automatically progressed stages. A
standalone stage invocation requires separate commit authority. If that authority
is absent, the agent may prepare and validate the proposed series but must pause
with the material gate incomplete.

Checkpoint authority covers only new commits for the stage-owned diff. It does
not authorize amend, merge, rebase, push, conflict resolution, callback
selection, or inclusion of unrelated changes. This is narrower than treating
general automatic progression as arbitrary Git authority and still permits the
owner-requested unattended end-to-end workflow.

### Coherence takes precedence over commit count

Distinct responsibilities within one gate are committed in dependency order
when each intermediate state is coherent and passes its applicable verification.
They remain together when splitting would knowingly leave the repository broken.
Unrelated pre-existing changes remain unstaged and uncommitted.

This avoids both monolithic gate commits and mechanically granular commits that
cannot stand alone.

### Finalization audits rather than collapses history

Finalization verifies that every material completed gate has its checkpoint
evidence and that no stage-owned work remains uncommitted. It then archives the
OpenSpec change and creates a checkpoint commit only for the remaining
finalization-owned diff. It does not squash or replace the earlier series.

## Risks / Trade-offs

- **More commits can increase history volume** → Require a non-empty coherent
  stage-owned diff and split only independent responsibilities.
- **A disposable utility plan may appear in history before later removal** →
  Treat that as intentional stage provenance; its later consumption is a
  separately coherent checkpoint.
- **Dirty working trees can blur ownership** → Require exact paths or hunks and
  preserve all unrelated changes.
- **Repeated verification can cost time** → Run stage-appropriate focused gates
  before each coherent commit and retain complete repository verification for
  finalization.
- **Automatic commit authority could be read too broadly** → State the allowed
  commit series and every withheld Git operation explicitly.

## Migration Plan

1. Add the material-gate checkpoint contract to the packaged workflow skill and
   its stage-assessment reference.
2. Reconcile the canonical consolidated-workflow specification.
3. Validate the prose/specification artifacts and complete repository quality
   gates without adding BDD or TDD for wording.
4. Apply the new checkpoint rule to subsequent material workflow gates; do not
   retroactively rewrite existing commits.

Rollback removes the new requirement and corresponding instructions. Existing
incremental commits remain valid Git history and are not rewritten.

## Open Questions

None.
