## Purpose

Provide maintainers with an interactive, local, read-only audit that independently simulates every complete ZPP workflow and compares its declared design with packaged skills, runtime behavior, and verification evidence.

## ADDED Requirements

### Requirement: Discover the complete workflow audit set
The workflow audit SHALL derive its audit set from the repository's validated packaged complete-workflow contract inventory. It SHALL NOT maintain a separate fixed workflow list, silently omit a discovered complete workflow, or treat entry routers and standalone components as complete workflows.

#### Scenario: Audit the discovered complete workflow inventory
- **WHEN** a maintainer starts a local workflow audit in a ZPP source checkout
- **THEN** the audit reports the exact complete workflows discovered from packaged workflow contracts and creates one audit assignment for each

#### Scenario: Reject an incomplete workflow evidence set
- **WHEN** a discovered workflow lacks its contract, playbook skill, referenced component contract, or referenced component skill
- **THEN** that workflow audit reports the missing evidence as a blocking conformance finding rather than silently narrowing its scope

### Requirement: Isolate one simulation subagent per workflow
The workflow audit SHALL assign every discovered complete workflow to a distinct subagent. Each subagent SHALL use isolated temporary ZPP product-home state to simulate start, resume, ordered checks and accepted-result recording, out-of-sequence reminders, and direct stage customization without modifying repository sources, the caller's product home, or retained Bundler leases. When concurrency is limited, assignments SHALL be queued without reusing one subagent for multiple workflows.

#### Scenario: Simulate every workflow independently
- **WHEN** the audit discovers multiple complete workflows
- **THEN** each workflow is simulated by its own subagent with a unique temporary product home and synthetic audit change identity

#### Scenario: Preserve live workflow state
- **WHEN** a simulation starts, customizes, advances, resumes, and stops its workflow reminder
- **THEN** all state transitions occur only in temporary product-home state and the live reminder and lease state remain unchanged

### Requirement: Compare declared design with implementation evidence
Each workflow audit SHALL compare the workflow's JSON stage contract, playbook-specific Markdown configuration and branches, referenced component contracts and skills, workflow CLI behavior, kernel reminder behavior, canonical OpenSpec requirements, capability BDD, and focused Python tests. Findings SHALL identify the workflow, evidence paths or commands, expected behavior, observed behavior, and whether the mismatch is contract drift, playbook drift, runtime drift, specification drift, or verification coverage drift.

#### Scenario: Report a design-to-implementation mismatch
- **WHEN** simulation or source evidence contradicts a workflow's declared contract or canonical requirement
- **THEN** the workflow result reports the contradiction with reproducible evidence and does not edit the conflicting artifact

#### Scenario: Report aligned workflow evidence
- **WHEN** declared stages, custom branches, isolated runtime observations, specifications, BDD, and focused tests agree
- **THEN** the workflow result reports conformance together with the evidence actually inspected and commands actually run

### Requirement: Review audit results interactively
The coordinating audit SHALL present one structured result per workflow and an aggregate summary after all assigned subagents return. It SHALL let the maintainer inspect a workflow result, supply a correction, or request a targeted rerun while preserving earlier results. It SHALL distinguish an unexecuted or blocked check from a passing check and SHALL NOT infer authority to repair, commit, archive, customize live stages, or continue a product workflow.

#### Scenario: Review and rerun one workflow
- **WHEN** a maintainer supplies additional evidence or requests a rerun for one workflow
- **THEN** the audit creates a fresh subagent assignment for that workflow, preserves the other workflow results, and updates the aggregate conclusion transparently

#### Scenario: Finish without repair authority
- **WHEN** the interactive audit concludes with one or more findings
- **THEN** it reports evidence and severity without changing source or live workflow state and requires a separate request for any repair
