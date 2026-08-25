## MODIFIED Requirements

### Requirement: Single executable acceptance authority
For each accepted obligation, ZPP SHALL distinguish normative specification ownership from executable acceptance-example ownership. A testable public-system obligation SHALL have its concrete acceptance examples only in the independently runnable `features/<capability>/` root. `zpps-shape-bdd` SHALL transfer a provisional concrete OpenSpec example into that feature root, bind every resulting feature scenario to the exact OpenSpec root, capability, and requirement identity, and remove the corresponding OpenSpec scenario within the same completed stage outcome.

The binding identity SHALL be the exact ordered tuple `root`, `capability`, `requirement`, `feature`, and `scenario`, encoded as compact JSON immediately above the feature scenario. `root` SHALL be an exact registered `store:<uuid>` or a resolvable `repo:<git-root-relative-path-to-openspec-root>` locator; ZPP SHALL NOT mint a UUID. The referenced OpenSpec requirement SHALL remain normative authority but SHALL contain no concrete, trace-only, or target-form scenario for behavior owned by that feature scenario.

`zpps-form-specs` SHALL reject semantic acceptance duplication, an unresolved feature-to-requirement binding, a BDD-backed requirement without its executable feature scenario, a BDD-owned scenario retained anywhere in the applicable OpenSpec delta or canonical specification, or a spec-only requirement claimed by a feature scenario. A pure-functionality case matrix SHALL remain in unit tests. An obligation with no executable public-system observation SHALL remain normative specification content and SHALL NOT cause a fabricated BDD scenario.

#### Scenario: Transfer a testable acceptance example
- **WHEN** shaping accepts a provisional OpenSpec example that can be observed through the public system
- **THEN** `zpps-shape-bdd` creates the bound capability feature scenario and removes the corresponding OpenSpec scenario while retaining the normative requirement

#### Scenario: Reject duplicated acceptance authority
- **WHEN** specification formation finds an OpenSpec scenario for behavior owned by a bound feature scenario
- **THEN** `zpps-form-specs` blocks synchronization and identifies both authorities

#### Scenario: Preserve a specification-only obligation
- **WHEN** an accepted policy or owner boundary has no executable public-system observation
- **THEN** it remains normative OpenSpec requirement and scenario content and no BDD scenario is invented for it

#### Scenario: Verify an existing repo-local binding without a UUID
- **WHEN** read-only discovery or verification resolves a feature binding under the nearest repo-local `openspec/` root
- **THEN** the feature declaration retains `repo:openspec`, ZPP neither requests nor invents a UUID, and the referenced requirement resolves without an OpenSpec trace scenario

#### Scenario: Resolve a registered-store binding
- **WHEN** shaping binds a requirement through an exact store UUID returned by the public registered-store list
- **THEN** the feature declaration uses `store:<uuid>` with that returned UUID and no store-name alias

### Requirement: BDD-target canonical specification formation
During `form-specs`, `zpps-form-specs` SHALL remove each OpenSpec scenario whose executable authority is an accepted BDD feature scenario. The feature-side binding SHALL identify the exact OpenSpec root, capability, requirement, feature path, and scenario name; belong to the same capability owner; resolve to the requirement; use scenario-selected bindings that exercise the named behavior through the public system; and have relevant passing verification. Canonical OpenSpec SHALL retain the normative requirement and SHALL NOT retain a concrete, trace-only, or target-form scenario for that BDD-owned behavior.

Every scenario without qualifying BDD coverage SHALL remain a complete OpenSpec WHEN/THEN scenario. A stale, missing, cross-capability, invalid, recorder-only, pure-counting, wording-only, or unverified feature target SHALL block scenario removal rather than justify it.

#### Scenario: Remove a scenario owned by an exact BDD target
- **WHEN** an OpenSpec scenario maps to a verified same-capability feature scenario with an exact feature-side binding
- **THEN** canonical formation removes the OpenSpec scenario completely and retains the normative requirement plus the feature-owned executable authority

#### Scenario: Preserve a non-BDD specification scenario
- **WHEN** an accepted OpenSpec scenario has no qualifying executable BDD target
- **THEN** canonical formation preserves its complete WHEN/THEN contract in OpenSpec and does not invent feature coverage

#### Scenario: Reject invalid feature authority
- **WHEN** a proposed target is absent, stale, owned by another capability, unbound, recorder-only, pure-counting, wording-only, or lacks passing relevant verification
- **THEN** canonical formation keeps the specification scenario and leaves `form-specs` incomplete

### Requirement: Verified incremental checkpoint commits
Before declaring any workflow stage `completed` when that stage owns a non-empty coherent diff, `zpps-workflow-kernel` SHALL invoke the exact installed `zmem-author-commits` skill and complete its authorized commit workflow. The acting agent SHALL identify the accepted contract revision, stage-owned diff, applicable stage verification, commit authority, and exact paths or hunks proposed for staging. It SHALL preserve unrelated working-tree changes and SHALL exclude every path under the active OpenSpec change root from every incremental checkpoint.

The active proposal, delta specifications, design, tasks, and change metadata SHALL remain updated in the working tree throughout execution but SHALL NOT enter Git history while the change is active. Source, feature, test, runtime, and packaged-artifact work MAY be committed incrementally when independently coherent and verified. Before every commit, the agent SHALL prove that no active change-root path is staged, validate the complete message using zmem, create the checkpoint, and inspect its SHA with `zmem show`.

