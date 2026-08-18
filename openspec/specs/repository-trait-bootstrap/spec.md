# Repository Trait Bootstrap Specification

## Purpose

Define direct repository trait use, explicit initialization, stable commands, and component-owned integration.

## Requirements

### Requirement: Bounded repository trait documents
ZPP SHALL open an existing `.zpp/zpp.toml` context document or existing `.zpp/traits/{name}.toml` one-family trait documents, and SHALL explicitly initialize only an exact requested document, through OpenLease's invocation-scoped direct document contract with the selected repository path as provenance. These document operations SHALL NOT themselves create a persistent configuration-source record, declare a relationship, or acquire a permit. Establishing a session for the repository SHALL register the repository and its worktree-covering authority as specified by the session lifecycle capability, and document binding SHALL remain invocation-scoped whether or not a session is established.

#### Scenario: Bind documents through the direct contract
- **WHEN** ZPP receives an eligible repository path containing `.zpp/zpp.toml` and `.zpp/traits/bdd.toml`
- **THEN** OpenLease returns invocation-scoped bound documents with repository-path provenance and creates no persistent configuration-source record

#### Scenario: Initialize the exact missing document
- **WHEN** an authorized initialization targets an absent `.zpp/traits/bdd.toml` within its permitted repository boundary
- **THEN** OpenLease initializes exactly that document without declaring a relationship or acquiring a permit

### Requirement: Invocation-authorized read-only loading
An explicit workflow invocation against a selected repository SHALL authorize ZPP to request read-only OpenLease direct bindings for existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents in that repository. File presence without such an invocation SHALL perform no operation, establish no session, and register no topology. Missing repository documents SHALL NOT be created implicitly and SHALL leave available space and global trait contributions eligible for resolution.

#### Scenario: Read existing traits during workflow invocation
- **WHEN** a user invokes the workflow against a repository containing `.zpp/traits/bdd.toml`
- **THEN** ZPP reads that document through an invocation-scoped OpenLease binding without requiring a separate trust or initialization step

#### Scenario: BDD target — Do nothing before an invocation targets the repository
- **WHEN** executable behavior is covered by `features/repository_trait_bootstrap/repository_trait_bootstrap.feature::Do nothing before an invocation targets the repository`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Explicit repository mutation authority
Creating or modifying `.zpp/zpp.toml` or `.zpp/traits/{name}.toml` SHALL require grouped `zpp trait init` to identify the intended exact context or trait-family document and repository target. Root `zpp init` SHALL retain agent setup selection rather than becoming an ambiguous repository-document mutation. Workflow invocation and read-only resolution SHALL NOT themselves authorize a write.

#### Scenario: Refuse implicit initialization
- **WHEN** workflow resolution encounters a missing repository trait document
- **THEN** ZPP leaves it absent instead of initializing it as a side effect

#### Scenario: Initialize through an explicit command
- **WHEN** a user explicitly requests initialization of `.zpp/traits/bdd.toml` for the selected repository
- **THEN** ZPP may request OpenLease's bounded initialization for exactly that document

### Requirement: Stable public command hierarchy
ZPP SHALL export its Typer application as `zpp.cli:app`; expose root `init`, `open`, `reset`, `resolve`, and `behave COMMAND` with reserved `behave init`; provide exact repository initialization as grouped `trait init`; and retain the `workflow install`, `workflow update`, and `workflow remove` command group. `reset` SHALL require explicit confirmation according to the product-home lifecycle contract. `behave COMMAND` SHALL accept `--all`, repeatable `--target`, `--gate`, and paired `--base` and `--head` according to the behavior-verification selection contract. Trait explanations SHALL be requested as part of `resolve`, and workflow lifecycle SHALL NOT be exposed as a flat `install-workflow` command. The commands SHALL delegate configuration and projection operations to OpenLease and Agent Router rather than exposing a mirrored OpenLease space lifecycle.

Root `--path` SHALL identify the selected ZPP home. ZPP SHALL derive its OpenLease state root as the selected home's `openlease` child rather than accepting the product home and component state root as the same directory.

#### Scenario: Inspect command help
- **WHEN** a user opens ZPP command help
- **THEN** root `init`, `open`, `reset`, `resolve`, and `behave COMMAND`, grouped `trait init`, and grouped `workflow install|update|remove` are present, while flat `init-trait`, flat `install-workflow`, standalone `explain`, and mirrored `space` commands are absent

