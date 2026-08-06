## MODIFIED Requirements

### Requirement: Optional provider delegation
A named command SHALL select a configured execution provider. ZPP SHALL know Nx as a first-class provider and SHALL prefer compatible repository-local executables in this order: an existing package-local wrapper, an official repository-root wrapper backed by `.nx/installation`, then a PATH-available executable. Every discovered executable SHALL be normalized to an absolute path before inspection or execution. ZPP SHALL delegate only to an existing repository-configured Nx project/target surface and SHALL revalidate the executable and declared Nx surface before execution. It SHALL NOT ask an agent to supply command text, use a package runner in a mode that downloads Nx, install or migrate Nx, connect a workspace to Nx Cloud, or install framework plugins.

Repositories SHALL own and version their Nx installation and plugins. ZPP SHALL treat plugin implementation as opaque and consume only the project and target surface exposed by the workspace. Missing framework support SHALL be resolved by repository-owned plugin installation, a repository-owned Nx command target, or a provider-neutral declaration. ZPP SHALL support the provider-neutral path as an equal first-class provider without requiring Nx to be installed. Provider selection SHALL come from validated repository configuration rather than trait activation, agent preference, or executable availability alone.

#### Scenario: Delegate to configured Nx
- **WHEN** a valid named command selects Nx and the required repository Nx configuration and executable are available
- **THEN** ZPP delegates only the validated selected targets to the repository's Nx task surface

#### Scenario: Discover a non-JavaScript repository wrapper
- **WHEN** an Nx workspace uses the official repository-root wrapper backed by `.nx/installation` and has no package-local wrapper
- **THEN** ZPP discovers that wrapper as an absolute repository-owned executable before considering PATH

#### Scenario: Run a provider-neutral command
- **WHEN** a valid named command selects a provider-neutral command declaration
- **THEN** ZPP executes that declaration with its validated selected targets without installing or invoking Nx

#### Scenario: Keep repository plugins opaque
- **WHEN** a repository exposes a configured Nx project and target through any repository-owned framework plugin or command target
- **THEN** ZPP validates and invokes that surface without installing, configuring, or interpreting the plugin

#### Scenario: Reject an unavailable provider
- **WHEN** the configured provider or its required repository state is unavailable
- **THEN** ZPP starts no alternate provider implicitly and identifies the unmet provider requirement
