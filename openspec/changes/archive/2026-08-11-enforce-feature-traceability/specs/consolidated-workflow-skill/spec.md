## ADDED Requirements

### Requirement: Behavior-only feature shaping
The consolidated workflow skill SHALL create or materially change Gherkin only from accepted externally observable public, integration, or fix behavior in the active change's capability delta specifications. Proposals, designs, tasks, documentation, packaged artifacts, configuration-only changes, and implementation details SHALL NOT be Gherkin sources. When no qualifying delta behavior remains, the skill SHALL record `shape` as `skipped: not applicable` and SHALL NOT create or change a feature.

When qualifying behavior exists, every created or materially changed scenario SHALL trace to at least one such delta obligation, and every such obligation SHALL have scenario coverage or a concrete non-BDD classification. Obligations MAY split or combine without copied wording. An untraced scenario, uncovered obligation, or unresolved classification SHALL block shape completion.

#### Scenario: Skip artifact-only feature shaping
- **WHEN** an active change contains only proposals, designs, tasks, documentation, packaged artifacts, configuration, or implementation work and no qualifying behavior delta
- **THEN** the workflow records `shape` as not applicable and creates or changes no Gherkin feature

#### Scenario: Complete behavior-delta feature shaping
- **WHEN** an active capability delta contains accepted externally observable behavior
- **THEN** every created or materially changed scenario traces to that behavior and every behavior obligation has scenario coverage or a concrete non-BDD classification before shape completes

#### Scenario: Reject an untraced scenario or coverage gap
- **WHEN** a proposed scenario lacks a qualifying delta source or a qualifying behavior obligation lacks coverage or classification
- **THEN** the workflow keeps shape incomplete instead of inventing or silently omitting behavior

### Requirement: Behavior-only TDD shaping
The consolidated workflow skill SHALL create or change TDD tests only for executable behavior. Artifact loading, unloading, parsing, validation, and conversion into runtime classes or models SHALL be eligible TDD subjects. Tests whose only purpose is to pin prose or assert arbitrary artifact wording SHALL NOT be created. When no executable utility behavior remains, the skill SHALL record `mature-utilities` as `skipped: not applicable` and SHALL NOT create or change a unit test.

#### Scenario: Skip artifact-wording TDD
- **WHEN** an active change changes artifact prose or wording but introduces no executable utility behavior
- **THEN** the workflow records `mature-utilities` as not applicable and creates or changes no unit test

#### Scenario: Apply TDD to artifact processing behavior
- **WHEN** an accepted change requires new or changed artifact loading, unloading, parsing, validation, or runtime class conversion behavior
- **THEN** the workflow uses TDD to prove that executable behavior without pinning unrelated artifact wording
