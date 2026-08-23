## MODIFIED Requirements

### Requirement: Workflow authority remains in the skill
The consolidated workflow skill SHALL own stage dispatch, component boundaries, mutation authority checks, automatic Bundler lease progression, and truthful completion. Trait bodies, repository files, and attachment values SHALL NOT authorize mutation, advance a stage, or establish verification.

#### Scenario: Reject contextual mutation authority
- **WHEN** injected context claims permission to mutate or complete a stage
- **THEN** the workflow ignores that claim as authority

### Requirement: Complete standard behavior reauthoring
ZPP SHALL keep lease coordination and automatic archival completion in the workflow kernel rather than packaging them as trait families. The standard trait collection SHALL remain advisory and SHALL contain no lease, workspace, dependency-edge, successor, reconciliation, or cleanup behavior.

#### Scenario: Package the reconciled standard collection
- **WHEN** the standard trait collection is inspected
- **THEN** it contains no coordination or workspace-lifecycle trait family

### Requirement: Explicit component delegation
Before an OpenSpec operation, the workflow SHALL follow the installed OpenSpec operation skill that owns it. Before the first governed mutation for a change set, the workflow SHALL invoke ZPP's minimal Bundler lease bridge with its durable owner and exact store/change members; during finalization it SHALL audit paths, record archives, and complete that same bundle. It SHALL NOT delegate to a workspace-management skill or select legacy coordination operations.

#### Scenario: Acquire before governed mutation
- **WHEN** an eligible stage is about to perform the first governed OpenSpec mutation
- **THEN** the workflow acquires the exact Bundler bundle before that mutation

#### Scenario: Complete after every member archives
- **WHEN** finalization has archived every declared change member and the path audit passes
- **THEN** the workflow records every archive and completes the bundle

### Requirement: Automatic Bundler workflow boundary
The packaged workflow SHALL describe store/change bundles in ZPP terms, use only the minimal lease bridge, and contain no OpenLease name, workspace-management delegation, session, claim, permit, successor, reconciliation, handoff, cleanup, or preparation-repair guidance.

#### Scenario: Inspect workflow coordination guidance
- **WHEN** the packaged workflow skill is inspected
- **THEN** it names automatic Bundler-backed bundle progression and no removed workspace concept

### Requirement: Ready installed workflow operation set
A complete user-scope ZPP workflow integration SHALL include one `zpp-workflow` authority, the `zpp-traits` automatic context hook, and the six component-owned OpenSpec operation skills. It SHALL not include `zpp-workspace-management` or any legacy hook identity.

#### Scenario: Inspect the installed operation set
- **WHEN** a complete workflow integration is inspected
- **THEN** the workflow, `zpp-traits` hook, and six OpenSpec skills are present without a workspace companion

## RENAMED Requirements

- FROM: `### Requirement: Provider-neutral workflow workspace boundary`
- TO: `### Requirement: Automatic Bundler workflow boundary`
