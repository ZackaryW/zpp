# Consolidated Workflow Skill Specification

## Purpose

Define the packaged ZPP workflow entry family, its single lifecycle kernel, bounded stage and OpenSpec adapter skills, contextual trait consumption, and single executable acceptance authority.

## Requirements

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

### Requirement: Bounded workflow phase skills
ZPP SHALL package one substantive skill for each bounded stage: `clarify` as `zpps-clarify`, `shape` as `zpps-shape-bdd`, `plan-utilities` as `zpps-planning-ponytail`, `mature-utilities` as `zpps-mature-utilities`, `wire` as `zpps-wire`, `form-specs` as `zpps-form-specs`, and `finalize` as `zpps-finalize`. Each skill SHALL contain its complete trigger, required inputs, input-resolution rules, ordered procedure, stopping boundary, result fields, and failure behavior rather than acting as a thin kernel delegate or conceptual reference.

A stage, adapter, or evidence skill SHALL accept explicit operation configuration from a playbook or a direct partial invocation. It SHALL NOT reject work solely because no playbook or kernel delegated it. Read-only work MAY run directly through a registered store or repo-local OpenSpec root. Before governed mutation the component SHALL resolve an exact store UUID through the public registered-store list and an exact change member, present or request the current kernel guard, and acquire a Bundler lease containing only that store/change member. Without the UUID it SHALL return `store-registration-required` and remain blocked. Filesystem, repository, canonical, and archive paths SHALL NOT be lease members; the component SHALL return every exact changed path for kernel post-result audit together with its bounded status, unresolved questions, and observed evidence. A mutating phase SHALL mark only supplied OpenSpec tasks whose behavior its successful stage work and evidence fully satisfy and SHALL NOT check off a partial, unrelated, or merely attempted task. No component SHALL select workflow continuation, expand authority, authorize a checkpoint, or declare lifecycle completion. `zpps-explore` SHALL remain read-only even when invoked directly and SHALL hand an explicit planning-mutation request to the corresponding planning operation rather than silently creating or revising artifacts.

#### Scenario: Delegate Ponytail planning
- **WHEN** a playbook configures `zpps-planning-ponytail` with accepted behavior and repository evidence for `plan-utilities`
- **THEN** that substantive skill executes its complete bounded planning procedure and returns a utility-plan outcome without implementation or stage progression

#### Scenario: Invoke a phase directly
- **WHEN** a caller invokes a phase skill directly with the explicit inputs needed for its bounded operation and no prior kernel delegation
- **THEN** the phase executes read-only work directly or obtains only the required mutation guard and does not reject the invocation merely because it came from outside a playbook

#### Scenario: Explore without mutation
- **WHEN** a user or stage invokes `zpps-explore`
- **THEN** it may inspect stores, changes, specifications, repository evidence, traits, and memory but creates or changes no planning or product artifact

#### Scenario: Reject phase self-progression
- **WHEN** a phase skill finishes its bounded output
- **THEN** it returns evidence to its caller and does not select the next stage or claim completion

#### Scenario: Conformance trace for packaged stage order
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Bounded workflow phase skills","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Load entries kernel and stages in lifecycle order"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Load entries kernel and stages in lifecycle order`

### Requirement: Skill-owned invariant policy
Invariant workflow behavior SHALL reside in the kernel or its owning phase, adapter, and evidence skills rather than in packaged traits. `zpps-planning-ponytail` SHALL own the ordered Ponytail ladder; `zpps-clarify` and the kernel SHALL own zero-assumption reconciliation; `zpps-shape-bdd` SHALL own public-system binding invariants; `zpps-mature-utilities` SHALL own shared RED, minimum-slice, and GREEN behavior; `zpps-verify-change` SHALL own semantic change verification; and `zpps-verify-repository` SHALL own executable verification truthfulness and complete build-gate obligations.

The packaged standard trait collection SHALL remove `dependencies`, `build`, and `zero-assumptions`. It SHALL retain `bdd`, `bdd-execution`, and `tdd` only for contextual language, framework, or repository-selected mode specialization, and SHALL retain `bdd-structure` and `tooling` as contextual families. A retained trait SHALL NOT repeat, replace, or waive its skill-owned invariant.

#### Scenario: Apply Ponytail without a dependency trait
- **WHEN** utility planning is applicable in a repository with no injected dependency trait
- **THEN** `zpps-planning-ponytail` applies the complete ordered ladder before approving new code or a third-party package

#### Scenario: Consume contextual BDD specialization
- **WHEN** a retained BDD trait selects established Python structure
- **THEN** `zpps-shape-bdd` applies that layout advice under its invariant scenario-binding and public-system contract

#### Scenario: Conformance trace for contextual trait inventory
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Skill-owned invariant policy","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Load only contextual trait specialization"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Load only contextual trait specialization`

