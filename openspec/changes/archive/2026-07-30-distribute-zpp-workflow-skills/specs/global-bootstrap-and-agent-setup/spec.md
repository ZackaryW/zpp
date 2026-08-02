## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.0 and expose initialization, profile, saved-profile, local-layer, resolution, workflow-skill lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain part of initialization, while permanent workflow-skill distribution SHALL use the independent `skill` command group.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.0 and exposes the confirmed command hierarchy including the independent workflow-skill lifecycle group

Executable public examples are maintained in `features/bootstrap_and_agents.feature` and `features/workflow_skill_distribution.feature`.
