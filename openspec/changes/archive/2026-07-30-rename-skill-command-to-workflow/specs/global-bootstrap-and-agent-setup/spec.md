## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.0 and expose initialization, profile, saved-profile, local-layer, resolution, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain part of initialization, while standard-workflow distribution SHALL use the independent `workflow` command group. The generic `skill` command group SHALL NOT remain available.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.0, exposes the independent standard-workflow lifecycle group, and does not expose a generic skill-management group

Executable public examples are maintained in `features/bootstrap_and_agents.feature` and `features/workflow_skill_distribution.feature`.
