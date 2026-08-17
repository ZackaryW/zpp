## ADDED Requirements

### Requirement: Bounded artifact-only maintenance route
The consolidated workflow skill SHALL classify a requested outcome before requiring a workflow stage and MAY route a change limited to ungoverned non-runtime artifacts directly to its owning artifact guidance without creating an OpenSpec change, Gherkin, a utility plan, TDD, or workflow-stage outcomes. Ungoverned artifacts SHALL be limited to repository README and reference documentation, repository-local ZPP traits and context, and commit metadata.

The route SHALL NOT apply to a spec-governed packaged artifact. The packaged workflow skill document, a packaged trait document, and a canonical OpenSpec specification SHALL be spec-governed, because a canonical requirement describes their content as observable behavior. A change to a spec-governed artifact SHALL use the product workflow and SHALL reconcile canonical specifications before finalization, whether or not it changes executable behavior.

Classification SHALL follow effect rather than filename. Artifact loading, parsing, validation, class conversion, and any artifact-backed change to executable or public behavior SHALL use the product workflow. For a mixed change, the skill SHALL apply the workflow to its behavioral portion while keeping supporting ungoverned artifact text out of BDD and TDD obligations.

#### Scenario: Route ungoverned artifact maintenance directly
- **WHEN** a requested change is limited to repository README or reference documentation, repository-local ZPP traits or context, or commit metadata
- **THEN** the skill edits through the owning artifact guidance and creates no OpenSpec change, feature, utility plan, unit test, or stage outcome

#### Scenario: Refuse the route for the packaged workflow skill
- **WHEN** a requested change alters the packaged workflow skill document or a packaged trait document and changes no executable behavior
- **THEN** the skill treats it as a spec-governed product change and does not accept artifact-only maintenance as its route

#### Scenario: Reconcile canonical specifications for a spec-governed artifact
- **WHEN** a spec-governed packaged artifact change reaches finalization
- **THEN** the canonical specification describing that artifact's content has been reconciled with the shipped wording and an unreconciled divergence blocks finalization

#### Scenario: Classify a mixed change by effect
- **WHEN** a requested change alters ungoverned artifact text alongside executable or public behavior
- **THEN** the workflow governs the behavioral portion and the supporting ungoverned text creates no BDD or TDD obligation

### Requirement: Monorepo behavior ownership
In a monorepo, the consolidated workflow skill SHALL shape and bind Gherkin only at an established public application or composition owner and only through that owner's real composed entry point. A reusable implementation subpackage SHALL own focused fail-first unit TDD rather than a feature-level acceptance contract. Public BDD MAY compose those subpackages but SHALL NOT replace their unit tests.

The skill SHALL determine package topology and dependency direction by direct inspection and SHALL NOT encode repository structure as behavior tests. When the owning application or composition boundary for accepted behavior is unresolved, the skill SHALL expose that ownership question to its owner rather than selecting a boundary.

#### Scenario: Shape behavior at the composition owner
- **WHEN** accepted behavior in a monorepo belongs to an established public application or composition owner
- **THEN** the workflow shapes and binds its Gherkin at that owner through its real composed entry point

#### Scenario: Keep subpackage contracts as unit TDD
- **WHEN** accepted behavior belongs to a reusable implementation subpackage rather than a public composition owner
- **THEN** the workflow proves it with focused fail-first unit TDD and creates no feature-level acceptance contract for that subpackage

#### Scenario: Refuse to encode repository structure as behavior
- **WHEN** a proposed scenario would assert package topology or dependency direction
- **THEN** the workflow verifies that structure by direct inspection instead of creating the scenario

#### Scenario: Expose unresolved package ownership
- **WHEN** the owning application or composition boundary for accepted behavior cannot be established from repository evidence
- **THEN** the workflow exposes the ownership question to its owner rather than selecting a boundary

### Requirement: Scenarios bind to executable public-system verification
Every scenario the consolidated workflow skill creates or retains SHALL bind to executable verification that exercises the described behavior through the public system. A step implementation that records its own phrase, asserts only that it executed, or observes no system state SHALL NOT satisfy that binding obligation. Verification SHALL be selected by the scenario it serves, and a capability-wide assertion block that runs identically after every scenario in its root SHALL NOT establish scenario coverage.

An obligation that can be expressed only as prose SHALL be recorded as a canonical specification requirement and SHALL NOT be represented as a scenario. Verification SHALL NOT assert the literal wording of an artifact whose content a canonical requirement already governs. When accepted behavior has no executable public-system observation, the skill SHALL record that obligation as non-BDD with a concrete reason rather than creating an unbound scenario.

The packaged BDD guidance SHALL state this binding obligation so that repositories consuming ZPP receive it as contextual policy. The guidance SHALL NOT supply a command, target, or completion authority.

#### Scenario: Reject a recording-only binding
- **WHEN** a scenario's steps record their own phrases or assert only that they executed
- **THEN** the workflow treats the scenario as unbound and does not count it as behavior coverage

#### Scenario: Reject capability-wide assertion blocks as coverage
- **WHEN** a capability's verification runs the same assertions after every scenario in its root
- **THEN** the workflow does not accept those assertions as per-scenario coverage and requires verification selected by the scenario it serves

#### Scenario: Route a prose-only obligation to specification
- **WHEN** an accepted obligation has no executable public-system observation
- **THEN** the workflow records it as a canonical specification requirement or a concrete non-BDD classification and creates no scenario for it

#### Scenario: Refuse to assert governed artifact wording
- **WHEN** proposed verification would assert the literal wording of an artifact already governed by a canonical requirement
- **THEN** the workflow relies on the canonical requirement and does not create that assertion

#### Scenario: Receive the binding obligation as packaged guidance
- **WHEN** a repository resolves ZPP's packaged BDD guidance
- **THEN** that guidance states the scenario binding obligation without supplying a command, target, or completion authority
