## MODIFIED Requirements

### Requirement: Authority-aware workflow reconciliation
Before product-change bootstrapping, clarification SHALL classify every requested outcome by observable ownership as repository-environment/tooling work, shipped source/product behavior, or a mixed request. Environmental-only work SHALL remain outside product capability deltas, Gherkin, and canonical product specifications and SHALL use its native implementation and verification surface. For a mixed request, clarification SHALL split the work so only shipped behavior enters the product change. A path or filename alone SHALL NOT override the observable ownership classification, and a genuinely ambiguous classification SHALL be resolved before product OpenSpec creation or selection.

For shipped behavior, clarification SHALL compare relevant temporal zmem history with the current canonical OpenSpec baseline before persisting accepted change material. The proposal SHALL retain motivation, scope, capability inventory, impact, and unresolved owner decisions. Every declared new or modified capability SHALL have a corresponding OpenSpec delta at `specs/<capability>/spec.md`, and clarification SHALL persist settled behavioral requirements into their owning deltas instead of collapsing the complete contract into `proposal.md`.

Feature shaping SHALL consume the proposal and every declared delta spec. In a monorepo, shaping SHALL identify each justifiably affected subproject from established repository boundaries and SHALL place executable behavior in each affected subproject's native feature surface. It SHALL NOT require one root-level feature file, framework, runner, or uniform project structure, SHALL NOT treat unaffected subprojects as part of the feature contract, and SHALL create a cross-subproject scenario only when the accepted public behavior itself crosses those boundaries. Once Gherkin owns executable examples, shaping SHALL remove only duplicated examples from the OpenSpec artifacts and SHALL preserve their stable intent, constraints, invariants, and acceptance obligations. Specification formation SHALL reconcile the existing deltas against mature green behavior before promoting them into canonical OpenSpec.

ZPP SHALL leave abandoned or superseded chronology in zmem and SHALL NOT require zmem dependency-graph semantics. Design and task artifacts SHALL follow the selected OpenSpec schema and artifact instructions rather than a universal ZPP one-file restriction.

#### Scenario: Classify work before product bootstrapping
- **WHEN** a request contains environmental tooling, shipped source behavior, or both
- **THEN** clarification classifies and separates those outcomes before product OpenSpec bootstrapping so environmental work does not become a product capability or BDD contract

#### Scenario: Clarify a multi-capability change
- **WHEN** clarification settles behavior for capabilities declared by an OpenSpec proposal
- **THEN** the overview remains in `proposal.md` and each capability contract is persisted in its own delta spec

#### Scenario: Shape justified monorepo feature surfaces
- **WHEN** an accepted shipped behavior change affects one or more established subprojects in a monorepo
- **THEN** feature shaping creates executable behavior only in each justifiably affected native feature surface without requiring a single repository-wide project shape

#### Scenario: Reconcile a changed decision
- **WHEN** a change has canonical behavior, mutable planning artifacts, and temporally ordered zmem decisions
- **THEN** the workflow forms current authority from mature accepted behavior without treating historical directions as current truth
