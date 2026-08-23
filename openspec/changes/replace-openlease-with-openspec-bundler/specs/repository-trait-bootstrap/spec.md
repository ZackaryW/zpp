## MODIFIED Requirements

### Requirement: Bounded repository trait documents
ZPP SHALL read existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents and explicitly initialize only one exact requested document through Bundler repository attachments. Operations SHALL preserve Git-root provenance, remain bounded to the worktree, and create no store manifest or lease state.

#### Scenario: Open existing repository trait documents
- **WHEN** a selected worktree contains valid ZPP documents
- **THEN** ZPP reads their exact bytes through repository attachments and owns their decoding

#### Scenario: Initialize one missing repository document
- **WHEN** explicit initialization targets an allowed missing ZPP document
- **THEN** ZPP creates exactly that document without creating coordination state

### Requirement: Invocation-authorized read-only loading
An explicit resolution invocation SHALL authorize read-only Bundler attachment access for repository documents and applicable registered-store `zpp-traits` namespaces. File presence alone SHALL perform no operation, and missing inputs SHALL remain absent.

#### Scenario: Resolve existing inputs without setup
- **WHEN** an explicit resolution targets a Git worktree with existing ZPP inputs
- **THEN** ZPP loads them without a trust, session, or initialization step

### Requirement: Explicit repository mutation authority
ZPP SHALL initialize a repository attachment only from explicit caller intent naming the exact allowed document and SHALL never overwrite an existing winner.

#### Scenario: Reject implicit initialization
- **WHEN** resolution observes a missing repository document without an initialization request
- **THEN** ZPP leaves it absent

### Requirement: Stable public command hierarchy
ZPP SHALL expose root `init`, `sync`, `open`, `reset`, `resolve`, and `behave`; grouped `trait init`; grouped `workflow install|update|remove`; and the minimal `lease` bridge used by the workflow. It SHALL NOT expose `workspace`, sessions, claims, permits, relationship declarations, successors, reconciliation, handoff, cleanup, preparation, or compatibility aliases.

#### Scenario: Inspect the hard-cut command hierarchy
- **WHEN** a caller inspects root and grouped commands
- **THEN** the minimal Bundler-backed hierarchy is present and the complete workspace hierarchy is absent

### Requirement: Lease-free repository operation
Ordinary trait opening, initialization, resolution, and direct behavior verification SHALL remain session-free and lease-free. Store input MAY come only from the selected store's root-to-child chain; siblings and unselected stores SHALL not participate.

#### Scenario: Resolve repository and selected-store input without a lease
- **WHEN** a caller resolves traits for a target in a managed store
- **THEN** ZPP returns repository plus root-to-target store inputs without creating lease state

### Requirement: Bundler attachment and lease authority
Bundler SHALL own bounded raw repository attachment access, exact store namespace selection, provenance, and store lease persistence. ZPP SHALL own TOML/YAML decoding, validation, repository-plus-store-chain composition, initialization payloads, behavior execution, and automatic workflow use of the minimal lease bridge.

#### Scenario: Keep consumer semantics in ZPP
- **WHEN** Bundler returns raw repository bytes or an opaque `zpp-traits` store mapping
- **THEN** ZPP alone validates and composes that input

### Requirement: No compatibility-owned component behavior
ZPP SHALL expose Bundler and Agent Router failures directly and SHALL NOT reproduce OpenLease behavior, translate old state, accept old environment variables or IDs, or fall back to compatibility adapters.

#### Scenario: Propagate a component rejection
- **WHEN** Bundler rejects an attachment or lease operation or Agent Router rejects a projection
- **THEN** ZPP reports that rejection without fallback

## RENAMED Requirements

- FROM: `### Requirement: No-space repository operation`
- TO: `### Requirement: Lease-free repository operation`
- FROM: `### Requirement: OpenLease configuration authority`
- TO: `### Requirement: Bundler attachment and lease authority`
