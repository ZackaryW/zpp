## ADDED Requirements

### Requirement: Bounded repository trait documents
ZPP SHALL open an existing `.zpp/zpp.toml` context document or existing `.zpp/traits/{name}.toml` one-family trait documents, and SHALL explicitly initialize only an exact requested document, through OpenLease's invocation-scoped direct document contract with the selected repository path as provenance. These operations SHALL NOT require durable OpenLease repository registration or create a persistent configuration-source record.

#### Scenario: Open an unregistered repository document
- **WHEN** ZPP receives an eligible unregistered repository path containing `.zpp/zpp.toml` and `.zpp/traits/bdd.toml`
- **THEN** OpenLease returns invocation-scoped bound documents with repository-path provenance and no registration mutation

#### Scenario: Initialize the exact missing document
- **WHEN** an authorized initialization targets an absent `.zpp/traits/bdd.toml` within its permitted repository boundary
- **THEN** OpenLease initializes exactly that document without creating repository topology or a persistent source binding

### Requirement: Invocation-authorized read-only loading
An explicit workflow invocation against a selected repository SHALL authorize ZPP to request read-only OpenLease direct bindings for existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents in that repository. File presence without such an invocation SHALL perform no operation. Missing repository documents SHALL NOT be created implicitly and SHALL leave available space and global trait contributions eligible for resolution.

#### Scenario: Read existing traits during workflow invocation
- **WHEN** a user invokes the workflow against a repository containing `.zpp/traits/bdd.toml`
- **THEN** ZPP reads that document through an invocation-scoped OpenLease binding without requiring a separate trust, initialization, registration, or space-selection step

#### Scenario: Do nothing before invocation
- **WHEN** a repository contains ZPP trait documents but no workflow or trait command targets it
- **THEN** ZPP does not open, evaluate, register, or mutate those documents

#### Scenario: Fall through when repository traits are absent
- **WHEN** a workflow invocation targets a repository without `.zpp/traits/bdd.toml`
- **THEN** ZPP performs no implicit creation and may resolve `bdd` from available space and global contributions

### Requirement: Explicit repository mutation authority
Creating or modifying `.zpp/zpp.toml` or `.zpp/traits/{name}.toml` SHALL require grouped `zpp trait init` to identify the intended exact context or trait-family document and repository target. Root `zpp init` SHALL retain agent setup selection rather than becoming an ambiguous repository-document mutation. Workflow invocation and read-only resolution SHALL NOT themselves authorize a write.

#### Scenario: Refuse implicit initialization
- **WHEN** workflow resolution encounters a missing repository trait document
- **THEN** ZPP leaves it absent instead of initializing it as a side effect

#### Scenario: Initialize through an explicit command
- **WHEN** a user explicitly requests initialization of `.zpp/traits/bdd.toml` for the selected repository
- **THEN** ZPP may request OpenLease's bounded initialization for exactly that document

### Requirement: Stable public command hierarchy
ZPP SHALL export its Typer application as `zpp.cli:app`, retain root `init` and `resolve` commands, add exact repository initialization as grouped `trait init`, and retain the `workflow install`, `workflow update`, and `workflow remove` command group. Trait explanations SHALL be requested as part of `resolve`, and workflow lifecycle SHALL NOT be exposed as a flat `install-workflow` command. The commands SHALL delegate configuration and projection operations to OpenLease and Agent Router rather than exposing a mirrored OpenLease space lifecycle.

#### Scenario: Inspect command help
- **WHEN** a user opens ZPP command help
- **THEN** root `init` and `resolve`, grouped `trait init`, and grouped `workflow install|update|remove` are present, while flat `init-trait`, flat `install-workflow`, standalone `explain`, and mirrored `space` commands are absent

#### Scenario: Explain one resolution
- **WHEN** a user resolves a target with the explanation option
- **THEN** the same side-effect-free resolution operation emits its source, policy, flavor, facet, and evidence decisions without changing the selected bodies

### Requirement: Typed agent selection behavior
ZPP CLI commands SHALL use Agent Router's `Agent` type as the supported agent identity. Commands accepting multiple agents SHALL accept repeatable explicit values, preserve first-seen request order, and deduplicate repeats. When such a command requires selection and receives no explicit value, it SHALL prompt on an interactive terminal in Codex, Claude Code, Pi, Kimi order and SHALL abort without mutation if cancelled; the same omission SHALL fail in noninteractive use. `resolve --agent` SHALL remain optional and SHALL accept at most one invoking agent.

#### Scenario: Select several agents explicitly
- **WHEN** a user repeats `--agent` with supported agent values including a duplicate
- **THEN** the command operates once per distinct agent in first-requested order

#### Scenario: Select agents interactively
- **WHEN** a multi-agent lifecycle command requires agents, receives none, and has an interactive terminal
- **THEN** ZPP offers Codex, Claude Code, Pi, and Kimi in that order and performs no mutation when selection is cancelled

#### Scenario: Require explicit agents noninteractively
- **WHEN** a multi-agent lifecycle command requires agents, receives none, and has no interactive terminal
- **THEN** ZPP reports that one or more `--agent` values are required

#### Scenario: Restrict resolution to one invoking agent
- **WHEN** `resolve` receives more than one `--agent` value
- **THEN** ZPP rejects the request instead of combining several invoking-agent artifact contexts

### Requirement: No-space repository operation
Ordinary repository trait opening, initialization, and resolution SHALL NOT create, select, lock, or require an OpenLease space. An explicitly selected space MAY supply additional OpenLease context, but its lifecycle SHALL remain independent from baseline repository trait availability.

#### Scenario: Resolve repository traits without a space
- **WHEN** an unregistered repository uses its direct trait document without explicit space selection
- **THEN** ZPP resolves the bounded repository context without creating or selecting a space

### Requirement: OpenLease configuration authority
OpenLease SHALL remain the owner of direct document binding, codec/layout handling, repository-path provenance, bounded initialization, and managed writes. ZPP SHALL own only the `zpp.traits` schemas and semantic resolution of the context and one-family trait documents supplied through that binding.

#### Scenario: Consume an exact direct context
- **WHEN** OpenLease supplies bound `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents with the selected repository path
- **THEN** ZPP consumes those exact invocation documents without creating topology or a compatibility-owned configuration record

### Requirement: Agent Router discovery and projection authority
Agent Router SHALL remain the owner of supported agent/plugin discovery, effective artifact selection, destination resolution, ownership inspection, installation, update, and removal. ZPP SHALL register trait artifact semantics and provide its workflow asset without independently scanning or mutating agent destinations.

#### Scenario: Project the consolidated workflow skill
- **WHEN** a user installs the ZPP workflow integration for a supported agent
- **THEN** ZPP asks Agent Router to project the asset and does not write the destination directly

### Requirement: No compatibility-owned component behavior
ZPP SHALL NOT implement a compatibility path that reproduces OpenLease coordination/configuration or Agent Router discovery/projection. Failure or rejection from either component SHALL remain visible rather than falling back to a ZPP-owned substitute.

#### Scenario: Preserve a component rejection
- **WHEN** OpenLease rejects a direct document operation or Agent Router rejects a conflicting projection
- **THEN** ZPP reports that component result and performs no legacy fallback mutation
