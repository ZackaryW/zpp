## MODIFIED Requirements

### Requirement: Bounded repository trait documents
ZPP SHALL open an existing `.zpp/zpp.toml` context document or existing `.zpp/traits/{name}.toml` one-family trait documents, and SHALL explicitly initialize only an exact requested document, through OpenLease's invocation-scoped direct document contract with the selected repository path as provenance. These document operations SHALL NOT themselves create a persistent configuration-source record, declare a relationship, or acquire a permit. Establishing a session for the repository SHALL register the repository and its worktree-covering authority as specified by the session lifecycle capability, and document binding SHALL remain invocation-scoped whether or not a session is established.

#### Scenario: Bind documents through the direct contract
- **WHEN** ZPP receives an eligible repository path containing `.zpp/zpp.toml` and `.zpp/traits/bdd.toml`
- **THEN** OpenLease returns invocation-scoped bound documents with repository-path provenance and creates no persistent configuration-source record

#### Scenario: Initialize the exact missing document
- **WHEN** an authorized initialization targets an absent `.zpp/traits/bdd.toml` within its permitted repository boundary
- **THEN** OpenLease initializes exactly that document without declaring a relationship or acquiring a permit

### Requirement: No-space repository operation
Ordinary repository trait opening, initialization, and resolution and direct `zpp behave init` or execution SHALL NOT require a declared affected claim, evaluate lockability, or acquire, hold, or release a permit. These operations SHALL run under the session ZPP establishes for the worktree and SHALL remain available as read-only work. An explicitly selected space MAY supply additional trait context or a real reconciliation callback context, and its lifecycle SHALL remain independent from baseline repository trait availability and direct behavior verification.

#### Scenario: Resolve repository traits without a permit
- **WHEN** a repository resolves its trait documents under an established session
- **THEN** ZPP resolves the bounded repository context without requiring a declared affected claim or acquiring a permit

#### Scenario: Run repository behavior without a permit
- **WHEN** a Git worktree invokes `zpp behave` against its dedicated root mapping
- **THEN** ZPP uses an invocation-scoped direct document binding without requiring a declared affected claim or acquiring a permit

### Requirement: Invocation-authorized read-only loading
An explicit workflow invocation against a selected repository SHALL authorize ZPP to request read-only OpenLease direct bindings for existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents in that repository. File presence without such an invocation SHALL perform no operation, establish no session, and register no topology. Missing repository documents SHALL NOT be created implicitly and SHALL leave available space and global trait contributions eligible for resolution.

#### Scenario: Read existing traits during workflow invocation
- **WHEN** a user invokes the workflow against a repository containing `.zpp/traits/bdd.toml`
- **THEN** ZPP reads that document through an invocation-scoped OpenLease binding without requiring a separate trust or initialization step

#### Scenario: Do nothing before invocation
- **WHEN** a repository contains ZPP trait documents but no workflow or trait command targets it
- **THEN** ZPP does not open, evaluate, register, establish a session for, or mutate those documents
