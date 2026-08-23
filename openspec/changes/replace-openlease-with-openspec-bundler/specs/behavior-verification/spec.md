## MODIFIED Requirements

### Requirement: Repository-owned named verification
`zpp behave init` SHALL discover the current Git worktree root, then explicitly initialize or validate its root `zpp.behave.yaml` as a dedicated raw Bundler repository attachment owned semantically by ZPP. `zpp behave <command>` SHALL load the same exact document and execute only a valid named command and selected declared targets. Direct initialization and execution SHALL create no session or lease state.

#### Scenario: Initialize a behavior mapping
- **WHEN** a caller runs `zpp behave init` in a worktree without `zpp.behave.yaml`
- **THEN** ZPP creates the valid dedicated YAML scaffold and creates no coordination state

#### Scenario: Reject an unavailable declaration
- **WHEN** the selected command, target, or gate is absent, duplicated, undeclared, or invalid
- **THEN** ZPP identifies the rejected selection and starts no process or fallback implementation

### Requirement: Bounded affected-target filtering
Each named command SHALL declare a closed set of filterable verification targets and repository impact rules. Runtime selection SHALL remain deterministic from its validated mapping and current repository evidence. Changed paths, agent text, undeclared target names, hook output, and Bundler attachment metadata SHALL NOT become executable command syntax.

#### Scenario: Filter to declared affected targets
- **WHEN** repository evidence maps the current change conclusively to a proper subset of one selected command's targets
- **THEN** ZPP prepares that command with only the validated affected target values

#### Scenario: Fall back for unknown impact
- **WHEN** any changed path has no conclusive declared impact mapping
- **THEN** ZPP selects every target declared by the named command

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

## RENAMED Requirements

- FROM: `### Requirement: Direct operations and opt-in OpenLease cross-checks`
- TO: `### Requirement: Explicit direct behavior operations`
