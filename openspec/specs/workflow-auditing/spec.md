# Workflow Auditing Specification

## Purpose

Provide maintainers with an interactive local audit that runs a synthetic OpenSpec change through every complete ZPP workflow, identifies design-to-implementation gaps, and drives each finding to an explicit closeout state.

## Requirements

### Requirement: Create a disposable Git and OpenSpec audit workspace
The workflow audit SHALL derive its audit set from the repository's validated packaged complete-workflow contract inventory. For every discovered complete workflow it SHALL assign one distinct subagent that creates a fresh empty temporary Git repository, initializes a local OpenSpec root without projecting agent tools, creates a synthetic change appropriate to that workflow, and uses a unique temporary ZPP product home. It SHALL NOT maintain a separate fixed workflow list, reuse a workspace or subagent across workflows, mutate the caller's product home, or register the disposable OpenSpec root in a persistent store.

#### Scenario: BDD target — Initialize an empty Git and OpenSpec audit repository
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Create a disposable Git and OpenSpec audit workspace","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Initialize an empty Git and OpenSpec audit repository"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Initialize an empty Git and OpenSpec audit repository`

### Requirement: Run one complete mock sequence per workflow
Each workflow subagent SHALL start its assigned workflow against the disposable repository and drive the synthetic change through every declared stage in order. At each transition it SHALL inspect the playbook's custom instruction and branches, construct a bounded mock result from the selected component contract, check and record that result through the real workflow reminder CLI, and retain exact inputs, outputs, branch decisions, and OpenSpec state. It SHALL exercise applicable planning, synchronization, verification, finalization, and archive branches and SHALL continue past resolvable fixture deficiencies until the workflow reaches a closed reminder and archived synthetic change or a truthful workflow blocker.

#### Scenario: BDD target — Close every declared workflow through a mock change
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Run one complete mock sequence per workflow","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Close every declared workflow through a mock change"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Close every declared workflow through a mock change`

### Requirement: Reconcile gaps against design and implementation
Each workflow audit SHALL compare every mock transition with the workflow's JSON stage contract, playbook-specific Markdown configuration and branches, referenced component contracts and skills, workflow CLI and kernel behavior, canonical OpenSpec requirements, capability BDD, and focused Python tests. It SHALL maintain a gap ledger that distinguishes a disposable-fixture deficiency from contract, playbook, runtime, specification, verification, or isolation drift. A subagent MAY repair a disposable fixture to continue the sequence, but it SHALL preserve the original failure and SHALL NOT edit the ZPP source checkout.

#### Scenario: BDD target — Track and classify gaps through sequence closeout
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Reconcile gaps against design and implementation","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Track and classify gaps through sequence closeout"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Track and classify gaps through sequence closeout`

### Requirement: Close gaps interactively and rerun
The coordinating audit SHALL present one structured result and gap ledger per workflow. Every source-level gap SHALL remain open until the maintainer accepts a correction, explicitly defers it, rejects it with rationale, or acknowledges a blocker. An accepted correction SHALL be applied only within the authority of the current repository change, shall update the owning design and implementation evidence together, and SHALL trigger a fresh subagent, Git repository, OpenSpec root, product home, and synthetic change for the affected workflow. The audit SHALL preserve superseded evidence and SHALL report completion only when every workflow mock sequence closes and every gap has an explicit closeout state.

#### Scenario: BDD target — Resolve one workflow gap and rerun from scratch
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Close gaps interactively and rerun","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Resolve one workflow gap and rerun from scratch"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Resolve one workflow gap and rerun from scratch`
