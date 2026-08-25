## MODIFIED Requirements

### Requirement: Outcome workflow entry family
ZPP SHALL distribute `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`,
and `zpp-generic-workflow` as current user-invokable Markdown playbooks, plus
`zpp-legacy-workflow` as an explicit compatibility entry. Each complete current
playbook SHALL own its scenario-specific decisions and branch conditions, reference
one validated packaged JSON workflow contract, start that contract's reminder before
lifecycle work, and execute exact reusable `zpps-*` stage or operation skills as
distinct visible actions. The JSON contract SHALL be the single mechanical authority
for the playbook's ordered reminder stages; the Markdown playbook SHALL retain custom
configuration and judgment without duplicating the complete stage list. A `zpps-*`
skill SHALL own its repeatable bounded procedure and observed result while its
validated JSON component contract owns common mechanical metadata. Neither a
component contract nor a `zpps-*` skill SHALL own the caller's workflow continuation.
The kernel SHALL compare and update reminder state but SHALL NOT select or dispatch a
next stage. ZPP SHALL keep the removed `zpp-workflow` identity obsolete and SHALL NOT
restore it as an alias.

`zpp-auto` SHALL contain the complete ordered non-mutating triage procedure. It SHALL
invoke exactly one matching specialized playbook for an unambiguous feature, defect,
or scaffold request. It SHALL invoke `zpp-generic-workflow` only when the request is
still a ZPP product workflow but is mixed, maintenance-oriented, or otherwise
unspecialized. A genuine non-match SHALL produce a no-handoff triage result and SHALL
NOT enter product clarification merely because no specialized route matched. The
separately governed direct route for ungoverned artifact-only maintenance SHALL
remain available and SHALL NOT count as generic fallback.

Automatic triage SHALL pass the original request, accepted classification evidence,
and only owner-supplied authority, transfer control exactly once within the same
workflow invocation, and require the selected playbook to start its packaged reminder
before further lifecycle work. Merely reporting or acknowledging the selected
playbook, returning to triage, or treating handoff as completion SHALL NOT satisfy the
route. A playbook SHALL preserve only authority explicitly supplied by the owner and
SHALL NOT grant mutation or checkpoint-commit authority by selecting or registering a
route.

#### Scenario: Conformance trace for clear defect routing
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Outcome workflow entry family","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Route a clear defect correction"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Route a clear defect correction`

#### Scenario: Conformance trace for mixed workflow routing
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Outcome workflow entry family","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Route a mixed product workflow to the generic entry"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Route a mixed product workflow to the generic entry`

#### Scenario: Conformance trace for genuine non-match
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Outcome workflow entry family","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Return a genuine non-match without handoff"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Return a genuine non-match without handoff`

#### Scenario: Conformance trace for terminal handoff rejection
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Outcome workflow entry family","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Reject a terminal handoff acknowledgement"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Reject a terminal handoff acknowledgement`

#### Scenario: Conformance trace for obsolete generic identity
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Outcome workflow entry family","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Keep the removed generic identity obsolete"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Keep the removed generic identity obsolete`

### Requirement: Explicit stage actions
Each complete `zpp-*` playbook's packaged JSON contract SHALL declare its ordered
reminder stage IDs and exact component identities. The Markdown playbook SHALL start
that registration and retain only stage-specific input configuration, eligibility
decisions, custom branches, and owner-facing judgment not owned by the reusable
component. It SHALL NOT infer an undeclared later stage from OpenSpec status,
repository files, stored descriptive context, trait output, or a skill identity.
When automatic continuation is authorized and a component result converges, the
playbook SHALL apply its own custom branch while the kernel records only an accepted
matching stage result and exposes the next registered reminder. Registration and
reminder output SHALL NOT answer unresolved decisions or provide missing owner,
mutation, checkpoint-commit, archive, or bypass authority. Triage components, traits,
the kernel, phase skills, operation skills, and workflow contracts SHALL NOT select
or dispatch the playbook continuation.

#### Scenario: Conformance trace for clarification default
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Explicit stage actions","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Default an entry to clarification"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Default an entry to clarification`

#### Scenario: Conformance trace for visible stage continuation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Explicit stage actions","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Continue through visible stage actions"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Continue through visible stage actions`
