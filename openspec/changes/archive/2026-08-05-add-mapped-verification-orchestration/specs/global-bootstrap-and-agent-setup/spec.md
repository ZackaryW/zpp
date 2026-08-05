## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.0 and expose initialization, profile, persistent global activation, saved-profile, local-layer, resolution, repository behavior verification through `zpp behave init`, `zpp behave <command>`, and `zpp behave <command> --all`, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain available through initialization and SHALL also participate in complete workflow installation, while standard-workflow distribution SHALL use the independent `workflow` command group and behavior verification SHALL remain independent from workflow-skill lifecycle management. The generic `skill` command group SHALL NOT remain available.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.0, exposes profile and global lifecycle behavior plus independent `behave` and standard-workflow lifecycle surfaces, and does not expose a generic skill-management group

Executable public examples are maintained in the capability feature contracts that own bootstrap, verification orchestration, and workflow distribution.