Explicit end-to-end workflow delegation SHALL grant checkpoint commit authority for the new source/test commits produced by the playbook. A standalone stage action SHALL require separate authority. Missing authority, staged active-change content, or failed verification, message validation, commit, or post-commit inspection SHALL leave the material gate incomplete.

A skipped stage or a stage with no stage-owned diff SHALL create no empty commit. After normal OpenSpec archival, the moved archive path becomes eligible for a terminal-state commit. After an accepted memory-fold route, the active change SHALL be removed before the zmem-bearing terminal commit and no OpenSpec archive path SHALL be created.

#### Scenario: Commit a material stage without the active change
- **WHEN** a workflow stage owns a verified coherent source or test diff and checkpoint authority is present
- **THEN** the workflow commits only the explicit stage paths, excludes the active OpenSpec change root, and records the inspected SHA

#### Scenario: Keep active planning current but uncommitted
- **WHEN** stage completion changes tasks or other artifacts under the active change root
- **THEN** the workflow updates those artifacts in the working tree and excludes them from every incremental commit

#### Scenario: Reject staged active-change content
- **WHEN** any proposed checkpoint includes a path under an active OpenSpec change root
- **THEN** zmem checkpoint handling blocks the commit until those paths are unstaged

#### Scenario: Preserve unrelated work
- **WHEN** the working tree contains changes outside the material stage-owned diff
- **THEN** the checkpoint stages only its explicit source or test paths and leaves unrelated and active-change paths untouched

#### Scenario: Keep annotations selective
- **WHEN** a checkpoint commit contains no durable decision, lesson, decay, cancellation, or registered custom memory
- **THEN** `zmem-author-commits` validates an ordinary human-readable commit message without requiring an annotation

#### Scenario: Commit normal archive state
- **WHEN** a verified change uses normal OpenSpec archival
- **THEN** the workflow archives first and only then may commit the resulting archive path with remaining terminal work

### Requirement: Scenarios bind to executable public-system verification
Every scenario `zpps-shape-bdd` creates or retains SHALL bind to executable verification that exercises the described behavior through the public system. A step implementation that records its own phrase, matches only literal text, proves only that it executed, or observes no system state SHALL NOT satisfy that binding obligation. Pure counting of files, stages, items, calls, or matches SHALL NOT be BDD acceptance evidence; a count MAY appear only as supplemental evidence after the scenario verifies an observable value, state transition, failure contract, ordering relationship, or other behavioral relationship selected by that scenario.

An obligation expressible only as prose SHALL remain a canonical specification requirement and SHALL NOT become an executable feature scenario. Verification SHALL NOT assert the literal wording of a governed artifact. When accepted behavior has no executable public-system observation, `zpps-shape-bdd` SHALL record a concrete non-BDD reason rather than creating an unbound scenario.

`zpps-shape-bdd` SHALL state this binding obligation as its invariant contract. Retained BDD traits SHALL remain contextual and SHALL NOT replace or waive it.

#### Scenario: Reject text-only verification
- **WHEN** a proposed BDD scenario succeeds only by finding or comparing literal text
- **THEN** the workflow treats the scenario as unbound and requires an observable public-system effect

#### Scenario: Reject pure counting as behavior
- **WHEN** a proposed BDD scenario asserts only a number of files, items, stages, calls, or matches
- **THEN** the workflow rejects it as acceptance evidence even when the expected count matches

#### Scenario: Permit a supplemental count
- **WHEN** a scenario first verifies its selected observable behavior and a count further constrains that same behavior
- **THEN** the count may remain supplemental but cannot replace the behavioral assertion

#### Scenario: Route a prose-only obligation to specification
- **WHEN** an accepted obligation has no executable public-system observation
- **THEN** the workflow records it as canonical specification content or a concrete non-BDD classification and creates no scenario for it

## ADDED Requirements

### Requirement: Terminal OpenSpec preservation route
At finalization, the workflow SHALL classify the verified active change as normal-archive or memory-fold eligible. Memory-fold eligibility SHALL require that every durable fact is completely expressible as validated zmem decisions or lessons and that the change carries no current normative behavior, nested or branching logic, failure contract, serialization rule, compatibility boundary, ownership boundary, or other information requiring canonical OpenSpec authority. Any doubt or partial fit SHALL select normal archive.

For normal archive, the workflow SHALL use the selected archive adapter and SHALL NOT commit the change directory until it has moved under `openspec/changes/archive`. For memory-fold, the workflow SHALL prepare and validate the complete zmem-bearing commit message, keep tasks complete, move the active change temporarily outside the worktree for recoverability, create no OpenSpec archive or canonical synchronization, commit the authorized implementation and zmem evidence, inspect the resulting SHA, then discard the temporary planning copy and release coordination truthfully. A failed commit SHALL restore the active change from the temporary copy.

#### Scenario: Fold a simple decision into zmem
- **WHEN** a verified change only adjusts simple words or variables and every durable rationale fits validated zmem without nested logic or normative behavior
- **THEN** finalization removes the active change before the zmem-bearing commit and creates no OpenSpec archive path

#### Scenario: Archive non-foldable behavior normally
- **WHEN** a change contains behavior, branching, nested logic, serialization, compatibility, ownership, or another canonical contract
- **THEN** finalization rejects memory-fold eligibility and requires normal OpenSpec archive before the change artifacts may be committed

#### Scenario: Restore planning after a failed fold commit
- **WHEN** the active change has been moved out of the worktree for a memory-fold commit and that commit fails
- **THEN** the workflow restores the exact active change and leaves the lifecycle incomplete
