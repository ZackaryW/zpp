## ADDED Requirements

### Requirement: Authority-aware workflow reconciliation
Clarification SHALL compare relevant temporal zmem history with the current canonical OpenSpec baseline before persisting accepted changes into the active proposal. Specification formation SHALL promote only mature enduring behavior into canonical OpenSpec and SHALL leave abandoned or superseded chronology in zmem. ZPP SHALL NOT require zmem dependency-graph semantics.

#### Scenario: Reconcile a changed decision
- **WHEN** a change has canonical behavior, a mutable proposal, and temporally ordered zmem decisions
- **THEN** the workflow forms current authority from mature accepted behavior without treating historical directions as current truth

### Requirement: Explicit temporal-memory checkpoints
Every material workflow gate SHALL produce its required logical commit, but SHALL add zmem only when that commit contains a meaningful decision change, reversal, fallback, surprise, or lesson worthy of durable temporal recall. Verification, stage completion, or specification adoption alone SHALL NOT require or repeat a zmem annotation.

The bundled commit-message validators SHALL accept valid conventional commits with zero zmem annotations in normal mode and SHALL require at least one canonical annotation when memory-bearing validation is explicitly requested.

#### Scenario: Validate ordinary and memory-bearing commits
- **WHEN** the same valid unannotated conventional message is checked normally and as a memory-bearing checkpoint
- **THEN** normal validation succeeds and memory-bearing validation rejects the missing canonical zmem annotation
