## MODIFIED Requirements

### Requirement: Outcome workflow entry family
ZPP SHALL distribute `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, and `zpp-legacy-workflow` as user-invokable Markdown skills. Each complete `zpp-*` skill SHALL own a scenario-specific workflow, state its complete ordered sequence and branch conditions, and execute exact reusable `zpps-*` stage or operation skills as distinct visible actions. A `zpps-*` skill SHALL own only its repeatable bounded procedure and observed result; it SHALL NOT own the caller's workflow sequence or continuation. A workflow SHALL NOT defer its sequence or next-stage selection to `zpps-workflow-kernel`, a shared hidden stage list, or an implicit convention. `zpp-legacy-workflow` SHALL preserve the generic product-workflow outcome of the former `zpp-workflow` identity while using the current reusable stages and kernel guards. ZPP SHALL remove the `zpp-workflow` skill identity without an alias.

`zpp-auto` SHALL contain the complete ordered non-mutating triage procedure. It SHALL invoke exactly one matching specialized playbook for an unambiguous request and SHALL invoke `zpp-legacy-workflow` at `clarify` for mixed, unsupported, or unresolved intent. It SHALL pass the original request, accepted classification evidence, and only owner-supplied authority, transfer control exactly once within the same workflow invocation, and remain under the selected playbook until that playbook returns a real blocked or completed lifecycle result. Merely reporting or acknowledging the selected playbook, returning to triage, or treating handoff as completion SHALL NOT satisfy the route. A playbook SHALL preserve only authority explicitly supplied by the owner and SHALL NOT grant mutation or checkpoint-commit authority by selecting a route.

#### Scenario: Route a clear defect correction
- **WHEN** `zpp-auto` receives an unambiguous request to correct a defect
- **THEN** it invokes `zpp-fix-bug` exactly once with the original request and supplied authority and continues under that playbook rather than merely naming or acknowledging the route

#### Scenario: Route unresolved intent to the legacy workflow
- **WHEN** `zpp-auto` cannot select exactly one specialized outcome
- **THEN** it delegates to `zpp-legacy-workflow` at `clarify` rather than inventing a workflow kind

#### Scenario: Reject a terminal handoff acknowledgement
- **WHEN** automatic triage selects a playbook but no selected-playbook result is produced
- **THEN** the workflow remains incomplete and does not treat the handoff itself as a successful outcome

#### Scenario: Reject the removed generic identity
- **WHEN** a projected integration is inspected after migration
- **THEN** no `zpp-workflow` skill or alias is present

### Requirement: Agent-declared stage outcomes
For `shape`, `plan-utilities`, `mature-utilities`, `wire`, and `form-specs`, the bounded stage skill SHALL declare either `completed` or `skipped: not applicable`. The active workflow SHALL obtain each declaration from a separate visible invocation of the exact stage skill; neither the workflow, `zpp-auto`, nor the kernel SHALL infer, combine, or manufacture it. `zpps-workflow-kernel` SHALL accept a skip only after independently observing the stage-specific evidence that no owned output is required. A selected trait, derived context value, repository declaration, caller assertion, another stage's result, or failed command SHALL NOT establish a skip. `clarify` and `finalize` SHALL remain mandatory and SHALL NOT accept a not-applicable outcome.

Before every stage action, the active workflow SHALL present a same-revision assessment naming the selected stage and component, complete ordered predecessor outcomes, invalid or stale evidence, accepted effects, stage-owned output, authority, and eligibility. The kernel SHALL audit only that caller-selected action. Before `wire` may be eligible, predecessor evidence SHALL contain separate actual results from both `zpps-planning-ponytail` and `zpps-mature-utilities` for the same contract revision. A planning skip SHALL NOT count as a maturation result or permit a direct jump to wiring.

#### Scenario: Skip feature shaping without public behavior
- **WHEN** the agent declares shape not applicable and the accepted change has no public or integration behavior requiring an executable feature contract
- **THEN** `zpps-shape-bdd` returns `skipped: not applicable` without creating a feature, the kernel assesses that result, and the playbook retains continuation selection

#### Scenario: Run a stage when evidence is uncertain
- **WHEN** an agent proposes a conditional-stage skip but the stage-specific evidence does not prove that no owned output is required
- **THEN** the kernel rejects the skip and the active playbook invokes its already declared stage action rather than treating the skip as progress

#### Scenario: Reject an inferred Ponytail skip
- **WHEN** a playbook requests wiring without a `zpps-planning-ponytail` result for the current accepted contract revision
- **THEN** the kernel blocks wiring and does not infer that utility planning was inapplicable

#### Scenario: Keep utility planning and maturation distinct
- **WHEN** `zpps-planning-ponytail` returns `skipped: not applicable`
- **THEN** the active workflow records only the `plan-utilities` outcome and separately invokes and assesses `zpps-mature-utilities` before it may request wiring

#### Scenario: Audit the complete predecessor chain
- **WHEN** a workflow requests a stage with a missing, stale, failed, contradicted, or superseded predecessor outcome
- **THEN** the kernel blocks that selected stage and reports the earliest invalid predecessor without choosing or invoking a replacement stage

#### Scenario: Reject a failed-stage skip
- **WHEN** a stage command or verification fails
- **THEN** the stage skill reports the failed gate and the kernel does not relabel it as not applicable

#### Scenario: Require mandatory boundary stages
- **WHEN** the workflow begins clarification or reaches finalization
- **THEN** the kernel requires that stage and rejects a not-applicable declaration

### Requirement: Explicit component delegation
A playbook SHALL invoke the exact configured ZPP phase or operation skill that owns each declared component use. A direct partial invocation MAY select the same component by supplying its required operation configuration. Before the first governed mutation for a change set, the playbook or directly invoked component SHALL pass the exact resolved repository roots and change names to `zpps-workflow-kernel`; the kernel SHALL invoke ZPP's runtime coordination operation and consume its structured guard without implementing registration, identity persistence, environment parsing, manifest preparation, or lease transitions in skill instructions. Missing internal store registration, store UUID, owner, or bundle identity SHALL trigger runtime preparation rather than an owner question. A preparation, override, or acquisition conflict SHALL remain blocked and visible. Repo-local roots remain valid for read-only work and existing `repo:` locator resolution.

During result assessment and finalization the kernel SHALL submit every exact changed path and archive result to the ZPP runtime. The runtime SHALL classify repository-local non-OpenSpec paths separately, submit only changed OpenSpec paths to Bundler's store-authority audit, preserve unknown-root and unheld-store violations, record archives, and complete the same bundle. Changed paths SHALL NOT be bundle members, and skills SHALL NOT manually reproduce the runtime classification. The component SHALL return its observed output and SHALL NOT select workflow continuation, advance the playbook sequence, expand the bundle, or claim lifecycle completion.

#### Scenario: Acquire without coordination questions
- **WHEN** an eligible phase has mutation authority and is about to perform the first governed OpenSpec mutation
- **THEN** the caller obtains the kernel's automatically prepared guard and exact Bundler bundle without asking the owner for registration, UUID, owner-string, or lease input

#### Scenario: Assess complete changed paths without false violations
- **WHEN** a component reports both OpenSpec and repository-local capability or test paths
- **THEN** the kernel submits the complete inventory to ZPP and accepts the result when the runtime audit reports held OpenSpec paths as audited and repository-local non-OpenSpec paths as ignored

#### Scenario: Pause on a genuine coordination conflict
- **WHEN** automatic preparation or acquisition reports an ambiguous registration, invalid manifest, topology error, or incompatible retained bundle
- **THEN** the component remains blocked with the concrete conflict and does not bypass coordination safety

#### Scenario: Complete after every member archives
- **WHEN** `zpps-archive-change` or an authorized `zpps-bulk-archive-change` operation has returned every declared member archive and the path audit passes
- **THEN** the kernel records every archive and completes the bundle using the retained ZPP-managed owner

#### Scenario: Reject operation continuation
- **WHEN** a bounded operation returns successful evidence
- **THEN** the kernel may assess that evidence but does not choose a continuation, and the operation itself does not continue to another stage
