## ADDED Requirements

### Requirement: Repository-owned named verification
`zpp behave init` SHALL discover the current Git worktree root, then explicitly initialize or validate its root `zpp.behave.yaml` as a dedicated YAML document bound invocation-scoped to extension identity `zpp.behave`. The scaffold SHALL remain `version: 1` with an empty `commands` mapping. Existing valid version-one files SHALL remain semantically and structurally authored in place; ZPP SHALL NOT wrap them under `zpp.behave`, convert them to TOML or JSON, or run the former behavior implementation as fallback. Initialization SHALL report current provider discovery as machine-local diagnostics without changing provider configuration.

`zpp behave <command>` SHALL open the same exact dedicated binding and invoke one named `zpp.behave` operation. The selected command and every exact target or gate name MUST resolve within one strict declaration before any configured process starts. An absent, invalid, or duplicate declaration, undeclared requested target, or unknown requested gate SHALL fail without fallback. Derived impact evidence and execution outcomes SHALL remain managed or machine-local and SHALL NOT replace the committed mapping as runtime authority.

Direct initialization and execution SHALL NOT create an OpenLease space, topology node, source record, pack, lease, or reconciliation state.

#### Scenario: Initialize a behavior mapping
- **WHEN** a caller runs `zpp behave init` in a worktree without `zpp.behave.yaml`
- **THEN** ZPP creates the valid dedicated YAML scaffold through `zpp.behave`, reports provider diagnostics, and creates no OpenLease space or topology

#### Scenario: Preserve an existing mapping
- **WHEN** a caller runs `zpp behave init` with an existing valid version-one mapping
- **THEN** ZPP validates and preserves its root schema and commands while reporting only machine-local provider discovery

#### Scenario: Resolve a declared command
- **WHEN** a caller selects a valid named behavior command
- **THEN** ZPP resolves exactly that declaration through the current `zpp.behave` operation before preparing execution

#### Scenario: Reject an unavailable declaration
- **WHEN** the selected command, target, or gate is absent, duplicated, undeclared, or invalid
- **THEN** ZPP identifies the rejected selection and starts no process or fallback implementation

### Requirement: Closed version-one behavior mapping
The dedicated root mapping SHALL contain only integer `version` and `commands`, and `version` SHALL equal `1`. Each non-empty command identity SHALL declare exactly one closed provider mapping, a non-empty ordered map of targets, and an optional map of gates. Each non-empty target identity SHALL declare a unique non-empty provider `value` within its command and a non-empty list of validated repository-relative `paths`. Unknown fields, absolute paths, escaping paths, invalid repository globs, duplicate provider values, and invalid empty identities or values SHALL be rejected before process creation.

#### Scenario: Accept one closed command declaration
- **WHEN** a version-one document declares one provider and valid ordered targets with unique values and repository-relative paths
- **THEN** ZPP preserves the authored command and target order as the bounded runtime mapping

#### Scenario: Reject an open or unsafe mapping
- **WHEN** a mapping contains an unknown field, escaping path, invalid glob, duplicate target value, or empty required value
- **THEN** validation rejects the complete document before any configured process starts

### Requirement: Repository-owned gate target sets
Each command MAY declare a `gates` mapping from stable, non-empty gate identities to non-empty lists of target identities declared by that same command. A workflow-owned gate SHALL use its packaged skill identity as the gate identity. Gate bindings SHALL contain target identities only and SHALL NOT duplicate target identities or embed provider values. Validation SHALL reject an empty gate, an empty target list, a duplicate target, or a reference to an undeclared target before any configured process starts.

`zpp behave <command> --gate <gate>` SHALL accept exactly one gate identity, resolve its complete binding through the validated selected command, and submit each bound target once in target declaration order. An unknown or invalid gate SHALL fail without falling back to affected or complete execution.

#### Scenario: Validate a command-local gate binding
- **WHEN** a command declares a gate whose non-empty target list refers only to targets declared by that command
- **THEN** ZPP accepts the gate as repository-owned selection policy without copying provider values

#### Scenario: Execute a configured gate
- **WHEN** a caller supplies `--gate` with a valid gate identity declared by the selected command
- **THEN** ZPP submits exactly that gate's targets once each in target declaration order

#### Scenario: Reject an invalid gate binding
- **WHEN** a gate is empty, repeats a target, or refers to a target not declared by its command
- **THEN** validation rejects the mapping and starts no configured process

#### Scenario: Reject an unknown gate selection
- **WHEN** a caller requests a gate not declared by the selected command
- **THEN** ZPP identifies the unknown gate and starts no process or fallback selection

