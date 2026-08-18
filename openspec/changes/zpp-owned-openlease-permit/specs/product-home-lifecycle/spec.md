## MODIFIED Requirements

### Requirement: Selected ZPP home layout
ZPP SHALL treat root `--path` as the selected ZPP home and SHALL default it to `~/.zpp`. Every OpenLease-backed ZPP operation SHALL use the exact `openlease` child of that selected home as its state root, and that state root SHALL hold registered repository topology, authorities, relationships, sessions, and leases in addition to bound configuration. Selecting or resolving a home SHALL NOT by itself create the home or state; establishing a session SHALL create the home and state when they are absent.

#### Scenario: Use the default ZPP home
- **WHEN** a caller omits root `--path`
- **THEN** ZPP selects `~/.zpp` as its home and supplies `~/.zpp/openlease` to OpenLease-backed operations

#### Scenario: Use an alternate ZPP home
- **WHEN** a caller supplies root `--path` with an eligible custom directory
- **THEN** ZPP treats that exact directory as the ZPP home and supplies only its `openlease` child as managed state

#### Scenario: Avoid eager home mutation
- **WHEN** a caller only requests help, version, or another operation that does not require filesystem state
- **THEN** selecting the ZPP home creates no directory or OpenLease state

#### Scenario: BDD target — Create home state when establishing a session
- **WHEN** executable behavior is covered by `features/product_home_lifecycle/product_home_lifecycle.feature::Create home state when establishing a session`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
