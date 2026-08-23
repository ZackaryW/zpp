# Behavior Verification Specification

## Purpose

Define repository-owned verification declarations, deterministic affected selection, and explicit shell-free provider execution through direct behavior operations.

## Requirements

### Requirement: Repository-owned named verification
`zpp behave init` SHALL discover the current Git worktree root, then explicitly initialize or validate its root `zpp.behave.yaml` as a dedicated raw Bundler repository attachment owned semantically by ZPP. `zpp behave <command>` SHALL load the same exact document and execute only a valid named command and selected declared targets. Direct initialization and execution SHALL create no session or lease state.

#### Scenario: Initialize a behavior mapping
- **WHEN** a caller runs `zpp behave init` in a worktree without `zpp.behave.yaml`
- **THEN** ZPP creates the valid dedicated YAML scaffold and creates no coordination state

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
Each named command SHALL declare a closed set of filterable verification targets and repository impact rules. Runtime selection SHALL remain deterministic from its validated mapping and current repository evidence. Changed paths, agent text, undeclared target names, hook output, and Bundler attachment metadata SHALL NOT become executable command syntax.

#### Scenario: Filter to declared affected targets
- **WHEN** repository evidence maps the current change conclusively to a proper subset of one selected command's targets
- **THEN** ZPP prepares that command with only the validated affected target values

#### Scenario: Fall back for unknown impact
- **WHEN** any changed path has no conclusive declared impact mapping
- **THEN** ZPP selects every target declared by the named command

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
ZPP SHALL use an explicit behavior adapter registry containing `argv`, `nx`, and `go-task`, validate each closed provider mapping before process creation, and construct shell-free argv. Bundler SHALL provide only exact raw document bytes and provenance; ZPP SHALL own validation and execution and SHALL NOT discover adapters dynamically or ask an agent for command text.

#### Scenario: Delegate to a configured provider
- **WHEN** a valid command selects an available declared provider surface
- **THEN** ZPP delegates only the validated selected targets through that adapter

#### Scenario: Reject an unavailable provider
- **WHEN** the selected adapter or required repository surface is unavailable
- **THEN** ZPP starts no alternate provider and identifies the unmet requirement

### Requirement: Explicit direct behavior operations
ZPP SHALL initialize and execute `zpp.behave.yaml` only through explicit direct `zpp behave` invocations. The native trait hook SHALL remain limited to read-only trait resolution. ZPP SHALL register no OpenLease callback, reconciliation event, repository callback, cohort callback, or compatibility selection, and document presence alone SHALL invoke no verification operation.

#### Scenario: Resolve traits without invoking behavior
- **WHEN** an agent-native hook resolves repository traits in a worktree containing `zpp.behave.yaml`
- **THEN** ZPP opens only the required trait inputs and starts no behavior operation or repository process

#### Scenario: Invoke behavior without coordination state
- **WHEN** a caller explicitly runs a valid `zpp behave` command from a Git worktree
- **THEN** ZPP reads the exact repository YAML and invokes the command without creating lease state

#### Scenario: Leave verification inactive when unselected
- **WHEN** `zpp.behave.yaml` exists but no `zpp behave` command is invoked
- **THEN** ZPP runs no behavior command
