## Purpose

Provides an explicit and visibly warned one-command escape hatch when an owner deliberately authorizes execution without ZPP's normal Bundler coordination.

## ADDED Requirements

### Requirement: Scope unleased bypass to one explicit command
ZPP SHALL expose a bypass command that requires an explicit reason and affirmative acknowledgement, runs exactly one supplied child command with coordination bypass active only in that child environment, and returns the child command's exit status. Ordinary environment overrides SHALL NOT activate bypass, and bypass state SHALL NOT persist in the selected product home, repository, or later commands.

#### Scenario: BDD target — Warn and scope one acknowledged bypass command
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Scope unleased bypass to one explicit command","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Warn and scope one acknowledged bypass command"}`
- **THEN** executable acceptance authority is `features/workflow_coordination_bypass/workflow_coordination_bypass.feature::Warn and scope one acknowledged bypass command`

#### Scenario: BDD target — Reject bypass without complete authorization
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Scope unleased bypass to one explicit command","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Reject bypass without complete authorization"}`
- **THEN** executable acceptance authority is `features/workflow_coordination_bypass/workflow_coordination_bypass.feature::Reject bypass without complete authorization`

### Requirement: Make bypass execution unmistakable
Before starting the child command, ZPP SHALL emit a prominent warning to standard error identifying that Bundler coordination is bypassed, the supplied reason, and the exact child command. The child environment SHALL contain a runtime-recognized bypass marker, and every ZPP governed-mutation entry reached inside that child SHALL emit structured bypass state rather than claiming that a lease was acquired.

#### Scenario: BDD target — Report warned structured bypass state
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Make bypass execution unmistakable","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Report warned structured bypass state"}`
- **THEN** executable acceptance authority is `features/workflow_coordination_bypass/workflow_coordination_bypass.feature::Report warned structured bypass state`

### Requirement: Preserve authority and verification boundaries during bypass
Bypass SHALL waive only Bundler registration, manifest, owner, and lease enforcement for the scoped child process. It SHALL NOT grant mutation, archive, abandonment, checkpoint, product-decision, verification, or lifecycle-completion authority, and it SHALL NOT suppress repository validation or genuine command failures.

#### Scenario: Refuse to treat bypass as broader authority
- **WHEN** a bypassed workflow lacks a required mutation, archive, checkpoint, or product decision
- **THEN** the owning workflow boundary remains blocked even though Bundler coordination is bypassed
