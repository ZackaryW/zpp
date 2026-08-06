## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.6 and expose initialization, global installed-state update, profile, persistent global activation, saved-profile, local-layer, resolution, repository behavior verification through `zpp behave init`, `zpp behave <command>`, and `zpp behave <command> --all`, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain available through initialization and complete workflow installation, while `zpp update` SHALL maintain existing recognized global integrations without becoming an executable self-updater. Standard-workflow distribution SHALL use the independent `workflow` command group and behavior verification SHALL remain independent from workflow-skill lifecycle management. The generic `skill` command group SHALL NOT remain available.

Typer help SHALL distinguish `zpp init` as missing-state bootstrap plus explicitly selected hook configuration from `zpp update` as maintenance of initialized global ZPP state and already-installed integrations.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.6, exposes independent `init`, top-level `update`, `behave`, and standard-workflow lifecycle surfaces, and does not expose a generic skill-management group

#### Scenario: Distinguish initialization from update
- **WHEN** a user inspects `zpp init --help` and `zpp update --help`
- **THEN** the helpers distinguish bootstrap and selected-hook setup from global installed-state maintenance without claiming that ZPP upgrades its running executable

Executable public examples are maintained in the capability feature contracts that own bootstrap, verification orchestration, and workflow distribution.