### Requirement: Complete bounded OpenSpec adapter set
ZPP SHALL package `zpps-explore`, `zpps-new-change`, `zpps-continue-change`, `zpps-ff-change`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-verify-change`, `zpps-sync-specs`, `zpps-archive-change`, and `zpps-bulk-archive-change` as its complete substantive OpenSpec adapter set. Every adapter SHALL preserve its upstream operation's complete input and change selection, registered-store resolution with sticky store identity, repo-local fallback, structured status and instruction discovery, current context/rule and dependency consumption, ordered work, prompts, stopping boundary, output summary, and failure behavior. It SHALL contain that procedure in its own skill body rather than forwarding the operation to the kernel or depending on an upstream generated skill.

The adapters SHALL preserve their distinct procedures: explore is read-only investigation; new scaffolds and stops before artifact creation; continue creates exactly one ready artifact; fast-forward always scaffolds a new change and creates its transitive apply-required planning set, returning a name collision for the caller to select continue separately rather than converting to existing-change continuation; propose reconciles material ambiguity and creates that complete planning set without implementation, stopping there when invoked standalone while an owner-authorized active playbook may consume its result and follow its declared branch; update changes existing planning artifacts only; apply implements and records pending tasks until done or blocked; verify returns a non-mutating completeness, correctness, and coherence report and returns `repository-evidence-required` when native evidence is missing or stale without invoking the repository verifier; sync performs selected-path, rules-aware, semantic, idempotent canonical merging and validation; single archive assesses one change and performs any selected sync synchronously before moving it; and bulk archive requires explicit selection, resolves exact-capability conflicts from implementation evidence, prefetches rule snapshots before mutation, synchronously syncs and verifies included deltas, and reports per-change and per-delta outcomes. Archive adapters MAY call `zpps-sync-specs` only for that explicit synchronous sub-operation.

Repo-local roots SHALL remain valid for adapter read-only discovery and verification and for resolving an existing `repo:` trace locator. Every mutating adapter SHALL require an exact registered store UUID/change member, return `store-registration-required` before mutation when it cannot resolve that UUID, and return every exact changed path for kernel post-result audit. Bundler membership SHALL contain no changed path.

ZPP SHALL explicitly exclude `openspec-onboard` and SHALL package no `zpps-onboard` because onboarding is an instructional walkthrough rather than an operational primitive. `zpps-verify-repository` SHALL be packaged separately as an executable-evidence component and SHALL NOT be classified as an OpenSpec adapter. ZPP SHALL contain no broad `zpps-plan-change`, `zpps-verify`, or `zpps-archive` compatibility identity.

#### Scenario: Conformance trace for OpenSpec adapter coverage
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Complete bounded OpenSpec adapter set","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Cover operational OpenSpec workflows without onboarding"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Cover operational OpenSpec workflows without onboarding`

#### Scenario: Preserve an adapter stopping boundary
- **WHEN** `zpps-continue-change` creates the next eligible artifact for a resolved change
- **THEN** it returns updated status without creating later artifacts or selecting workflow continuation

#### Scenario: Invoke an adapter directly
- **WHEN** a caller directly invokes a mutating adapter with explicit operation configuration but no prior kernel delegation
- **THEN** the adapter obtains only the guard and exact lease required for that selected operation, executes its own complete procedure, and returns without selecting another workflow operation

#### Scenario: Preserve synchronous archive synchronization
- **WHEN** a selected single or bulk archive procedure requires specification synchronization
- **THEN** the archive adapter invokes `zpps-sync-specs` synchronously, verifies the selected deltas, and does not move the change while synchronization is incomplete or failed

### Requirement: Immediate-operation component admission
Every packaged `zpps-*` discovery description and bounded procedure SHALL admit work from the caller's immediate necessary operation rather than from an eventual product outcome. When the next necessary work is to discover, compare, or validate unresolved external or repository evidence, admission SHALL select `zpps-explore` and remain read-only even if the caller ultimately intends a dependency, planning, implementation, synchronization, or archive mutation.

A mutating `zpps-*` component SHALL be eligible only when its exact bounded operation is already resolved and either the caller explicitly requests that mutation or an active playbook configures that exact component use. The existence of an active change, a mutating eventual outcome, an imperative verb, or pending tasks SHALL NOT independently admit a mutating component. If component admission remains ambiguous between read-only discovery and mutation, the workflow SHALL select read-only exploration or request one focused clarification before admitting mutation.

When an agent detects that the admitted component does not match the immediate operation, it SHALL report the mismatch to the caller immediately, stop using that component before performing further work, and preserve the result as a failed admission. Any continuation SHALL occur only through a separately admitted component; the misrouted component SHALL NOT reinterpret the request, yield a successful stage result, or continue merely because its internal procedure can inspect related evidence.

#### Scenario: Explore unresolved package integration evidence
- **WHEN** a caller ultimately wants to adopt published packages but the next necessary work is to discover their available versions and validate recent repository integration changes
- **THEN** the workflow admits `zpps-explore`, remains read-only, and does not admit `zpps-apply-change` from the eventual adoption outcome

#### Scenario: Admit an exact requested mutation
- **WHEN** the target and prerequisites of one bounded mutation are resolved and the caller explicitly requests that exact mutation or an active playbook configures it
- **THEN** the workflow may admit the matching mutating `zpps-*` component without treating earlier discovery as implementation authority

#### Scenario: Default ambiguous admission to read-only work
- **WHEN** a request does not establish whether its immediate bounded operation is evidence discovery or a resolved mutation
- **THEN** the workflow uses `zpps-explore` or one focused clarification and admits no mutating component

#### Scenario: Report a detected component mismatch first
- **WHEN** an agent detects that its admitted `zpps-*` component does not match the caller's immediate operation
- **THEN** it reports the failed admission immediately and stops that component before any separately admitted continuation

### Requirement: Single executable acceptance authority
For each accepted obligation, ZPP SHALL distinguish normative specification ownership from executable acceptance-example ownership. A testable public-system obligation SHALL have its concrete acceptance examples only in the independently runnable `features/<capability>/` root. `zpps-shape-bdd` SHALL transfer a provisional concrete OpenSpec example into that feature root, bind every resulting feature scenario to the exact OpenSpec store, capability, and requirement identity, and replace the concrete OpenSpec example within the same completed stage outcome with a trace-only conformance scenario that does not restate the executable behavior.

The binding identity SHALL be the exact ordered tuple `root`, `capability`, `requirement`, `feature`, and `scenario`, encoded on both sides as compact JSON with those keys in that order. Creating or changing a binding during shaping SHALL use `store:<uuid>` with the exact UUID discovered through the public registered-store list because that action is governed mutation. An existing binding MAY retain `repo:<git-root-relative-path-to-openspec-root>` for a repo-local OpenSpec root and SHALL remain resolvable during read-only discovery, formation audit, and verification without authorizing mutation or automatic locator migration. ZPP SHALL NOT generate a store UUID, derive one from a name, or replace an existing repo-local locator with a fabricated UUID. `capability` SHALL be the capability directory identity, `requirement` SHALL be the exact requirement heading, `feature` SHALL be the Git-root-relative feature path, and `scenario` SHALL be the exact Gherkin scenario title. The feature declaration SHALL appear immediately above that scenario, and the trace-only OpenSpec conformance scenario SHALL name the exact `<feature>::<scenario>` target with the identical tuple.

