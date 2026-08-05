## Purpose

Defines repository-owned affected-verification mapping and safe execution of named commands through optional task providers without making any provider mandatory.

## ADDED Requirements

### Requirement: Repository-owned named verification
`zpp behave init` SHALL initialize or validate the target repository's committed `zpp.behave.yaml` and report whether a compatible Nx executable and workspace surface are currently discoverable without making Nx mandatory. Repeated initialization SHALL preserve an existing valid mapping. `zpp behave <command>` SHALL select one named repository verification declaration, and `--all` SHALL remain an optional selection override for that command.

The selected name MUST resolve to one validated declaration before any configured process is started, and an absent, invalid, or duplicate declaration SHALL fail without running a fallback command implicitly. Derived impact evidence and execution state SHALL remain machine-local and SHALL NOT replace the committed mapping as runtime authority.

#### Scenario: Initialize a behavior mapping
- **WHEN** a caller runs `zpp behave init` in a repository without `zpp.behave.yaml`
- **THEN** ZPP creates a valid committed mapping scaffold and reports current Nx discovery without requiring Nx or inventing repository verification commands

#### Scenario: Preserve an existing mapping
- **WHEN** a caller runs `zpp behave init` with an existing valid mapping
- **THEN** ZPP validates and preserves that mapping while refreshing only reported machine-local provider discovery

#### Scenario: Resolve a declared command
- **WHEN** a caller selects a valid named verification command in a repository with a valid mapping
- **THEN** ZPP resolves exactly that declaration and prepares only its declared verification execution

#### Scenario: Reject an unavailable command
- **WHEN** the selected command is absent, duplicated, or invalid
- **THEN** ZPP identifies the selected name and starts no configured process

### Requirement: Bounded affected-target filtering
Each named command SHALL declare a closed set of filterable verification targets and repository impact rules. For local execution, ZPP SHALL derive the change from `HEAD` plus staged, unstaged, and untracked working-tree paths. For revision-based execution, the caller SHALL provide the comparison base and head. Unmapped or uncertain changed paths SHALL select every declared target rather than be treated as unaffected.

Agents MAY help author or broaden the committed mapping, but runtime selection SHALL remain deterministic from validated repository state. Changed paths, agent text, and undeclared target names SHALL NOT become executable command syntax.

#### Scenario: Filter to declared affected targets
- **WHEN** repository evidence maps the current change to a proper subset of one named command's declared targets
- **THEN** ZPP prepares that command with only the validated affected target values

#### Scenario: Reject executable agent output
- **WHEN** agent-assisted impact output contains an undeclared target or command material
- **THEN** ZPP does not execute that material and reports why it cannot participate

#### Scenario: Fall back for unknown impact
- **WHEN** any changed path has no conclusive declared impact mapping
- **THEN** ZPP selects every target declared by the named command

### Requirement: Typed in-place target expansion
A provider-neutral command SHALL be represented as a typed argv sequence with one declared target-expansion position. ZPP SHALL replace that position with the selected targets as distinct argv values and SHALL NOT evaluate the resulting values through a command shell. An invalid number of expansion positions or an empty expansion where the declaration forbids it SHALL fail before process creation.

#### Scenario: Expand selected targets as argv
- **WHEN** a valid provider-neutral command selects multiple affected targets
- **THEN** ZPP inserts each target as one argv value at the declared expansion position and starts the configured executable without a shell

#### Scenario: Reject an invalid expansion declaration
- **WHEN** a command omits, duplicates, or otherwise invalidates its required target-expansion position
- **THEN** ZPP identifies the declaration error and starts no process

### Requirement: Optional provider delegation
A named command SHALL select a configured execution provider. ZPP SHALL know Nx as a first-class provider, prefer a compatible repository-local Nx executable over a PATH-available executable, and delegate only to an existing repository-configured Nx project/target surface. ZPP SHALL revalidate the executable and declared Nx surface before execution. It SHALL NOT ask an agent to supply command text, use a package runner in a mode that downloads Nx, install or migrate Nx, connect a workspace to Nx Cloud, or install framework plugins.

Repositories SHALL own and version their Nx installation and plugins. ZPP SHALL treat plugin implementation as opaque and consume only the project and target surface exposed by the workspace. Missing framework support SHALL be resolved by repository-owned plugin installation, a repository-owned Nx command target, or a provider-neutral declaration. ZPP SHALL support the provider-neutral path as an equal first-class provider without requiring Nx to be installed. Provider selection SHALL come from validated repository configuration rather than trait activation, agent preference, or executable availability alone.

#### Scenario: Delegate to configured Nx
- **WHEN** a valid named command selects Nx and the required repository Nx configuration and executable are available
- **THEN** ZPP delegates only the validated selected targets to the repository's Nx task surface

#### Scenario: Run a provider-neutral command
- **WHEN** a valid named command selects a provider-neutral command declaration
- **THEN** ZPP executes that declaration with its validated selected targets without installing or invoking Nx

#### Scenario: Keep repository plugins opaque
- **WHEN** a repository exposes a configured Nx project and target through any repository-owned framework plugin or command target
- **THEN** ZPP validates and invokes that surface without installing, configuring, or interpreting the plugin

#### Scenario: Reject an unavailable provider
- **WHEN** the configured provider or its required repository state is unavailable
- **THEN** ZPP starts no alternate provider implicitly and identifies the unmet provider requirement

### Requirement: Filtered and complete execution
`zpp behave` SHALL use deterministic mapped filtering by default. An explicit `--all` selection SHALL execute every target declared by the selected named command without discarding provider cache behavior. Provider-specific uncached verification SHALL be represented by a separately declared audit command rather than a universal cache flag that some providers cannot honor.

#### Scenario: Execute the mapped subset
- **WHEN** the caller selects a valid named command without `--all` and every changed path has a conclusive mapping
- **THEN** ZPP runs only the deterministically affected declared targets

#### Scenario: Execute every declared target
- **WHEN** the caller explicitly supplies `--all`
- **THEN** ZPP submits every target declared by the named command to its configured provider
