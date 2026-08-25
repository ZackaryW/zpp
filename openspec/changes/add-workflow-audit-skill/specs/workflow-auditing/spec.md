## Purpose

Provide maintainers with an interactive, local, read-only audit that independently simulates every complete ZPP workflow and compares its declared design with packaged skills, runtime behavior, and verification evidence.

## ADDED Requirements

### Requirement: Discover the complete workflow audit set
The workflow audit SHALL derive its audit set from the repository's validated packaged complete-workflow contract inventory. It SHALL NOT maintain a separate fixed workflow list, silently omit a discovered complete workflow, or treat entry routers and standalone components as complete workflows.

#### Scenario: BDD target — Prepare one assignment per complete workflow
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Discover the complete workflow audit set","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Prepare one assignment per complete workflow"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Prepare one assignment per complete workflow`

### Requirement: Isolate one simulation subagent per workflow
The workflow audit SHALL assign every discovered complete workflow to a distinct subagent. Each subagent SHALL use isolated temporary ZPP product-home state to simulate start, resume, ordered checks and accepted-result recording, out-of-sequence reminders, and direct stage customization without modifying repository sources, the caller's product home, or retained Bundler leases. When concurrency is limited, assignments SHALL be queued without reusing one subagent for multiple workflows.

#### Scenario: BDD target — Exercise every workflow in isolated reminder state
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Isolate one simulation subagent per workflow","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Exercise every workflow in isolated reminder state"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Exercise every workflow in isolated reminder state`

### Requirement: Compare declared design with implementation evidence
Each workflow audit SHALL compare the workflow's JSON stage contract, playbook-specific Markdown configuration and branches, referenced component contracts and skills, workflow CLI behavior, kernel reminder behavior, canonical OpenSpec requirements, capability BDD, and focused Python tests. Findings SHALL identify the workflow, evidence paths or commands, expected behavior, observed behavior, and whether the mismatch is contract drift, playbook drift, runtime drift, specification drift, or verification coverage drift.

#### Scenario: BDD target — Classify design and implementation evidence per workflow
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Compare declared design with implementation evidence","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Classify design and implementation evidence per workflow"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Classify design and implementation evidence per workflow`

### Requirement: Review audit results interactively
The coordinating audit SHALL present one structured result per workflow and an aggregate summary after all assigned subagents return. It SHALL let the maintainer inspect a workflow result, supply a correction, or request a targeted rerun while preserving earlier results. It SHALL distinguish an unexecuted or blocked check from a passing check and SHALL NOT infer authority to repair, commit, archive, customize live stages, or continue a product workflow.

#### Scenario: BDD target — Rerun one selected workflow without replacing other results
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-auditing","requirement":"Review audit results interactively","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Rerun one selected workflow without replacing other results"}`
- **THEN** executable acceptance authority is `features/workflow_auditing/workflow_auditing.feature::Rerun one selected workflow without replacing other results`