`zpps-form-specs` SHALL reject semantic acceptance duplication, an unresolved binding in either direction, a BDD-backed requirement without an executable feature scenario, or a spec-only requirement claimed by a feature scenario. It SHALL return canonical synchronization eligibility only after this audit; the invoking playbook or direct caller SHALL select `zpps-sync-specs` explicitly and then invoke `zpps-form-specs` for the resulting canonical audit. A pure-functionality case matrix SHALL remain in unit tests, with one public-system BDD scenario retained when needed to prove enforcement. An obligation with no executable public-system observation SHALL remain normative specification content and SHALL NOT cause a fabricated BDD scenario.

#### Scenario: Transfer a testable acceptance example
- **WHEN** shaping accepts a provisional OpenSpec example that can be observed through the public system
- **THEN** `zpps-shape-bdd` creates the bound capability feature scenario and leaves OpenSpec with normative requirement text plus a trace-only conformance scenario rather than the same executable example

#### Scenario: Reject duplicated acceptance authority
- **WHEN** specification formation finds semantically equivalent executable acceptance behavior in both an OpenSpec scenario and a bound feature scenario
- **THEN** `zpps-form-specs` blocks synchronization and identifies both authorities

#### Scenario: Preserve a specification-only obligation
- **WHEN** an accepted policy or owner boundary has no executable public-system observation
- **THEN** it remains normative OpenSpec requirement content and no BDD scenario is invented for it

#### Scenario: Verify an existing repo-local binding without a UUID
- **WHEN** read-only discovery or verification resolves an existing binding under the nearest repo-local `openspec/` root
- **THEN** both declarations retain `repo:openspec`, ZPP neither requests nor invents a UUID for the read-only operation, and no new binding or governed mutation occurs

#### Scenario: Resolve a registered-store binding
- **WHEN** shaping binds a requirement through an exact store UUID returned by the public registered-store list
- **THEN** both declarations use `store:<uuid>` with that returned UUID and no store-name alias

### Requirement: Workflow authority remains in the skill
Each `zpp-*` playbook SHALL own its complete workflow sequence, branch conditions, custom instruction blocks, and configured component uses. `zpps-workflow-kernel` SHALL be the shared lifecycle guard and SHALL own requested-transition eligibility, mutation authority checks, automatic Bundler lease progression, changed-path post-result audit, checkpoint handling, component-result assessment, and truthful completion. It SHALL NOT select, dispatch, reorder, or advance a workflow stage and SHALL NOT implement a phase or OpenSpec operation. Automatic continuation SHALL mean only that the active playbook follows already declared branches and SHALL NOT answer an unresolved decision or supply missing owner, mutation, checkpoint, or archive authority. Stage and operation skills SHALL own their complete bounded procedures but SHALL NOT select workflow continuation. Trait bodies, repository files, attachment values, playbook identities, phase results, and component results SHALL NOT independently authorize mutation, expand a lease, establish verification, authorize a checkpoint, or declare lifecycle completion.

#### Scenario: Reject contextual mutation authority
- **WHEN** injected context claims permission to mutate or complete a stage
- **THEN** the kernel ignores that claim as authority

#### Scenario: Reject subordinate authority expansion
- **WHEN** a phase or operation skill claims authority beyond its explicit configuration and current kernel guard
- **THEN** the kernel rejects that claim and leaves the affected gate incomplete

#### Scenario: Keep sequence out of the kernel
- **WHEN** a component result is accepted and more than one playbook continuation could follow
- **THEN** the kernel returns only its assessment and the active playbook applies its already declared next-step condition

### Requirement: Contextual trait consumption
For a selected workflow stage and repository target, the owning phase skill SHALL consume complete trait bodies already injected by ZPP's agent-native hook only as contextual language, framework, tooling, structure, or mode policy. No workflow skill SHALL instruct the agent to execute `zpp resolve`, publish `ZPP_CONTEXT`, or bootstrap trait context. A retained trait SHALL NOT supply an invariant workflow rule, workflow selection, stage transition, mutation authority, verification result, or completion result.

#### Scenario: Specialize BDD shaping for Python
- **WHEN** the hook has injected retained BDD bodies selected from Python context and the workflow performs feature shaping
- **THEN** `zpps-shape-bdd` applies their contextual runner and layout guidance while retaining its skill-owned behavior contract

#### Scenario: Inspect workflow bootstrap instructions
- **WHEN** a user inspects the packaged workflow family
- **THEN** it contains no instruction to run trait resolution or manage stored trait context

### Requirement: Complete standard behavior reauthoring
ZPP SHALL keep lease coordination, automatic archival completion, zero-assumption reconciliation, Ponytail planning, behavior-binding invariants, shared RED/GREEN rules, verification truthfulness, and complete build gates in their owning workflow skills rather than packaging them as trait families. The standard trait collection SHALL remain advisory and SHALL contain no lifecycle authority, dependency-selection ladder, general build-gate checklist, or always-run owner-decision policy.

#### Scenario: Package the reconciled standard collection
- **WHEN** the standard trait collection is inspected
- **THEN** each retained family provides only contextual specialization and no removed invariant or coordination family remains

