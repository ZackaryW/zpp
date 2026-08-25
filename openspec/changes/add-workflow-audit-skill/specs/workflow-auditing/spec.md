## Purpose

Provide maintainers with an interactive local audit that runs a synthetic OpenSpec change through every complete ZPP workflow, identifies design-to-implementation gaps, and drives each finding to an explicit closeout state.

## ADDED Requirements

### Requirement: Bootstrap one reusable mock project
The workflow audit SHALL derive its audit set from the repository's validated packaged complete-workflow contract inventory. Before assigning a workflow, the coordinator SHALL create one temporary base project, initialize it as a Git repository and local OpenSpec root without projecting agent tools, and verify its exact Git and OpenSpec identities. Every workflow run SHALL clone that immutable base into a fresh disposable repository and use a fresh temporary ZPP product home. A subagent SHALL NOT repeat base initialization, reuse another workflow's clone or product home, mutate the caller's product home, or register either the base or a clone in a persistent store.

#### Scenario: BDD target — Clone a reusable mock base for one workflow
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Bootstrap one reusable mock project","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Clone a reusable mock base for one workflow"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Clone a reusable mock base for one workflow`

### Requirement: Run and review one workflow at a time
The coordinator SHALL assign exactly one workflow subagent at a time. That subagent SHALL start its assigned workflow against its fresh clone and drive the synthetic change through every declared stage in order. At each transition it SHALL inspect the playbook's custom instruction and branches, construct a bounded mock result from the selected component contract, check and record that result through the real workflow reminder CLI, and retain exact inputs, outputs, branch decisions, and OpenSpec state. It SHALL exercise applicable planning, synchronization, verification, finalization, and archive branches and SHALL continue past resolvable fixture deficiencies until the workflow reaches a closed reminder and archived synthetic change or a truthful workflow blocker. The coordinator SHALL receive the result and recapture source, reminder, and lease status before it may assign another workflow.

#### Scenario: BDD target — Complete one workflow before assigning the next
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Run and review one workflow at a time","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Complete one workflow before assigning the next"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Complete one workflow before assigning the next`

### Requirement: Reconcile gaps against design and implementation
Each workflow audit SHALL compare every mock transition with the workflow's JSON stage contract, playbook-specific Markdown configuration and branches, referenced component contracts and skills, workflow CLI and kernel behavior, canonical OpenSpec requirements, capability BDD, and focused Python tests. It SHALL maintain a gap ledger that distinguishes a disposable-fixture deficiency from contract, playbook, runtime, specification, verification, or isolation drift. A subagent MAY repair a disposable fixture to continue the sequence, but it SHALL preserve the original failure and SHALL NOT edit the ZPP source checkout.

#### Scenario: BDD target — Track and classify gaps through sequence closeout
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Reconcile gaps against design and implementation","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Track and classify gaps through sequence closeout"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Track and classify gaps through sequence closeout`

### Requirement: Close feedback before advancing
After each workflow result, the coordinating audit SHALL present that workflow's structured result and gap ledger before assigning another workflow. Every source-level gap SHALL remain open until the maintainer accepts a correction, explicitly defers it, rejects it with rationale, or acknowledges a blocker. An accepted correction SHALL be applied only within the authority of the current repository change, SHALL re-enter the applicable full planning, behavior, utility, wiring, specification, and verification phases rather than patching directly, and SHALL trigger a fresh subagent, clone, product home, and synthetic change for the same workflow. The coordinator SHALL advance only after the rerun closes or every recommendation has an explicit non-open state. The audit SHALL preserve superseded evidence and SHALL report completion only when every workflow mock sequence closes in this serial order.

#### Scenario: BDD target — Re-enter full phases before advancing
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Close feedback before advancing","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Re-enter full phases before advancing"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Re-enter full phases before advancing`
