# Stage assessment contract

Apply this complete contract before every ZPP workflow stage action. It is
normative content of the installed `zpp-workflow` skill, not a separate skill or
authority. It cannot itself advance a stage, authorize mutation, establish
verification, or declare completion.

## Present the assessment

Before executing the explicitly requested stage, present:

1. **Contract revision** — identify the current accepted owner input, proposal,
   capability deltas, and any `Unresolved — Do Not Assume` entry that controls
   the assessment.
2. **Requested stage** — record the explicit dispatch request. Its name supplies
   no gate evidence.
3. **Predecessor outcomes** — list every predecessor in order with its current
   `completed` or evidence-backed `skipped: not applicable` outcome and the
   repository or accepted-contract evidence supporting it.
4. **Invalid evidence** — identify every missing, stale, failed, contradicted, or
   superseded checkpoint.
5. **Accepted effects** — classify the complete change using the effect classes
   below.
6. **Stage-owned output** — state what the requested stage must produce for those
   effects.
7. **Eligibility** — declare the stage eligible or blocked and name every
   blocker. Do not perform the stage while it is blocked.

After an eligible stage runs, record its observed result. `clarify` and
`finalize` must be `completed`; each middle stage must be `completed` or
`skipped: not applicable` under its evidence gate.

## Enforce predecessor gates

| Requested stage | Required current predecessors | Stage-owned result |
| --- | --- | --- |
| `clarify` | None | One coherent accepted proposal and capability-delta contract with no unresolved product decision |
| `shape` | `clarify` | Complete traced feature and fix contracts for accepted externally observable behavior |
| `plan-utilities` | `clarify`, `shape` | Disposable signature-level plan for every required new or changed utility boundary |
| `mature-utilities` | Through `plan-utilities` | Fail-first proof, minimum implementation, independent verification, and checkpoint for planned utility behavior |
| `wire` | Through `mature-utilities` | Public-boundary bindings and product composition for approved behavior and utilities |
| `form-specs` | Through `wire` | Canonical specification reconciliation for every mature behavior or accepted capability delta |
| `finalize` | All prior stages | Complete verification, retained-successor reconciliation, OpenSpec archival, and only separately authorized commit work |

A predecessor outcome is current only when it applies to the same accepted
contract revision. If any required predecessor is absent, stale, failed, or
superseded, block the requested stage. Identify the earliest unsatisfied stage,
but do not execute it without an explicit invocation unless end-to-end
progression was separately authorized.

When newer input changes or appears to change the contract, return to
`clarify`. Invalidate every downstream assessment derived from the older
contract and replace it only after the complete agreement converges again.

## Classify effects before applicability

Classify the complete accepted change by what changes, not by filenames,
artifact labels, selected traits, or generic workflow convention:

- **Externally observable public, integration, or fix behavior** may require
  `shape` and `wire`. Create BDD only for an accepted shaped obligation that can
  be exercised through the public system.
- **Pure executable utility behavior** may require `plan-utilities` and
  `mature-utilities`. Keep pure-function case matrices in unit TDD.
- **Executable artifact processing or update behavior** includes loading,
  parsing, validation, conversion, projection, and update mechanics. Assess it
  at its actual public or utility boundary even when it operates on a skill,
  environment, configuration, or documentation artifact.
- **Spec-governed prose or declarative instructions** require `clarify`,
  `form-specs`, and `finalize` when an accepted delta changes their governed
  content. By themselves they require no Gherkin, BDD execution, utility plan,
  unit TDD, or product wiring.
- **Ungoverned non-runtime artifact text** uses the artifact-only maintenance
  route and creates no product-workflow stage outcomes.
- **Mixed changes** use the union of stage obligations from their executable and
  governed effects. Supporting prose does not create its own BDD or TDD work.

Never use an artifact label alone to skip executable behavior. A prose-only
skill instruction update has no test subject; a change to code that loads,
validates, projects, or updates that skill remains testable.

## Assess each conditional stage

- `shape` is `skipped: not applicable` only when no accepted public,
  integration, or fix behavior requires an executable feature contract.
- `plan-utilities` is `skipped: not applicable` only when the complete accepted
  feature and effect set requires no new or changed utility boundary.
- `mature-utilities` is `skipped: not applicable` only when the settled utility
  plan contains no executable behavior to prove or implement.
- `wire` is `skipped: not applicable` only when no approved behavior requires a
  public binding or product composition change.
- `form-specs` is `skipped: not applicable` only when neither mature behavior nor
  an accepted capability delta requires canonical reconciliation. A governed
  prose delta therefore keeps `form-specs` required even when all four earlier
  conditional stages are not applicable.

A failed command, incomplete implementation, selected trait, descriptive
repository value, or confident agent statement cannot establish
not-applicability. When evidence is insufficient, run the stage normally or
report the unresolved owner decision; never guess a skip.

## Preserve visible progression

Automatic end-to-end authority permits progression only after the current stage
has an observed satisfied outcome. Invoke the next stage as a new visible action
and repeat this assessment. The assessment never chooses callbacks, runs
verification, stages files, commits, merges, rebases, archives, or reconciles
retained work on its own.
