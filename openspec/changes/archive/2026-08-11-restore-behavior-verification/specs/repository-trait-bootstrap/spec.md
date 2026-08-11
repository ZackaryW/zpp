## MODIFIED Requirements

### Requirement: Stable public command hierarchy
ZPP SHALL export its Typer application as `zpp.cli:app`, retain root `init` and `resolve` commands, add exact repository initialization as grouped `trait init`, restore root `behave COMMAND` with reserved `behave init`, and retain the `workflow install`, `workflow update`, and `workflow remove` command group. `behave COMMAND` SHALL accept `--all`, repeatable `--target`, `--gate`, and paired `--base` and `--head` according to the behavior-verification selection contract. Trait explanations SHALL be requested as part of `resolve`, and workflow lifecycle SHALL NOT be exposed as a flat `install-workflow` command. The commands SHALL delegate configuration and projection operations to OpenLease and Agent Router rather than exposing a mirrored OpenLease space lifecycle.

#### Scenario: Inspect command help
- **WHEN** a user opens ZPP command help
- **THEN** root `init`, `resolve`, and `behave COMMAND`, grouped `trait init`, and grouped `workflow install|update|remove` are present, while flat `init-trait`, flat `install-workflow`, standalone `explain`, and mirrored `space` commands are absent

#### Scenario: Explain one resolution
- **WHEN** a user resolves a target with the explanation option
- **THEN** the same side-effect-free resolution operation emits its source, policy, flavor, facet, and evidence decisions without changing the selected bodies

#### Scenario: Inspect behavior selection help
- **WHEN** a user inspects `zpp behave --help`
- **THEN** the command documents its command-or-init argument and complete, exact-target, gate, and paired-revision selection options

### Requirement: No-space repository operation
Ordinary repository trait opening, initialization, and resolution and direct `zpp behave init` or execution SHALL NOT create, select, lock, or require an OpenLease space. An explicitly selected space MAY supply additional trait context or a real reconciliation callback context, but its lifecycle SHALL remain independent from baseline repository trait availability and direct behavior verification.

#### Scenario: Resolve repository traits without a space
- **WHEN** an unregistered repository uses its direct trait document without explicit space selection
- **THEN** ZPP resolves the bounded repository context without creating or selecting a space

#### Scenario: Run repository behavior without a space
- **WHEN** an unregistered Git worktree invokes `zpp behave` against its dedicated root mapping
- **THEN** ZPP uses an invocation-scoped direct document binding without creating or selecting a space

### Requirement: OpenLease configuration authority
OpenLease SHALL remain the owner of direct document binding, codec and layout handling, repository-path provenance, bounded initialization, managed writes, and explicit extension invocation and callback boundaries. ZPP SHALL own the `zpp.traits` schemas and semantic resolution of context and one-family trait documents and the independent `zpp.behave` version-one schema, deterministic selection, and provider execution supplied through those bindings. The dedicated root `zpp.behave.yaml` SHALL be bound wholly to `zpp.behave` without a namespace wrapper.

#### Scenario: Consume an exact direct trait context
- **WHEN** OpenLease supplies bound `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents with the selected repository path
- **THEN** ZPP consumes those exact invocation documents without creating topology or a compatibility-owned configuration record

#### Scenario: Consume an exact behavior mapping
- **WHEN** OpenLease supplies the repository-root dedicated YAML document to `zpp.behave`
- **THEN** ZPP receives root-level `version` and `commands`, validates their behavior semantics, and adds no extension wrapper or compatibility record
