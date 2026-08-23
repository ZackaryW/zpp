# OpenSpec Bundler Integration Specification

## Purpose

Defines ZPP's breaking replacement of OpenLease with raw Bundler attachments and UUID-addressed atomic store lease bundles while ZPP retains ownership of its schemas and workflow behavior.

## Requirements

### Requirement: Use OpenSpec Bundler without an OpenLease compatibility surface
ZPP SHALL use `openspec-bundler` as its attachment and store-lease dependency and SHALL NOT import or invoke OpenLease, read or convert OpenLease state, accept OpenLease environment variables or identifiers, expose compatibility aliases, or silently translate old configuration.

#### Scenario: BDD target — Ignore legacy state while using the Bundler state boundary
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Ignore legacy state while using the Bundler state boundary`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Own ZPP attachment schemas and composition
ZPP SHALL load raw repository documents and exact store namespaces through Bundler, SHALL address its store namespace as the bare key `zpp-traits` declared by `[extensions.zpp-traits]`, and SHALL own all TOML or YAML parsing, validation, initialization payloads, precedence, and execution. Store composition SHALL follow only the selected store's root-to-child chain and SHALL exclude siblings.

#### Scenario: BDD target — Compose repository and selected-store inputs without a sibling
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Compose repository and selected-store inputs without a sibling`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Keep read-only resolution session-free
ZPP SHALL resolve repository and store attachment inputs without creating a session, space, claim, permit, or lease. The automatic trait hook SHALL perform only this read-only resolution under the `zpp-traits` identity.

#### Scenario: Resolve traits without coordination state
- **WHEN** an agent requests ordinary read-only trait resolution in a Git worktree
- **THEN** ZPP returns the resolved traits without creating session or lease state

### Requirement: Automatically hold atomic store bundles through archival completion
Before governed OpenSpec mutation, the active mutation-authorized complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) or a directly invoked mutating `zpps-*` component SHALL request `zpps-workflow-kernel` to acquire one atomic Bundler lease bundle for its durable owner identity and exact registered store UUID/change members. A parent member SHALL use Bundler's descendant closure, and independent related members SHALL be requested as explicit multi-roots without a dependency edge. ZPP SHALL surface conflicts before mutation, audit changed OpenSpec paths, record each successful member archive, and complete the bundle only after every member is archived; explicitly authorized bundle abandonment SHALL be the only recovery release. Neither the kernel nor a component SHALL select workflow continuation or expand the acquired member set.

#### Scenario: BDD target — Retain an automatic bundle until every change archives
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Retain an automatic bundle until every change archives`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Acquire automatically before governed OpenSpec mutation
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Acquire automatically before governed OpenSpec mutation`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Expose a minimal Bundler lease bridge
ZPP SHALL expose only the Bundler lease operations required by its automatic workflow: acquire exact store/change members for a durable owner, audit changed OpenSpec paths, record one member archive, complete an all-archived bundle, inspect retained bundles for recovery, and owner-authorized abandonment. The bridge SHALL expose Bundler UUIDs and bundle results directly and SHALL NOT reproduce OpenLease workspace terminology or operations.

#### Scenario: Drive a workflow bundle through the minimal bridge
- **WHEN** the workflow acquires exact members, audits its changed paths, records every archive, and completes the bundle
- **THEN** ZPP delegates those operations to Bundler without creating any additional coordination model

### Requirement: Remove the OpenLease workspace surface
ZPP SHALL NOT expose the `workspace` command group, package `zpp-workspace-management`, create successor or reconciliation state, record handoff dispositions, manage generated worktrees, repair preparation, or declare dependency relationships. It SHALL use only Bundler parent containment and explicit multi-root bundle requests and SHALL provide no aliases for the removed surface.

#### Scenario: BDD target — Expose no OpenLease workspace compatibility surface
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Expose no OpenLease workspace compatibility surface`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
