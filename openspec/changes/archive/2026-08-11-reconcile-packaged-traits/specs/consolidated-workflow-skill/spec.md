## MODIFIED Requirements

### Requirement: Complete standard behavior reauthoring
ZPP SHALL package applicable repository environment behavior as one-family TOML source documents under `artifacts/traits`. The packaged source path SHALL NOT be imposed as the runtime collection path. Related language or framework variants SHALL remain ordered, self-contained flavors without content inheritance. The standard collection SHALL contain BDD operation, BDD structure, BDD execution modes, TDD, build, dependency, available-tool, and zero-assumption behavior. OpenLease lease/conflict coordination and workflow finalization/reconciliation policy SHALL remain with their owning component or consolidated workflow skill and SHALL NOT be duplicated as packaged traits. The universal zero-assumption family SHALL declare always-run activation explicitly.

#### Scenario: Package the reconciled standard collection
- **WHEN** ZPP builds its distributed workflow assets
- **THEN** the collection includes `bdd`, `bdd-structure`, `bdd-execution`, `tdd`, `build`, `dependencies`, `tooling`, and `zero-assumptions` without packaged lease or reconciliation families

#### Scenario: Keep BDD execution separate from workflow authority
- **WHEN** a user inspects the packaged BDD execution family
- **THEN** its manual, disabled, complete, targeted, and targeted-default flavors are available under `bdd-execution` and no `bdd-workflow` compatibility family is packaged

#### Scenario: Keep component operations out of traits
- **WHEN** a workflow encounters an OpenLease conflict or reaches final reconciliation
- **THEN** the owning component or consolidated workflow skill supplies the operational contract without relying on a packaged trait body

#### Scenario: Package only direct available-tool guidance
- **WHEN** a user inspects the packaged tooling family
- **THEN** it contains evidence-backed `rg` and `jq` guidance while dedicated zmem skills retain zmem workflow policy
