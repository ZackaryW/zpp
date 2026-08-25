## Purpose

Provide lightweight, persistent workflow-stage reminders from validated packaged
contracts while preserving flexible standalone component execution.

## ADDED Requirements

### Requirement: Strict packaged workflow contracts
ZPP SHALL package one versioned JSON workflow contract for every complete current
`zpp-*` playbook and one versioned JSON component contract for every packaged
`zpps-*` skill. Workflow contracts SHALL identify reminder mode and an ordered list
of unique stage IDs mapped to existing component identities. Component contracts
SHALL declare their identity, kind, effect class, standalone eligibility, and bounded
result vocabulary. Contract loading SHALL reject unknown fields, unsupported
versions, duplicate identities or stage IDs, missing referenced skills, and invalid
typed values.

#### Scenario: Load a complete contract inventory
- **WHEN** the packaged workflow and component contract inventory is inspected
- **THEN** every complete current playbook and packaged component resolves to exactly one valid JSON contract and every registered stage references an existing component

#### Scenario: Reject malformed contract metadata
- **WHEN** a contract contains an unknown field, invalid type, duplicate stage ID, unsupported version, or missing component reference
- **THEN** ZPP rejects the packaged inventory with a diagnostic identifying the exact contract and field

### Requirement: Start or resume a reminder workflow
ZPP SHALL expose `zpp workflow run start <workflow>` for exact repository/change
targets. Starting SHALL load the packaged workflow contract into persistent
product-home reminder state before the playbook performs another lifecycle action.
Starting the same workflow for the same exact targets SHALL idempotently return the
existing checklist without resetting completed or skipped stages. Starting a
different workflow for already governed targets SHALL preserve the existing reminder
and require an explicit stop or replacement request rather than silently overwrite
it. Starting reminder state alone SHALL NOT acquire a Bundler lease or grant mutation,
checkpoint, archive, or bypass authority.

#### Scenario: Start a packaged workflow reminder
- **WHEN** a playbook starts its packaged workflow for exact repository/change targets with no matching reminder
- **THEN** ZPP persists an active checklist containing the contract's ordered pending stages and returns its workflow identity, targets, and first pending stage

#### Scenario: Resume without resetting progress
- **WHEN** the same workflow and targets are started after one or more stages were completed or skipped
- **THEN** ZPP returns the existing checklist with the observed progress unchanged

#### Scenario: Preserve an existing different workflow
- **WHEN** start targets already governed by a different active reminder workflow
- **THEN** ZPP reports the existing workflow and does not replace its checklist without an explicit replacement operation

### Requirement: Require registration only for complete playbooks
Every complete packaged `zpp-*` playbook SHALL start its declared workflow reminder
before its first lifecycle stage or operation. A kernel assessment identifying a
complete playbook without matching active registration SHALL return
`workflow-start-required`. Direct standalone `zpps-*` invocations SHALL remain
eligible without starting a workflow when no active reminder governs the exact
targets.

#### Scenario: Remind an unregistered playbook to start
- **WHEN** a caller identifies a complete packaged playbook but requests a lifecycle action before starting its workflow reminder
- **THEN** the kernel reports `workflow-start-required` with the exact start command and performs no stage update

#### Scenario: Preserve standalone component use
- **WHEN** a caller directly invokes an otherwise eligible `zpps-*` component for targets with no active reminder workflow
- **THEN** ZPP reports the invocation as untracked and preserves the component's existing standalone behavior

### Requirement: Inspect and directly customize reminder stages
ZPP SHALL expose structured status and stop operations plus direct `insert`, `delete`,
`modify`, and `upsert` operations over an active workflow's stage checklist. Stage
customization SHALL apply immediately to the persisted reminder, SHALL preserve
unique stable stage IDs and valid component references, and SHALL NOT create a
revision history, approval workflow, or implicit authority. Stopping SHALL remove the
active reminder association without releasing, completing, or abandoning any Bundler
lease.

#### Scenario: Insert a custom reminder stage
- **WHEN** a user inserts a valid uniquely identified component stage before or after an existing stage
- **THEN** subsequent status and sequence checks expose that stage at the requested position

#### Scenario: Upsert a reminder stage idempotently
- **WHEN** a user upserts a stage that is absent and then repeats the same upsert
- **THEN** ZPP creates one stage on the first request and returns the same single stage configuration on the repeated request

#### Scenario: Reject an invalid checklist edit
- **WHEN** a user edit would create a duplicate stage ID, reference an unknown component, or name an unavailable position
- **THEN** ZPP rejects that edit without changing the persisted checklist

#### Scenario: Stop reminder state independently of leases
- **WHEN** a user stops an active reminder workflow
- **THEN** ZPP removes that workflow reminder while leaving all Bundler lease state unchanged

