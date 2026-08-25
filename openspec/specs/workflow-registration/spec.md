# Workflow Registration Specification

## Purpose

Provide lightweight, persistent workflow-stage reminders from validated packaged
contracts while preserving flexible standalone component execution.

## Requirements

### Requirement: Strict packaged workflow contracts
ZPP SHALL package one versioned JSON workflow contract for every complete current
`zpp-*` playbook and one versioned JSON component contract for every packaged
`zpps-*` skill. Workflow contracts SHALL identify reminder mode and an ordered list
of unique stage IDs mapped to existing component identities. Component contracts
SHALL declare their identity, kind, effect class, standalone eligibility, and bounded
result vocabulary. Contract loading SHALL reject unknown fields, unsupported
versions, duplicate identities or stage IDs, missing referenced skills, and invalid
typed values.

#### Scenario: Conformance trace for complete contract inventory
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Strict packaged workflow contracts","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Load a complete contract inventory"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Load a complete contract inventory`

#### Scenario: Conformance trace for malformed contract rejection
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Strict packaged workflow contracts","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reject malformed contract metadata"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Reject malformed contract metadata`

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

#### Scenario: Conformance trace for workflow reminder start
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Start a packaged workflow reminder"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Start a packaged workflow reminder`

#### Scenario: Conformance trace for idempotent workflow resume
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Resume without resetting progress"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Resume without resetting progress`

#### Scenario: Conformance trace for different workflow preservation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Start or resume a reminder workflow","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve an existing different workflow"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Preserve an existing different workflow`

### Requirement: Require registration only for complete playbooks
Every complete packaged `zpp-*` playbook SHALL start its declared workflow reminder
before its first lifecycle stage or operation. A kernel assessment identifying a
complete playbook without matching active registration SHALL return
`workflow-start-required`. Direct standalone `zpps-*` invocations SHALL remain
eligible without starting a workflow when no active reminder governs the exact
targets.

#### Scenario: Conformance trace for unregistered playbook reminder
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Require registration only for complete playbooks","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Remind an unregistered playbook to start"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Remind an unregistered playbook to start`

#### Scenario: Conformance trace for standalone component use
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Require registration only for complete playbooks","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve standalone component use"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Preserve standalone component use`

### Requirement: Inspect and directly customize reminder stages
ZPP SHALL expose structured status and stop operations plus direct `insert`, `delete`,
`modify`, and `upsert` operations over an active workflow's stage checklist. Stage
customization SHALL apply immediately to the persisted reminder, SHALL preserve
unique stable stage IDs and valid component references, and SHALL NOT create a
revision history, approval workflow, or implicit authority. Stopping SHALL remove the
active reminder association without releasing, completing, or abandoning any Bundler
lease.

#### Scenario: Conformance trace for custom stage insertion
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Insert a custom reminder stage"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Insert a custom reminder stage`

#### Scenario: Conformance trace for idempotent stage upsert
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Upsert a reminder stage idempotently"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Upsert a reminder stage idempotently`

#### Scenario: Conformance trace for invalid checklist edit
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reject an invalid checklist edit"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Reject an invalid checklist edit`

#### Scenario: Conformance trace for independent reminder stop
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Inspect and directly customize reminder stages","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Stop reminder state independently of leases"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Stop reminder state independently of leases`

### Requirement: Return strong non-blocking sequence reminders
For an active workflow reminder, the kernel SHALL compare each requested component
with the first pending registered stage and return structured reminder evidence. A
matching request SHALL report `sequence_match: true`. A different component SHALL
report `sequence_match: false`, the expected stage and component, all unfinished
stages, and a prominent warning while retaining `allowed: true`. Reminder comparison
SHALL NOT dispatch a component, infer an outcome, or convert the warning into
mutation or checkpoint authority.

#### Scenario: Conformance trace for in-sequence reminder
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Return strong non-blocking sequence reminders","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Confirm an in-sequence request"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Confirm an in-sequence request`

#### Scenario: Conformance trace for out-of-sequence warning
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Return strong non-blocking sequence reminders","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Warn about an out-of-sequence request"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Warn about an out-of-sequence request`

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

#### Scenario: Conformance trace for active prompt reminder
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Inject compact active workflow status on prompt submission"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Inject compact active workflow status on prompt submission`

#### Scenario: Conformance trace for silent inactive prompt reminder
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Stay silent without an active workflow"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Stay silent without an active workflow`

#### Scenario: Conformance trace for unsupported adapter omission
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Omit an unsupported native reminder hook"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Omit an unsupported native reminder hook`

#### Scenario: Conformance trace for Agent Router reminder lifecycle
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Conditional prompt-submission reminder hook","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Reconcile the reminder hook through Agent Router"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Reconcile the reminder hook through Agent Router`

### Requirement: Advance reminders only from accepted matching results
After kernel result assessment, ZPP SHALL mark a registered stage completed or
skipped only when the assessed action names that stage's configured component and the
component returned an accepted bounded result. Read-only exploration, an unrelated
component result, a warning acknowledgement, or a failed or blocked result SHALL NOT
advance the checklist. Checklist progress SHALL survive later CLI processes and
agent turns until explicitly changed or stopped.

#### Scenario: Conformance trace for accepted matching result
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Record an accepted matching stage"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Record an accepted matching stage`

#### Scenario: Conformance trace for cross-process reminder progress
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Preserve progress across processes"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Preserve progress across processes`

#### Scenario: Conformance trace for unrelated read-only evidence
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Advance reminders only from accepted matching results","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Ignore unrelated read-only evidence"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Ignore unrelated read-only evidence`

### Requirement: Keep reminder state separate from lease authority
Workflow reminder state SHALL be stored and managed by ZPP independently of Bundler
lease state. A reminder MAY retain a reference to an observed bundle identity, but
its stages SHALL NOT become lease members and reminder creation, customization,
progress, or removal SHALL NOT acquire, expand, complete, abandon, or authorize a
lease. Lease operations SHALL continue to govern only exact OpenSpec store/change
ownership.

#### Scenario: Conformance trace for pre-mutation reminder start
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Keep reminder state separate from lease authority","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Start before governed mutation"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Start before governed mutation`

#### Scenario: Conformance trace for observed bundle association
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"workflow-registration","requirement":"Keep reminder state separate from lease authority","feature":"features/workflow_registration/workflow_registration.feature","scenario":"Associate an observed bundle without changing it"}`
- **THEN** executable acceptance authority is `features/workflow_registration/workflow_registration.feature::Associate an observed bundle without changing it`