### Requirement: Explicit stage actions
Each `zpp-*` playbook SHALL declare every stage or component use as an explicit ordered Markdown action with its input configuration, eligibility condition, accepted result, and next-step branch. It SHALL NOT infer an undeclared later stage from OpenSpec status, repository files, stored descriptive context, trait output, or a skill identity. A playbook MAY declare `clarify` when no later stage was explicitly selected. When automatic continuation is authorized and the current component result has converged, the playbook SHALL apply its own declared condition and explicitly request the next kernel assessment. That authorization SHALL NOT answer unresolved decisions or provide missing owner, mutation, checkpoint-commit, or archive authority. Triage components, traits, the kernel, phase skills, and operation skills SHALL NOT select or advance the playbook sequence.

#### Scenario: Default an entry to clarification
- **WHEN** a workflow invocation identifies no later requested stage
- **THEN** the selected playbook declares `clarify` rather than inferring progress from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes or truthfully skips one conditional stage and continues
- **THEN** the active playbook follows its declared branch and requests the next named action explicitly

### Requirement: Complete agreement reconciliation before convergence
During clarification, `zpps-clarify` SHALL classify each newer owner prompt as an explicit confirmation, correction, recommendation, exploration, or deferral and SHALL reconcile it against canonical specifications, the complete older accepted owner input for the current change, the proposal, every capability delta, downstream checkpoints, and current repository evidence before changing normative behavior. A newer statement SHALL NOT silently replace or contradict an older accepted statement merely because it is newer. Assistant recommendations, inferred preferences, default choices, and automatic end-to-end delegation SHALL NOT count as owner confirmation.

For every outcome-changing decision that remains unresolved after that reconciliation, `zpps-clarify` SHALL ask the owner one to three focused questions at a time. Each question SHALL identify the exact missing decision and its meaningful consequences; when bounded alternatives exist, it SHALL present concrete mutually exclusive choices, and otherwise it SHALL ask one precise open question. `zpps-clarify` SHALL use the active agent's structured user-question mechanism when available and SHALL ask the same focused question directly when it is unavailable. It SHALL wait for an explicit owner answer and SHALL NOT treat a vague request such as “can you clarify?”, an unanswered recommendation, or a presumed default as resolution.

When an apparent agreement conflicts with older accepted input or leaves a product behavior, constraint, serialization, or owner boundary unsettled, `zpps-clarify` SHALL record the contradiction under `Unresolved — Do Not Assume`, remove the unconfirmed outcome from normative deltas, ask the focused owner question needed to resolve it, and keep clarification open. The unresolved record SHALL NOT substitute for asking. After each explicit owner answer, `zpps-clarify` SHALL reconcile the complete agreement again and SHALL repeat the question loop until no outcome-changing owner decision remains. If downstream feature, utility, wiring, or specification gates were formed from an unconfirmed outcome, `zpps-clarify` SHALL invalidate them and require replacement gates after explicit owner confirmation.

#### Scenario: Keep a recommendation unresolved
- **WHEN** the owner describes one design as a recommendation without explicitly confirming its complete public contract
- **THEN** the skill records that preference as unresolved, asks the focused question needed for confirmation, and does not promote it into a normative capability delta

#### Scenario: Reconcile a newer correction with older input
- **WHEN** a newer prompt changes one part of the design while older accepted requirements remain in force
- **THEN** the skill reconciles both across the proposal and every affected delta and asks about any remaining contradiction before continuing

#### Scenario: Refuse automatic delegation as design authority
- **WHEN** the owner authorizes automatic end-to-end execution while a product decision remains unresolved
- **THEN** the skill pauses at clarification and asks the owner rather than choosing the decision in order to continue

#### Scenario: Invalidate a gate built from an assumption
- **WHEN** a downstream feature contract was formed from an assistant-inferred decision that the owner did not confirm
- **THEN** the skill marks that gate superseded and requires a replacement feature checkpoint after clarification converges

#### Scenario: Ask a bounded focused question
- **WHEN** repository evidence leaves an outcome-changing decision with bounded alternatives unresolved
- **THEN** the skill asks one focused question with concrete mutually exclusive choices and meaningful consequences instead of making a vague clarification request

#### Scenario: Fall back from an unavailable question mechanism
- **WHEN** the active agent does not expose a structured user-question mechanism
- **THEN** the skill asks the same focused question directly, waits for an explicit answer, and does not weaken or bypass clarification

#### Scenario: Repeat until clarification converges
- **WHEN** an owner answer resolves one question but another outcome-changing decision remains unresolved
- **THEN** the skill reconciles the complete agreement and asks the next focused question batch before declaring clarification complete

#### Scenario: Avoid asking about established evidence
- **WHEN** current specifications, accepted input, and repository evidence already settle a possible clarification point
- **THEN** the skill preserves that established outcome and does not ask the owner to decide it again

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

### Requirement: Automatic Bundler workflow boundary
The packaged workflow family SHALL describe repository/change targets in ZPP terms, delegate automatic preparation and Bundler progression to ZPP's runtime through `zpps-workflow-kernel`, and never ask the owner to choose or type an OpenSpec store registration, store UUID, durable owner string, bundle UUID, environment override, or lease command during ordinary authorized execution. Skills SHALL neither parse `ZPP_WORKFLOW_COORDINATION` nor implement a bypass. They SHALL preserve explicit mutation, archive, and bypass authority, surface runtime coordination conflicts, and contain no OpenLease name, workspace-management delegation, session, claim, permit, successor, reconciliation, handoff, cleanup, or preparation-repair guidance.

#### Scenario: Inspect seamless workflow coordination guidance
- **WHEN** the packaged workflow family is inspected
- **THEN** it delegates registration, identity, override, and bundle progression to the ZPP runtime while preserving visible authority and conflict boundaries

### Requirement: BDD-target canonical specification formation
During `form-specs`, `zpps-form-specs` SHALL replace the repeated body of each OpenSpec scenario with a trace-only conformance scenario when, and only when, an accepted BDD feature scenario is its executable authority. The trace SHALL repeat the exact five-field binding declaration, identify `<git-root-relative-feature-path>::<exact-scenario-name>`, belong to the same capability owner, resolve to the requirement in both directions, use scenario-selected bindings that exercise the named behavior through the public system, and have relevant passing verification. The trace-only OpenSpec scenario SHALL state that the exact feature scenario is executable authority and SHALL NOT repeat its Given/When/Then behavior.

