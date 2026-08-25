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

#### Scenario: Route a clear defect correction
- **WHEN** `zpp-auto` receives an unambiguous request to correct a defect
- **THEN** it invokes `zpp-fix-bug` exactly once with the original request and supplied authority, and that playbook starts its packaged reminder before continuing

#### Scenario: Route a mixed product workflow to the generic entry
- **WHEN** a request remains product-workflow-shaped but no specialized outcome exclusively owns it
- **THEN** `zpp-auto` invokes `zpp-generic-workflow` at clarification instead of using compatibility or inventing a specialized outcome

#### Scenario: Return a genuine non-match without handoff
- **WHEN** bounded triage establishes that a request is not a ZPP product workflow or an accepted direct artifact-maintenance route
- **THEN** `zpp-auto` returns a no-handoff result without registering or invoking a workflow or mutating governed state

#### Scenario: Reject a terminal handoff acknowledgement
- **WHEN** automatic triage selects a playbook but that playbook neither starts its packaged reminder nor produces a selected-playbook result
- **THEN** the workflow remains incomplete and does not treat the handoff itself as a successful outcome

#### Scenario: Keep the removed generic identity obsolete
- **WHEN** a projected integration is inspected after migration
- **THEN** no `zpp-workflow` skill, contract, or alias is present

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

#### Scenario: Default an entry to clarification
- **WHEN** a complete workflow registration starts without accepted evidence for a later custom branch
- **THEN** its first pending registered reminder is `clarify` rather than an action inferred from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes or truthfully skips one registered conditional stage and continues
- **THEN** the kernel records that matching result and the active playbook applies its custom branch with the following registered stage visible as a reminder