#### Scenario: Explain one resolution
- **WHEN** a user resolves a target with the explanation option
- **THEN** the same side-effect-free resolution operation emits its source, policy, flavor, facet, and evidence decisions without changing the selected bodies

#### Scenario: Inspect behavior selection help
- **WHEN** a user inspects `zpp behave --help`
- **THEN** the command documents its command-or-init argument and complete, exact-target, gate, and paired-revision selection options

#### Scenario: Route through one selected home
- **WHEN** a caller supplies root `--path` and invokes an OpenLease-backed command
- **THEN** ZPP passes the selected home's exact `openlease` child to OpenLease and does not reinterpret the command target as the state root

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
Ordinary repository trait opening, initialization, and resolution and direct `zpp behave init` or execution SHALL NOT require a declared affected claim, evaluate lockability, or acquire, hold, or release a permit. These operations SHALL run under the session ZPP establishes for the worktree and SHALL remain available as read-only work. An explicitly selected space MAY supply additional trait context or a real reconciliation callback context, and its lifecycle SHALL remain independent from baseline repository trait availability and direct behavior verification.

#### Scenario: BDD target — Resolve repository traits without a permit
- **WHEN** executable behavior is covered by `features/repository_trait_bootstrap/repository_trait_bootstrap.feature::Resolve repository traits without a permit`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Run direct repository behavior without a permit
- **WHEN** executable behavior is covered by `features/repository_trait_bootstrap/repository_trait_bootstrap.feature::Run direct repository behavior without a permit`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: OpenLease configuration authority
OpenLease SHALL remain the owner of direct document binding, codec and layout handling, repository-path provenance, bounded initialization, managed writes, and explicit extension invocation and callback boundaries. ZPP SHALL own the `zpp.traits` schemas and semantic resolution of context and one-family trait documents and the independent `zpp.behave` version-one schema, deterministic selection, and provider execution supplied through those bindings. The dedicated root `zpp.behave.yaml` SHALL be bound wholly to `zpp.behave` without a namespace wrapper.

#### Scenario: Consume an exact direct trait context
- **WHEN** OpenLease supplies bound `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents with the selected repository path
- **THEN** ZPP consumes those exact invocation documents without creating topology or a compatibility-owned configuration record

#### Scenario: Consume an exact behavior mapping
- **WHEN** OpenLease supplies the repository-root dedicated YAML document to `zpp.behave`
- **THEN** ZPP receives root-level `version` and `commands`, validates their behavior semantics, and adds no extension wrapper or compatibility record

### Requirement: Agent Router discovery and projection authority
Agent Router SHALL remain the owner of supported agent/plugin discovery, effective artifact selection, destination resolution, ownership inspection, skill and hook installation, explicit project skill update, and removal. ZPP SHALL construct Agent Router with the actual user home and the selected repository as project context, register trait artifact semantics, and provide its packaged workflow skill and per-agent hook without independently scanning or mutating agent destinations. One resolution SHALL consume plugin traits only from the explicitly invoking agent's effective active `zpp.traits` artifacts.

#### Scenario: Project the complete workflow integration
- **WHEN** a user installs the ZPP workflow integration for a supported agent
- **THEN** ZPP asks that agent's Agent Router to project the consolidated skill and native hook and does not write either destination directly

#### Scenario: Discover invoking-agent plugin traits
- **WHEN** `resolve --agent codex` targets a repository and Codex has active user or project plugins providing `zpp.traits`
- **THEN** ZPP resolves those active artifacts using the router's home-rooted state and does not combine another agent's plugin context

#### Scenario: Explicitly update a project skill
- **WHEN** a user invokes project-scoped `workflow update` for a selected agent and repository
- **THEN** ZPP uses Agent Router's explicit project `update_skill` operation for the consolidated skill and its owned hook lifecycle for the hook

#### Scenario: Maintain a user integration safely
- **WHEN** a user installs or updates the user-scoped workflow integration
- **THEN** ZPP uses Agent Router's ownership-safe install reconciliation for the skill and hook

### Requirement: No compatibility-owned component behavior
ZPP SHALL NOT implement a compatibility path that reproduces OpenLease coordination/configuration or Agent Router discovery/projection. Failure or rejection from either component SHALL remain visible rather than falling back to a ZPP-owned substitute.

#### Scenario: Preserve a component rejection
- **WHEN** OpenLease rejects a direct document operation or Agent Router rejects a conflicting projection
- **THEN** ZPP reports that component result and performs no legacy fallback mutation