### Requirement: Bounded affected-target filtering
Each named command SHALL declare a closed set of filterable verification targets and repository impact rules. For local execution, `zpp behave` SHALL derive the change from `HEAD` plus staged, unstaged, and untracked non-ignored working-tree paths. For revision execution, the caller SHALL supply comparison base and head together. Unmapped, invalid, or uncertain changed paths SHALL select every target declared by the selected command rather than be treated as unaffected. No changed paths SHALL produce a successful no-target result without starting the provider.

Agents MAY help author or broaden `zpp.behave.yaml`, but runtime selection SHALL remain deterministic from its validated mapping and current repository evidence. Changed paths, agent text, undeclared target names, hook output, and OpenLease configuration metadata SHALL NOT become executable command syntax.

#### Scenario: Filter to declared affected targets
- **WHEN** repository evidence maps the current change conclusively to a proper subset of one selected command's targets
- **THEN** ZPP prepares that command with only the validated affected target values

#### Scenario: Fall back for unknown impact
- **WHEN** any changed path has no conclusive declared impact mapping
- **THEN** ZPP selects every target declared by the named command

#### Scenario: Return without provider execution when nothing changed
- **WHEN** deterministic affected selection observes no changed path
- **THEN** ZPP reports that no target is affected and starts no provider process

#### Scenario: Reject executable agent output
- **WHEN** agent-assisted impact output contains undeclared target or command material
- **THEN** ZPP does not execute that material and reports why it cannot participate

### Requirement: Filtered and complete execution modes
`zpp behave <command>` SHALL use deterministic affected filtering by default. Repeatable `--target` SHALL execute exactly the requested declared target identities, de-duplicate repeated identities, and preserve target declaration order. `--gate` SHALL execute exactly one configured command-local gate target set. Explicit `--all` SHALL execute every target declared by that command without discarding provider-specific cache behavior. Exact target, configured gate, complete, and revision-range affected selection SHALL be mutually exclusive modes. Provider-specific uncached verification SHALL remain a separately declared behavior command rather than a universal flag. `--base` and `--head` SHALL be accepted only together, and `init` SHALL reject every execution-selection option.

#### Scenario: Execute the mapped subset
- **WHEN** a caller selects a valid command without an explicit selection mode and every changed path maps conclusively
- **THEN** ZPP runs only the deterministically affected declared targets

#### Scenario: Execute exact declared targets
- **WHEN** a caller supplies one or more valid exact target identities including a repeat
- **THEN** ZPP submits each selected target once in declaration order

#### Scenario: Execute every declared target
- **WHEN** a caller explicitly supplies `--all`
- **THEN** ZPP submits every target declared by the command to its configured adapter

#### Scenario: Reject ambiguous selection modes
- **WHEN** a caller combines `--target`, `--gate`, `--all`, or a revision range with another selection mode
- **THEN** ZPP rejects the invocation before configuration execution or process creation

#### Scenario: Reject an incomplete revision range
- **WHEN** a caller supplies only one of `--base` or `--head`
- **THEN** ZPP rejects the invocation before configuration execution or process creation

#### Scenario: Reject selection options during initialization
- **WHEN** a caller combines `zpp behave init` with any execution-selection option
- **THEN** ZPP rejects the invocation without initializing or executing the mapping

### Requirement: Typed shell-free target expansion
The `argv` provider SHALL contain `kind: argv` and a typed argv sequence with exactly one `{targets}` expansion position after a non-empty executable. Its adapter SHALL replace that marker with selected target values as distinct argv elements and SHALL start the resulting executable without a command shell. A missing or duplicate marker, a marker executable, an empty or NUL-containing literal, or an empty executable SHALL fail before process creation.

#### Scenario: Expand selected targets as argv
- **WHEN** a valid argv provider selects multiple targets
- **THEN** ZPP inserts each target as one argv value at the declared expansion position and starts the executable without a shell

#### Scenario: Reject an invalid expansion declaration
- **WHEN** an argv provider omits, duplicates, or invalidates its target-expansion position
- **THEN** ZPP identifies the declaration error and starts no process

### Requirement: Explicit behavior provider adapter registry
The `zpp.behave` extension SHALL use an explicit adapter registry keyed by each declaration's `provider.kind`. Current ZPP SHALL register `argv`, `nx`, and `go-task` adapters. A host MAY explicitly supply another conforming adapter when constructing the extension, but ZPP SHALL NOT discover adapters dynamically from installed packages, entry points, executable availability, or configuration. Unknown, duplicate, invalid, or unavailable adapters SHALL fail without selecting another provider.

