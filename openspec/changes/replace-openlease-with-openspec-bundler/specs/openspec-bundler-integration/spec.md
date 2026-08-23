## Purpose

Defines ZPP's breaking replacement of OpenLease with raw Bundler attachments and UUID-addressed atomic store lease bundles while ZPP retains ownership of its schemas and workflow behavior.

## ADDED Requirements

### Requirement: Use OpenSpec Bundler without an OpenLease compatibility surface
ZPP SHALL use `openspec-bundler` as its attachment and store-lease dependency and SHALL NOT import or invoke OpenLease, read or convert OpenLease state, accept OpenLease environment variables or identifiers, expose compatibility aliases, or silently translate old configuration.

#### Scenario: Start without OpenLease state migration
- **WHEN** ZPP runs after the dependency cutover while prior OpenLease state exists under the selected product home
- **THEN** ZPP ignores that state, performs no conversion or deletion, and uses only its new Bundler-owned state boundary

### Requirement: Own ZPP attachment schemas and composition
ZPP SHALL load raw repository documents and exact store namespaces through Bundler, SHALL address its store namespace as the bare key `zpp-traits` declared by `[extensions.zpp-traits]`, and SHALL own all TOML or YAML parsing, validation, initialization payloads, precedence, and execution. Store composition SHALL follow only the selected store's root-to-child chain and SHALL exclude siblings.

#### Scenario: Compose a selected store without its sibling
- **WHEN** a monorepo repository input and related parent, selected-child, and sibling stores declare ZPP inputs
- **THEN** ZPP composes the repository, parent, and selected-child inputs in order and excludes the sibling input

### Requirement: Keep read-only resolution session-free
ZPP SHALL resolve repository and store attachment inputs without creating a session, space, claim, permit, or lease. The automatic trait hook SHALL perform only this read-only resolution under the `zpp-traits` identity.

#### Scenario: Resolve traits without coordination state
- **WHEN** an agent requests ordinary read-only trait resolution in a Git worktree
- **THEN** ZPP returns the resolved traits without creating session or lease state

### Requirement: Automatically hold atomic store bundles through archival completion
Before governed OpenSpec mutation, `zpp-workflow` SHALL automatically acquire one atomic Bundler lease bundle for its durable owner identity and exact store/change members. A parent member SHALL use Bundler's descendant closure, and independent related members SHALL be requested as explicit multi-roots without a dependency edge. ZPP SHALL surface conflicts before mutation, audit changed OpenSpec paths, record each successful member archive, and complete the bundle only after every member is archived; explicitly authorized bundle abandonment SHALL be the only recovery release.

#### Scenario: Retain a multi-store bundle until every change archives
- **WHEN** one workflow acquires multiple requested store/change members and archives only a proper subset
- **THEN** ZPP retains the complete bundle until every member archives and completion is explicit

#### Scenario: Acquire automatically before governed mutation
- **WHEN** a workflow with exact store/change members is ready to begin governed OpenSpec mutation
- **THEN** ZPP acquires the current Bundler bundle without a session, claim, preview, separate go-ahead, permit, or workspace command

### Requirement: Expose a minimal Bundler lease bridge
ZPP SHALL expose only the Bundler lease operations required by its automatic workflow: acquire exact store/change members for a durable owner, audit changed OpenSpec paths, record one member archive, complete an all-archived bundle, inspect retained bundles for recovery, and owner-authorized abandonment. The bridge SHALL expose Bundler UUIDs and bundle results directly and SHALL NOT reproduce OpenLease workspace terminology or operations.

#### Scenario: Drive a workflow bundle through the minimal bridge
- **WHEN** the workflow acquires exact members, audits its changed paths, records every archive, and completes the bundle
- **THEN** ZPP delegates those operations to Bundler without creating any additional coordination model

### Requirement: Remove the OpenLease workspace surface
ZPP SHALL NOT expose the `workspace` command group, package `zpp-workspace-management`, create successor or reconciliation state, record handoff dispositions, manage generated worktrees, repair preparation, or declare dependency relationships. It SHALL use only Bundler parent containment and explicit multi-root bundle requests and SHALL provide no aliases for the removed surface.

#### Scenario: Inspect the hard-cut public surface
- **WHEN** a caller inspects ZPP commands, packaged skills, hooks, and coordination state after cutover
- **THEN** no OpenLease workspace lifecycle or compatibility identity is present
