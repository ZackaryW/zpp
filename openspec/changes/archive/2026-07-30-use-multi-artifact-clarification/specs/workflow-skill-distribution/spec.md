## MODIFIED Requirements

### Requirement: Authority-aware workflow reconciliation
Clarification SHALL compare relevant temporal zmem history with the current
canonical OpenSpec baseline before persisting accepted change material. The
proposal SHALL retain motivation, scope, capability inventory, impact, and
unresolved owner decisions. Every declared new or modified capability SHALL
have a corresponding OpenSpec delta at `specs/<capability>/spec.md`, and
clarification SHALL persist settled behavioral requirements into their owning
deltas instead of collapsing the complete contract into `proposal.md`.

Feature shaping SHALL consume the proposal and every declared delta spec. Once
Gherkin owns executable examples, shaping SHALL remove only duplicated examples
from the OpenSpec artifacts and SHALL preserve their stable intent,
constraints, invariants, and acceptance obligations. Specification formation
SHALL reconcile the existing deltas against mature green behavior before
promoting them into canonical OpenSpec.

ZPP SHALL leave abandoned or superseded chronology in zmem and SHALL NOT
require zmem dependency-graph semantics. Design and task artifacts SHALL follow
the selected OpenSpec schema and artifact instructions rather than a universal
ZPP one-file restriction.

#### Scenario: Clarify a multi-capability change
- **WHEN** clarification settles behavior for capabilities declared by an OpenSpec proposal
- **THEN** the overview remains in `proposal.md` and each capability contract is persisted in its own delta spec

#### Scenario: Reconcile a changed decision
- **WHEN** a change has canonical behavior, mutable planning artifacts, and temporally ordered zmem decisions
- **THEN** the workflow forms current authority from mature accepted behavior without treating historical directions as current truth

Executable public examples for this requirement are maintained in `features/workflow_skill_distribution.feature`.