Every scenario without qualifying BDD coverage SHALL remain a complete OpenSpec WHEN/THEN scenario. A stale, missing, cross-capability, mismatched-tuple, recorder-only, capability-wide, wording-only, or unverified target SHALL block specification formation rather than justify scenario removal.

#### Scenario: Replace duplicated behavior with an exact BDD target
- **WHEN** an OpenSpec scenario has a verified same-capability five-field binding to an exact feature scenario
- **THEN** canonical formation retains one trace-only OpenSpec scenario naming that exact target and removes the duplicated executable steps

#### Scenario: Preserve a non-BDD specification scenario
- **WHEN** an accepted OpenSpec scenario has no qualifying executable BDD target
- **THEN** canonical formation preserves its complete WHEN/THEN contract in OpenSpec and does not invent feature coverage

#### Scenario: Reject invalid feature authority
- **WHEN** a proposed target is absent, stale, owned by another capability, untraced, unbound, recorder-only, capability-wide, wording-only, or lacks passing relevant verification
- **THEN** canonical formation keeps the specification scenario and leaves `form-specs` incomplete

### Requirement: Consume only ZPP-provisioned OpenSpec operation skills
The workflow family SHALL consume the exact installed ZPP-owned phase and operation skills required by the current stage and SHALL use the installed OpenSpec executable only through its public store, status, artifact-instruction, validation, synchronization, and archive interfaces. It SHALL NOT invoke a generated `openspec-*` skill as workflow authority, invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, repair an operation skill, or create a substitute operation owner in the target repository or any other location.

When a required packaged ZPP skill is absent, unreadable, invalid, or stale, the invoking playbook or direct caller SHALL leave the selected operation blocked, identify that integration boundary, and direct the owner to root `zpp init` for an uninitialized ZPP integration or root `zpp sync` for an existing integration. When the `openspec` executable or a required public interface is absent, failed, or unsupported, the invoked adapter SHALL block before governed mutation and report that runtime dependency directly; ZPP lifecycle commands SHALL NOT be presented as an OpenSpec installer or repair path. Neither the kernel nor an adapter SHALL invoke a lifecycle command on the owner's behalf. Ordinary repo-local planning state under `openspec/` SHALL remain allowed and SHALL NOT be treated as skill installation.

#### Scenario: Use a ZPP-owned planning operation
- **WHEN** an eligible stage requires planning mutation and the exact new, continue, fast-forward, propose, or update adapter plus the required public OpenSpec interfaces are available
- **THEN** the playbook invokes that exact substantive adapter under the kernel guard without invoking a generated OpenSpec skill or changing skill installation

#### Scenario: Block a missing operation owner
- **WHEN** the required ZPP phase or operation skill is absent or invalid
- **THEN** the caller leaves the operation blocked and directs the owner to the appropriate ZPP initialization or synchronization command without invoking it

#### Scenario: Block a missing OpenSpec runtime
- **WHEN** the delegated adapter cannot invoke its required public OpenSpec interface
- **THEN** it blocks before governed mutation and reports the runtime dependency without directing ZPP lifecycle to install or repair OpenSpec

#### Scenario: Reject a local initialization prerequisite
- **WHEN** an operation path proposes `openspec init`, a generated local skill tree, or project-scope skill projection as a prerequisite
- **THEN** the workflow rejects that path and creates, copies, installs, projects, or repairs no OpenSpec operation skill

#### Scenario: Preserve repository planning operations
- **WHEN** a ZPP-owned skill creates, updates, validates, synchronizes, or archives ordinary state under the repository's `openspec/` directory
- **THEN** the workflow treats that state as allowed product planning rather than prohibited skill bootstrap

### Requirement: Evidence-based stage eligibility assessment
Before a playbook or direct caller invokes any workflow stage, `zpps-workflow-kernel` SHALL present an explicit eligibility assessment for the current accepted contract revision. The assessment SHALL identify the explicitly requested stage, the current evidence-backed outcome of every predecessor stage, any missing, stale, failed, or superseded checkpoint, and the output the requested stage owns for the accepted change. A stage name supplied by an owner or proposed by an agent SHALL be requested-assessment input only and SHALL NOT satisfy the stage's eligibility, any predecessor gate, verification, or mutation authority.

The kernel SHALL block a requested stage when any required predecessor outcome is absent, stale, failed, or derived from a superseded contract. It MAY identify the earliest unsatisfied predecessor but SHALL NOT execute it or choose it as the next action. Under separately authorized end-to-end continuation, only the active playbook MAY follow its already declared branch and request a new assessment for that predecessor. A changed contract SHALL return to clarification and invalidate every downstream assessment derived from the older contract revision.

#### Scenario: Reject a named stage with an unsatisfied predecessor
- **WHEN** an owner or agent names a later workflow stage but a required predecessor has no current evidence-backed outcome
- **THEN** the workflow reports the requested stage as blocked and does not treat its name as gate satisfaction

#### Scenario: Reject stale checkpoint evidence
- **WHEN** a newer accepted contract changes an outcome from which downstream stage assessments were derived
- **THEN** the workflow reopens clarification and refuses to execute those stages until replacement predecessor outcomes are established

#### Scenario: Preserve explicit invocation after identifying a blocker
- **WHEN** an eligibility assessment identifies the earliest unsatisfied predecessor without separate end-to-end progression authority
- **THEN** the workflow reports that predecessor but does not execute it until the owner explicitly invokes the stage