### Requirement: Return strong non-blocking sequence reminders
For an active workflow reminder, the kernel SHALL compare each requested component
with the first pending registered stage and return structured reminder evidence. A
matching request SHALL report `sequence_match: true`. A different component SHALL
report `sequence_match: false`, the expected stage and component, all unfinished
stages, and a prominent warning while retaining `allowed: true`. Reminder comparison
SHALL NOT dispatch a component, infer an outcome, or convert the warning into
mutation or checkpoint authority.

#### Scenario: Confirm an in-sequence request
- **WHEN** the requested component matches the first pending registered stage
- **THEN** the kernel returns `allowed: true`, `sequence_match: true`, and the matching workflow and stage identities

#### Scenario: Warn about an out-of-sequence request
- **WHEN** a requested component differs from the first pending registered stage
- **THEN** the kernel returns `allowed: true`, `sequence_match: false`, the expected stage, the unfinished checklist, and a visible warning without selecting or invoking another component

### Requirement: Conditional prompt-submission reminder hook
ZPP SHALL package a separate native hook identity named `zpp-workflow-reminder` for
each supported agent whose Agent Router adapter confirms a prompt-submission event
that injects successful command output into model context. The hook SHALL invoke a
read-only `zpp workflow run remind` operation for the current exact repository
target. With an active workflow, the operation SHALL emit compact prompt-ready
context containing the workflow identity, next stage and component, and remaining
stage count. Without an active workflow, it SHALL emit no prompt context. The hook
SHALL NOT start, stop, replace, customize, check, record, acquire, transition,
dispatch, or grant authority, and SHALL NOT be combined with the `zpp-traits` hook.

The shared root and grouped workflow lifecycle SHALL project, inspect, update, and
remove each eligible reminder hook through Agent Router in the selected scope. ZPP
SHALL NOT infer event support from an agent name or write a native destination
directly. When an adapter does not confirm a suitable event, ZPP SHALL omit the hook
for that agent and retain kernel sequence reminders as the portable path.

#### Scenario: Inject compact active workflow status on prompt submission
- **WHEN** a supported agent with a confirmed prompt-submission context event receives a user prompt in a repository with an active workflow reminder
- **THEN** `zpp-workflow-reminder` injects only the workflow identity, next stage and component, and remaining-stage count without changing reminder or lease state

#### Scenario: Stay silent without an active workflow
- **WHEN** the prompt-submission reminder hook runs in a repository without an active workflow reminder
- **THEN** it emits no prompt context and creates no workflow, product-home, or lease state

#### Scenario: Omit an unsupported native reminder hook
- **WHEN** Agent Router does not confirm a prompt-submission context event for a selected agent
- **THEN** ZPP projects no `zpp-workflow-reminder` hook for that agent and kernel reminder behavior remains available

#### Scenario: Reconcile the reminder hook through Agent Router
- **WHEN** a lifecycle operation projects or removes an eligible agent's current ZPP integration
- **THEN** it reconciles `zpp-workflow-reminder` through Agent Router in the selected scope without changing the separately packaged `zpp-traits` hook behavior

### Requirement: Advance reminders only from accepted matching results
After kernel result assessment, ZPP SHALL mark a registered stage completed or
skipped only when the assessed action names that stage's configured component and the
component returned an accepted bounded result. Read-only exploration, an unrelated
component result, a warning acknowledgement, or a failed or blocked result SHALL NOT
advance the checklist. Checklist progress SHALL survive later CLI processes and
agent turns until explicitly changed or stopped.

#### Scenario: Record an accepted matching stage
- **WHEN** the first pending stage's configured component returns an accepted completed or not-applicable result
- **THEN** ZPP records that stage outcome and exposes the following pending stage as the next reminder

#### Scenario: Preserve progress across processes
- **WHEN** a later CLI process inspects the same exact targets after accepted stage progress
- **THEN** it observes the persisted outcomes and the same next pending reminder

#### Scenario: Ignore unrelated read-only evidence
- **WHEN** read-only exploration runs while a workflow reminder is active
- **THEN** its result does not complete, skip, delete, or reorder any registered stage

### Requirement: Keep reminder state separate from lease authority
Workflow reminder state SHALL be stored and managed by ZPP independently of Bundler
lease state. A reminder MAY retain a reference to an observed bundle identity, but
its stages SHALL NOT become lease members and reminder creation, customization,
progress, or removal SHALL NOT acquire, expand, complete, abandon, or authorize a
lease. Lease operations SHALL continue to govern only exact OpenSpec store/change
ownership.

#### Scenario: Start before governed mutation
- **WHEN** a playbook starts its reminder before any governed mutation requires a lease
- **THEN** the checklist is available without creating or acquiring a Bundler bundle

#### Scenario: Associate an observed bundle without changing it
- **WHEN** a later kernel guard acquires a bundle for the workflow's exact targets
- **THEN** ZPP may expose that bundle identity with reminder status while preserving the existing Bundler members and authority semantics
