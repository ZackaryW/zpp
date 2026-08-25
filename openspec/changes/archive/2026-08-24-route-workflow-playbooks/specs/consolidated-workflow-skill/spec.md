## ADDED Requirements

### Requirement: Explicit legacy workflow compatibility
ZPP SHALL package `zpp-legacy-workflow` as an explicit compatibility entry for the
immediately preceding consolidated generic-workflow invocation shape. It SHALL invoke
`zpp-generic-workflow` exactly once with the original request, exact roots, accepted
owner input, and only owner-supplied authority. It SHALL NOT own or copy lifecycle
stages, select continuation, participate in `zpp-auto` routing, translate a ZPP 1.x
`zpp-flow-*` identity, or claim the delegated workflow's result.

#### Scenario: Invoke explicit legacy compatibility
- **WHEN** a caller explicitly invokes `zpp-legacy-workflow` with a supported preceding generic-workflow request
- **THEN** it invokes `zpp-generic-workflow` once with the preserved request and authority and applies no independent workflow policy

#### Scenario: Keep legacy out of automatic routing
- **WHEN** automatic triage needs a current generic product workflow
- **THEN** it selects `zpp-generic-workflow` and does not invoke the legacy compatibility entry

## MODIFIED Requirements

### Requirement: Outcome workflow entry family
ZPP SHALL distribute `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`,
and `zpp-generic-workflow` as current user-invokable Markdown playbooks, plus
`zpp-legacy-workflow` as an explicit compatibility entry. Each complete current
playbook SHALL own its scenario-specific workflow, state its complete ordered
sequence and branch conditions, and execute exact reusable `zpps-*` stage or
operation skills as distinct visible actions. A `zpps-*` skill SHALL own only its
repeatable bounded procedure and observed result; it SHALL NOT own the caller's
workflow sequence or continuation. A workflow SHALL NOT defer its sequence or
next-stage selection to `zpps-workflow-kernel`, a shared hidden stage list, or an
implicit convention. ZPP SHALL keep the removed `zpp-workflow` identity obsolete and
SHALL NOT restore it as an alias.

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
workflow invocation, and remain under the selected playbook until that playbook
returns a real blocked or completed lifecycle result. Merely reporting or
acknowledging the selected playbook, returning to triage, or treating handoff as
completion SHALL NOT satisfy the route. A playbook SHALL preserve only authority
explicitly supplied by the owner and SHALL NOT grant mutation or checkpoint-commit
authority by selecting a route.

#### Scenario: Route a clear defect correction
- **WHEN** `zpp-auto` receives an unambiguous request to correct a defect
- **THEN** it invokes `zpp-fix-bug` exactly once with the original request and supplied authority and continues under that playbook rather than merely naming or acknowledging the route

#### Scenario: Route a mixed product workflow to the generic entry
- **WHEN** a request remains product-workflow-shaped but no specialized outcome exclusively owns it
- **THEN** `zpp-auto` invokes `zpp-generic-workflow` at clarification instead of using compatibility or inventing a specialized outcome

#### Scenario: Return a genuine non-match without handoff
- **WHEN** bounded triage establishes that a request is not a ZPP product workflow or an accepted direct artifact-maintenance route
- **THEN** `zpp-auto` returns a no-handoff result without invoking a workflow or mutating governed state

#### Scenario: Reject a terminal handoff acknowledgement
- **WHEN** automatic triage selects a playbook but no selected-playbook result is produced
- **THEN** the workflow remains incomplete and does not treat the handoff itself as a successful outcome

#### Scenario: Keep the removed generic identity obsolete
- **WHEN** a projected integration is inspected after migration
- **THEN** no `zpp-workflow` skill or alias is present

### Requirement: Ready installed workflow operation set
A complete user-scope ZPP workflow integration SHALL include the five complete
current playbooks `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, and
`zpp-generic-workflow`; the explicit `zpp-legacy-workflow` compatibility entry;
guard-only `zpps-workflow-kernel`; the seven substantive bounded stage skills; the
eleven substantive procedure-complete OpenSpec adapters; `zpps-verify-repository`;
and the `zpp-traits` automatic context hook. It SHALL NOT include `zpp-workflow`,
`zpps-onboard`, broad `zpps-plan-change`, `zpps-verify`, or `zpps-archive` identities,
generated `openspec-*` operation skills, `zpp-workspace-management`, or a ZPP 1.x
stage or hook identity.

#### Scenario: Conformance trace for the canonical workflow identity sequence
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Ready installed workflow operation set","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Preserve one deterministic public inventory"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Preserve one deterministic public inventory`

## REMOVED Requirements

### Requirement: No legacy workflow compatibility
**Reason**: The legacy identity currently carries the complete generic ZPP 2 sequence,
which makes current generic behavior indistinguishable from explicit compatibility
and encourages automatic triage to treat legacy as an unmatched-request bucket.

**Migration**: Use `zpp-generic-workflow` for current mixed or unspecialized product
workflows. Invoke `zpp-legacy-workflow` only when translating the immediately
preceding consolidated generic-workflow request shape.