### Requirement: Effect-based conditional-stage applicability
When a playbook requests assessment of `shape`, `plan-utilities`, `mature-utilities`, or `wire`, `zpps-workflow-kernel` SHALL classify the complete accepted change by its effects: externally observable public or integration behavior, pure executable utility behavior, executable artifact processing or update behavior, spec-governed prose, and ungoverned artifact text. It SHALL use that classification only to accept or reject the requested stage's eligibility or not-applicable result from the output that stage owns. It SHALL NOT select a stage or infer test obligations from a filename, artifact category, selected trait, or generic workflow convention.

A change limited to spec-governed skill prose, environment guidance, or equivalent declarative instructions SHALL require no Gherkin, BDD execution, utility plan, unit TDD, or product wiring. Such a change SHALL still complete `form-specs` when an accepted delta requires canonical reconciliation. A change to executable loading, parsing, validation, conversion, projection, or update mechanics SHALL remain eligible for behavior or unit verification at its actual executable boundary and SHALL NOT be skipped merely because it operates on a skill or environment artifact.

#### Scenario: Skip behavior and utility work for governed prose
- **WHEN** an accepted change alters only spec-governed skill prose or environment guidance and changes no executable behavior
- **THEN** `shape`, `plan-utilities`, `mature-utilities`, and `wire` are each assessed as `skipped: not applicable` without creating Gherkin, BDD, a utility plan, unit tests, or bindings

#### Scenario: Reconcile governed prose specifications
- **WHEN** a prose-only spec-governed artifact change contains an accepted capability delta
- **THEN** `form-specs` remains required even though behavior and utility stages are not applicable

#### Scenario: Test executable artifact update behavior
- **WHEN** an accepted change alters executable loading, validation, projection, or update mechanics for a skill or environment artifact
- **THEN** the workflow assesses the relevant behavior or utility stages from that executable boundary instead of skipping them because of the artifact label

### Requirement: Verified incremental checkpoint commits
Before declaring any workflow stage `completed` when that stage owns a non-empty
coherent diff, `zpps-workflow-kernel` SHALL invoke the exact installed
`zmem-author-commits` skill and complete its authorized commit workflow. The
acting agent SHALL identify the accepted contract revision, the stage-owned
diff, applicable stage verification and its observed result, checkpoint commit
authority, and the exact paths or hunks proposed for staging. It SHALL preserve
unrelated working-tree changes.

The commit series SHALL be dependency ordered and SHALL separate distinct
responsibilities when each intermediate commit is independently coherent and
verifiable. It SHALL NOT create a split whose intermediate state is known to
break the repository. Before each commit, the agent SHALL complete the
stage-appropriate verification and validate the complete proposed message using
zmem. After each authorized commit, it SHALL record the resulting SHA and inspect
the commit with `zmem show`. The `zmem-author-commits` operation SHALL decide
whether durable memory warrants an annotation; a checkpoint SHALL NOT require a
meaningless annotation.

Explicit end-to-end workflow delegation SHALL grant checkpoint commit authority
for the new commits produced by the playbook's automatically continued stage series. A
standalone stage action SHALL require separately granted commit authority. This
authority SHALL NOT include amend, merge, rebase, push, conflict reconciliation,
callback selection, or inclusion of unrelated work. Missing commit authority or
any failed verification, zmem validation, commit, or post-commit inspection SHALL
leave a material gate incomplete.

A skipped stage or a stage with no stage-owned diff SHALL record its observed
outcome without creating an empty commit. At finalization, the workflow SHALL
verify that every material completed gate has its checkpoint evidence, archive
the OpenSpec change, and commit only the remaining finalization-owned diff. It
SHALL NOT collapse or replace the preceding checkpoint series.

#### Scenario: Commit a material stage gate
- **WHEN** a workflow stage owns a non-empty coherent diff and checkpoint commit authority is present
- **THEN** the workflow verifies the stage-owned work, follows `zmem-author-commits`, creates the validated commit series from only its explicit paths or hunks, and records each inspected SHA before declaring the stage completed

#### Scenario: Skip an empty checkpoint
- **WHEN** a stage is skipped as not applicable or completes with no stage-owned diff
- **THEN** the workflow records the observed stage outcome without creating an empty commit

#### Scenario: Pause without commit authority
- **WHEN** a material stage has verified work but its invocation carries no checkpoint commit authority
- **THEN** the workflow leaves the gate incomplete and pauses before creating a commit

#### Scenario: Carry end-to-end checkpoint authority
- **WHEN** the owner explicitly delegates the workflow end to end
- **THEN** automatic progression may create each required stage checkpoint commit without requesting ordinary per-commit approval and gains no authority for other Git operations

#### Scenario: Preserve unrelated work
- **WHEN** the working tree contains changes outside the material stage-owned diff
- **THEN** the checkpoint stages only its explicit paths or hunks and leaves the unrelated changes untouched

#### Scenario: Split only coherent responsibilities
- **WHEN** one material gate contains multiple distinct responsibilities
- **THEN** the workflow commits them in dependency order when every intermediate state is coherent and verifiable and keeps them together when a split would knowingly break the repository

#### Scenario: Reject a failed checkpoint
- **WHEN** stage verification, zmem message validation, commit creation, or resulting-commit inspection fails
- **THEN** the workflow reports the failure and does not declare the material gate completed

#### Scenario: Keep annotations selective
- **WHEN** a checkpoint commit contains no durable decision, lesson, decay, cancellation, or registered custom memory
- **THEN** `zmem-author-commits` validates an ordinary human-readable commit message without requiring an annotation

#### Scenario: Finalize an incremental series
- **WHEN** all pre-finalization stages have observed outcomes and the change reaches finalization
- **THEN** the workflow verifies every material checkpoint, archives the change, and commits only remaining finalization-owned work without collapsing the earlier commits

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

### Requirement: Explicit behavior verification consumption
When an accepted shaped BDD obligation requires repository integration verification, `zpps-verify-repository` SHALL apply the resolved `bdd-execution` body only as advisory mode selection and SHALL invoke an established native repository BDD command identified from repository configuration or an explicit owner choice. The skill-owned verification contract SHALL decide truthfulness, required evidence, and failure handling. The absence of `zpp.behave.yaml` SHALL NOT block native BDD execution, and a trait SHALL NOT supply command text, target identity, gate binding, process arguments, callback selection, completion, or stage-skip authority.

