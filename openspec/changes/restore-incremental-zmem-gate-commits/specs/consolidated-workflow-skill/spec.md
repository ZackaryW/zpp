## ADDED Requirements

### Requirement: Verified incremental checkpoint commits
Before declaring any workflow stage `completed` when that stage owns a non-empty
coherent diff, the consolidated workflow skill SHALL invoke the exact installed
`zmem-author-commits` skill and complete its authorized commit workflow. The
acting agent SHALL identify the accepted contract revision, the stage-owned
diff, applicable stage verification and its observed result, checkpoint commit
authority, and the exact paths or hunks proposed for staging. It SHALL preserve
unrelated working-tree changes.

The commit series SHALL be dependency ordered and SHALL separate distinct
responsibilities when each intermediate commit is independently coherent and
verifiable. It SHALL NOT create a split whose intermediate state is known to
break the repository. Before each commit, the agent SHALL complete the
stage-appropriate verification and validate the complete proposed message using
zmem. After each authorized commit, it SHALL record the resulting SHA and inspect
the commit with `zmem show`. The `zmem-author-commits` operation SHALL decide
whether durable memory warrants an annotation; a checkpoint SHALL NOT require a
meaningless annotation.

Explicit end-to-end workflow delegation SHALL grant checkpoint commit authority
for the new commits produced by the automatically progressed stage series. A
standalone stage action SHALL require separately granted commit authority. This
authority SHALL NOT include amend, merge, rebase, push, conflict reconciliation,
callback selection, or inclusion of unrelated work. Missing commit authority or
any failed verification, zmem validation, commit, or post-commit inspection SHALL
leave a material gate incomplete.

A skipped stage or a stage with no stage-owned diff SHALL record its observed
outcome without creating an empty commit. At finalization, the workflow SHALL
verify that every material completed gate has its checkpoint evidence, archive
the OpenSpec change, and commit only the remaining finalization-owned diff. It
SHALL NOT collapse or replace the preceding checkpoint series.

#### Scenario: Commit a material stage gate
- **WHEN** a workflow stage owns a non-empty coherent diff and checkpoint commit authority is present
- **THEN** the workflow verifies the stage-owned work, follows `zmem-author-commits`, creates the validated commit series from only its explicit paths or hunks, and records each inspected SHA before declaring the stage completed

#### Scenario: Skip an empty checkpoint
- **WHEN** a stage is skipped as not applicable or completes with no stage-owned diff
- **THEN** the workflow records the observed stage outcome without creating an empty commit

#### Scenario: Pause without commit authority
- **WHEN** a material stage has verified work but its invocation carries no checkpoint commit authority
- **THEN** the workflow leaves the gate incomplete and pauses before creating a commit

#### Scenario: Carry end-to-end checkpoint authority
- **WHEN** the owner explicitly delegates the workflow end to end
- **THEN** automatic progression may create each required stage checkpoint commit without requesting ordinary per-commit approval and gains no authority for other Git operations

#### Scenario: Preserve unrelated work
- **WHEN** the working tree contains changes outside the material stage-owned diff
- **THEN** the checkpoint stages only its explicit paths or hunks and leaves the unrelated changes untouched

#### Scenario: Split only coherent responsibilities
- **WHEN** one material gate contains multiple distinct responsibilities
- **THEN** the workflow commits them in dependency order when every intermediate state is coherent and verifiable and keeps them together when a split would knowingly break the repository

#### Scenario: Reject a failed checkpoint
- **WHEN** stage verification, zmem message validation, commit creation, or resulting-commit inspection fails
- **THEN** the workflow reports the failure and does not declare the material gate completed

#### Scenario: Keep annotations selective
- **WHEN** a checkpoint commit contains no durable decision, lesson, decay, cancellation, or registered custom memory
- **THEN** `zmem-author-commits` validates an ordinary human-readable commit message without requiring an annotation

#### Scenario: Finalize an incremental series
- **WHEN** all pre-finalization stages have observed outcomes and the change reaches finalization
- **THEN** the workflow verifies every material checkpoint, archives the change, and commits only remaining finalization-owned work without collapsing the earlier commits