Every adapter SHALL validate its own closed settings before process creation and SHALL construct one shell-free argv sequence from validated command and target values. OpenLease SHALL treat provider declarations and results as opaque extension values.

Nx SHALL prefer compatible executables in this order: an existing package-local wrapper, an official repository-root wrapper backed by `.nx/installation`, then a PATH executable. ZPP SHALL delegate only to an existing configured Nx project and target surface and SHALL revalidate that surface before execution. The `go-task` adapter SHALL treat selected values as declared Task task names, MAY accept validated literal extra arguments, and SHALL use an explicitly configured or safely discovered repository-local or PATH executable. ZPP SHALL NOT install, download, migrate, connect cloud services, infer a provider, or ask an agent for command text.

#### Scenario: Delegate to configured Nx
- **WHEN** a valid command selects Nx and its repository executable, project, and target surface are available
- **THEN** ZPP delegates only the validated selected targets through the Nx adapter

#### Scenario: Discover a non-JavaScript Nx wrapper
- **WHEN** an Nx workspace has the official repository-root wrapper backed by `.nx/installation` and no package-local wrapper
- **THEN** ZPP discovers that absolute repository-owned wrapper before considering PATH

#### Scenario: Run configured Go Task
- **WHEN** a valid command selects Go Task and its declared task surface and executable are available
- **THEN** ZPP delegates only the validated selected task names and literal settings through the Go Task adapter

#### Scenario: Reject an unavailable provider
- **WHEN** the selected adapter or required repository surface is unavailable
- **THEN** ZPP starts no alternate provider and identifies the unmet requirement

#### Scenario: Keep provider settings opaque to OpenLease
- **WHEN** `zpp.behave` validates a built-in or host-supplied adapter's settings
- **THEN** OpenLease supplies configuration and invocation boundaries without interpreting or executing those settings

### Requirement: Direct operations and opt-in OpenLease cross-checks
ZPP SHALL register `zpp.behave` independently with `initialize` for direct targets and `run` for direct, repository, and cohort targets. It SHALL declare `run` for `RECONCILE_BEFORE_REPOSITORY` in `gate` and `observe` modes, for `RECONCILE_AFTER_REPOSITORY` in `observe` mode, and for `RECONCILE_AFTER_COHORT` in `observe` mode. Registration, configuration presence, and agent hook execution SHALL NOT invoke a behavior operation or select a callback.

The native agent hook SHALL remain limited to repository trait resolution. Explicit `zpp behave init` or `zpp behave <command>` invocation SHALL discover the containing Git worktree, bind its exact dedicated YAML internally, and invoke the selected direct operation without exposing OpenLease coordination concepts to the agent.

A reconciliation callback SHALL require an explicit OpenLease selection identifying its behavior command, complete or affected selection mode, event, mode, and real repository or cohort target. The handler SHALL derive the exact target worktree from that context and reopen its dedicated `zpp.behave.yaml` through invocation-scoped direct binding. It SHALL NOT require an extension-managed behavior configuration source or create another repository registration, space, lease, or topology record.

#### Scenario: Register both ZPP extensions independently
- **WHEN** ZPP constructs its OpenLease host
- **THEN** `zpp.traits` and `zpp.behave` are available as isolated extensions and no handler runs during construction

#### Scenario: Resolve traits without invoking behavior
- **WHEN** an agent-native hook resolves repository traits in a worktree containing `zpp.behave.yaml`
- **THEN** ZPP opens only the required trait documents and starts no behavior operation or repository process

#### Scenario: Invoke behavior without coordination state
- **WHEN** a caller explicitly runs a valid `zpp behave` command from an unregistered worktree
- **THEN** ZPP binds the exact repository YAML and invokes `run` without creating or selecting OpenLease coordination state

#### Scenario: Leave verification inactive when unselected
- **WHEN** `zpp.behave.yaml` exists and compatible callbacks are registered but reconciliation selects none
- **THEN** reconciliation invokes no behavior command

#### Scenario: Cross-check one repository through its direct document
- **WHEN** reconciliation explicitly selects a valid repository callback with complete or affected mode
- **THEN** ZPP reopens that repository's exact root `zpp.behave.yaml` directly and returns its behavior outcome without requiring managed callback configuration

#### Scenario: Observe one cohort with isolated repository context
- **WHEN** reconciliation explicitly selects a valid post-cohort callback with a real target repository context
- **THEN** ZPP runs only the selected repository command policy and returns observational evidence without inventing a blocking state

#### Scenario: Reject incomplete callback policy
- **WHEN** a callback selection omits its behavior command, selection mode, event, mode, or required target context
- **THEN** planning rejects it instead of guessing repository verification policy