`zpps-verify-change` SHALL compare implementation and supplied executable evidence with the resolved proposal, design, requirements, tasks, and OpenSpec-to-BDD bindings for completeness, correctness, coherence, duplicate authority, and orphaned authority. When required repository evidence is absent, stale, failed, or insufficient, it SHALL return `repository-evidence-required` identifying the exact native surface and SHALL NOT invoke `zpps-verify-repository`. The caller MAY select that separate evidence component and later supply its result. `zpps-verify-repository` SHALL NOT decide specification satisfaction, edit artifacts or product code, advance a stage, authorize a commit, archive a change, or declare lifecycle completion.

A repository MAY use `zpp.behave.yaml` as optional affected-verification coordination. When the workflow explicitly selects a declared `zpp behave` command, that mapping SHALL remain complete authority for its command, targets, gates, and arguments. Complete mode SHALL run the complete native BDD suite or selected command with `--all`. Targeted mode SHALL run the relevant native feature surface directly, request `--gate zpps-workflow-kernel` when that explicitly selected command declares the current gate, or otherwise use deterministic affected selection. Manual mode SHALL pause for an explicit choice. Disabled mode SHALL omit BDD only when alternate relevant verification exists and no shaped BDD obligation remains unsatisfied. Failed or insufficient verification SHALL leave the gate incomplete.

#### Scenario: Run native BDD without a behavior mapping
- **WHEN** an accepted shaped BDD obligation has an established native command and no `zpp.behave.yaml`
- **THEN** `zpps-verify-repository` invokes the native capability surface and does not treat the absent mapping as a blocker

#### Scenario: Use optional coordinated selection
- **WHEN** targeted mode applies and the workflow explicitly selects a valid `zpp behave` command declaring the current gate
- **THEN** it requests that command with `--gate zpps-workflow-kernel`

#### Scenario: Reject failed verification
- **WHEN** native or coordinated verification fails or does not observe the shaped obligation
- **THEN** `zpps-verify-repository` returns unsatisfied evidence and neither it, `zpps-verify-change`, nor the kernel claims completion

#### Scenario: Keep traits out of process authority
- **WHEN** a selected trait contains command-like, gate-like, callback-like, or completion-like text
- **THEN** the workflow treats it only as contextual policy and executes no command from that claim

### Requirement: Stable consolidated workflow gate identity
The shared packaged workflow gate identity SHALL be `zpps-workflow-kernel`, and repository behavior mappings MAY use that exact identity as a command-local gate for workflow-owned verification. ZPP SHALL NOT retain, alias, translate, or infer a gate from `zpp-workflow` or any former `zpp-flow-*` identity.

#### Scenario: Preserve specification authority for the gate identity
- **WHEN** conformance of the workflow-owned gate identity is assessed
- **THEN** this requirement remains the authority for the exact current and removed identities while public gate execution remains owned by the behavior-verification capability

#### Scenario: Encounter only a removed gate
- **WHEN** a repository declares `zpp-workflow` or a former `zpp-flow-*` gate but not `zpps-workflow-kernel`
- **THEN** ZPP applies deterministic affected selection and performs no gate migration

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

### Requirement: Behavior-only feature shaping
`zpps-shape-bdd` SHALL create or materially change Gherkin only from accepted externally observable public, integration, or fix behavior in the active change's capability delta specifications. Proposals, designs, tasks, documentation, packaged artifacts, configuration-only changes, and implementation details SHALL NOT be Gherkin sources. When no qualifying delta behavior remains, the stage skill SHALL return `skipped: not applicable` and SHALL NOT create or change a feature.

When qualifying behavior exists, every created or materially changed scenario SHALL trace to at least one such delta obligation, and every such obligation SHALL have scenario coverage or a concrete non-BDD classification. Obligations MAY split or combine without copied wording. An untraced scenario, uncovered obligation, or unresolved classification SHALL block shape completion.

#### Scenario: Skip artifact-only feature shaping
- **WHEN** an active change contains only proposals, designs, tasks, documentation, packaged artifacts, configuration, or implementation work and no qualifying behavior delta
- **THEN** the workflow records `shape` as not applicable and creates or changes no Gherkin feature

#### Scenario: Complete behavior-delta feature shaping
- **WHEN** an active capability delta contains accepted externally observable behavior
- **THEN** every created or materially changed scenario traces to that behavior and every behavior obligation has scenario coverage or a concrete non-BDD classification before shape completes

#### Scenario: Reject an untraced scenario or coverage gap
- **WHEN** a proposed scenario lacks a qualifying delta source or a qualifying behavior obligation lacks coverage or classification
- **THEN** the workflow keeps shape incomplete instead of inventing or silently omitting behavior

### Requirement: Behavior-only TDD shaping
`zpps-mature-utilities` SHALL create or change TDD tests only for executable behavior. Artifact loading, unloading, parsing, validation, and conversion into runtime classes or models SHALL be eligible TDD subjects. Tests whose only purpose is to pin prose or assert arbitrary artifact wording SHALL NOT be created. When no executable utility behavior remains, the stage skill SHALL return `skipped: not applicable` and SHALL NOT create or change a unit test.

#### Scenario: Skip artifact-wording TDD
- **WHEN** an active change changes artifact prose or wording but introduces no executable utility behavior
- **THEN** the workflow records `mature-utilities` as not applicable and creates or changes no unit test

#### Scenario: Apply TDD to artifact processing behavior
- **WHEN** an accepted change requires new or changed artifact loading, unloading, parsing, validation, or runtime class conversion behavior
- **THEN** the workflow uses TDD to prove that executable behavior without pinning unrelated artifact wording

### Requirement: Bounded artifact-only maintenance route
`zpp-auto` SHALL classify a requested outcome before requiring a workflow stage and MAY route a change limited to ungoverned non-runtime artifacts directly to its owning artifact guidance without creating an OpenSpec change, Gherkin, a utility plan, TDD, or workflow-stage outcomes. Ungoverned artifacts SHALL be limited to repository README and reference documentation, repository-local ZPP traits and context, and commit metadata.

The route SHALL NOT apply to a spec-governed packaged artifact. Any packaged workflow skill document, a packaged trait document, and a canonical OpenSpec specification SHALL be spec-governed because a canonical requirement describes their content as observable behavior. A change to a spec-governed artifact SHALL use the product workflow and SHALL reconcile canonical specifications before finalization, whether or not it changes executable behavior.

Classification SHALL follow effect rather than filename. Artifact loading, parsing, validation, class conversion, and any artifact-backed change to executable or public behavior SHALL use the product workflow. For a mixed change, `zpp-auto` SHALL route the behavioral portion to the product workflow while keeping supporting ungoverned artifact text out of BDD and TDD obligations.

#### Scenario: Route ungoverned artifact maintenance directly
- **WHEN** a requested change is limited to repository README or reference documentation, repository-local ZPP traits or context, or commit metadata
- **THEN** the skill edits through the owning artifact guidance and creates no OpenSpec change, feature, utility plan, unit test, or stage outcome

#### Scenario: Refuse the route for a packaged workflow skill
- **WHEN** a requested change alters any packaged workflow skill document or a packaged trait document and changes no executable behavior
- **THEN** the skill treats it as a spec-governed product change and does not accept artifact-only maintenance as its route

#### Scenario: Reconcile canonical specifications for a spec-governed artifact
- **WHEN** a spec-governed packaged artifact change reaches finalization
- **THEN** the canonical specification describing that artifact's content has been reconciled with the shipped wording and an unreconciled divergence blocks finalization

#### Scenario: Classify a mixed change by effect
- **WHEN** a requested change alters ungoverned artifact text alongside executable or public behavior
- **THEN** the workflow governs the behavioral portion and the supporting ungoverned text creates no BDD or TDD obligation

### Requirement: Monorepo behavior ownership
In a monorepo, `zpps-shape-bdd` SHALL shape and bind Gherkin only at an established public application or composition owner and only through that owner's real composed entry point. A reusable implementation subpackage SHALL own focused fail-first unit TDD rather than a feature-level acceptance contract. Public BDD MAY compose those subpackages but SHALL NOT replace their unit tests.

`zpps-shape-bdd` SHALL determine package topology and dependency direction by direct inspection and SHALL NOT encode repository structure as behavior tests. When the owning application or composition boundary for accepted behavior is unresolved, it SHALL expose that ownership question to its owner rather than selecting a boundary.

#### Scenario: Shape behavior at the composition owner
- **WHEN** accepted behavior in a monorepo belongs to an established public application or composition owner
- **THEN** the workflow shapes and binds its Gherkin at that owner through its real composed entry point

#### Scenario: Keep subpackage contracts as unit TDD
- **WHEN** accepted behavior belongs to a reusable implementation subpackage rather than a public composition owner
- **THEN** the workflow proves it with focused fail-first unit TDD and creates no feature-level acceptance contract for that subpackage

#### Scenario: Refuse to encode repository structure as behavior
- **WHEN** a proposed scenario would assert package topology or dependency direction
- **THEN** the workflow verifies that structure by direct inspection instead of creating the scenario

#### Scenario: Expose unresolved package ownership
- **WHEN** the owning application or composition boundary for accepted behavior cannot be established from repository evidence
- **THEN** the workflow exposes the ownership question to its owner rather than selecting a boundary

### Requirement: Scenarios bind to executable public-system verification
Every scenario `zpps-shape-bdd` creates or retains SHALL bind to executable verification that exercises the described behavior through the public system. A step implementation that records its own phrase, asserts only that it executed, or observes no system state SHALL NOT satisfy that binding obligation. Verification SHALL be selected by the scenario it serves, and a capability-wide assertion block that runs identically after every scenario in its root SHALL NOT establish scenario coverage.

An obligation that can be expressed only as prose SHALL be recorded as a canonical specification requirement and SHALL NOT be represented by an executable feature scenario. Verification SHALL NOT assert the literal wording of an artifact whose content a canonical requirement already governs. When accepted behavior has no executable public-system observation, `zpps-shape-bdd` SHALL record that obligation as non-BDD with a concrete reason rather than creating an unbound scenario.

`zpps-shape-bdd` SHALL state this binding obligation as its invariant contract. Retained BDD traits SHALL remain contextual and SHALL NOT repeat, replace, waive, or supply a command, target, or completion authority for that contract.

#### Scenario: Reject a recording-only binding
- **WHEN** a scenario's steps record their own phrases or assert only that they executed
- **THEN** the workflow treats the scenario as unbound and does not count it as behavior coverage

#### Scenario: Reject capability-wide assertion blocks as coverage
- **WHEN** a capability's verification runs the same assertions after every scenario in its root
- **THEN** the workflow does not accept those assertions as per-scenario coverage and requires verification selected by the scenario it serves

#### Scenario: Route a prose-only obligation to specification
- **WHEN** an accepted obligation has no executable public-system observation
- **THEN** the workflow records it as a canonical specification requirement or a concrete non-BDD classification and creates no scenario for it

#### Scenario: Refuse to assert governed artifact wording
- **WHEN** proposed verification would assert the literal wording of an artifact already governed by a canonical requirement
- **THEN** the workflow relies on the canonical requirement and does not create that assertion

#### Scenario: Receive the binding obligation from the shaping skill
- **WHEN** a playbook configures `zpps-shape-bdd` with a qualifying public-system obligation under the current kernel guard
- **THEN** the shaping skill applies its scenario binding obligation without accepting command, target, or completion authority from a trait
