## ADDED Requirements

### Requirement: Outcome workflow entry family
ZPP SHALL distribute `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, and `zpp-legacy-workflow` as complete user-invokable Markdown playbooks. Each playbook SHALL state its complete ordered sequence and branch conditions by interleaving workflow-specific custom instruction blocks with explicit configured uses of exact `zpps-*` components. A playbook SHALL NOT defer its sequence or next-component selection to `zpps-workflow-kernel`, a shared hidden stage list, or an implicit convention. `zpp-legacy-workflow` SHALL preserve the generic product-workflow outcome of the former `zpp-workflow` identity while using the current bounded components and kernel guards. ZPP SHALL remove the `zpp-workflow` skill identity without an alias.

`zpp-auto` SHALL contain the complete ordered non-mutating triage procedure. It SHALL invoke exactly one matching specialized playbook for an unambiguous request and SHALL invoke `zpp-legacy-workflow` at `clarify` for mixed, unsupported, or unresolved intent. It SHALL pass the original request, accepted classification evidence, and only owner-supplied authority to that playbook, transfer control exactly once, and not return to triage after the invocation. Merely reporting the selected playbook and stopping SHALL NOT satisfy the route. A playbook SHALL preserve only authority explicitly supplied by the owner and SHALL NOT grant mutation or checkpoint-commit authority by selecting a route.

#### Scenario: Route a clear defect correction
- **WHEN** `zpp-auto` receives an unambiguous request to correct a defect
- **THEN** it invokes `zpp-fix-bug` exactly once with the original request and supplied authority, rather than merely naming the route or mutating governed state itself

#### Scenario: Route unresolved intent to the legacy workflow
- **WHEN** `zpp-auto` cannot select exactly one specialized outcome
- **THEN** it delegates to `zpp-legacy-workflow` at `clarify` rather than inventing a workflow kind

#### Scenario: Reject the removed generic identity
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

## MODIFIED Requirements

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

### Requirement: Explicit component delegation
A playbook SHALL invoke the exact configured ZPP phase or operation skill that owns each declared component use. A direct partial invocation MAY select the same component by supplying its required operation configuration. Before the first governed mutation for a change set, the playbook or directly invoked component SHALL resolve exact registered store UUID/change members through the public store list and request ZPP's minimal Bundler lease bridge through the kernel with its durable owner and only those exact members. If no exact UUID resolves, the component SHALL return `store-registration-required` and remain blocked. Repo-local roots remain valid for read-only work and existing `repo:` locator resolution but do not satisfy mutation acquisition. During finalization the kernel SHALL post-audit every exact changed path returned by the components, record archives, and complete that same bundle; changed paths SHALL NOT be bundle members. The component SHALL return its observed output and SHALL NOT select workflow continuation, advance the playbook sequence, expand the bundle, or claim lifecycle completion.

#### Scenario: Acquire before governed mutation
- **WHEN** an eligible phase is about to perform the first governed OpenSpec mutation
- **THEN** the caller obtains the kernel's guard and exact Bundler bundle before that component mutates

#### Scenario: Complete after every member archives
- **WHEN** `zpps-archive-change` or an authorized `zpps-bulk-archive-change` operation has returned every declared member archive and the path audit passes
- **THEN** the kernel records every archive and completes the bundle

#### Scenario: Reject operation continuation
- **WHEN** a bounded operation returns successful evidence
- **THEN** the kernel may assess that evidence but does not choose a continuation, and the operation itself does not continue to another stage

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

### Requirement: No legacy workflow compatibility
`zpp-legacy-workflow` SHALL be the renamed generic ZPP 2 complete playbook and SHALL contain its ordered generic procedure using current subordinate skills and kernel guards. Its legacy name SHALL NOT authorize, translate, require, or preserve any ZPP 1.x `zpp-flow-*` stage skill, former gate, or migration behavior.

#### Scenario: Invoke the renamed generic workflow
- **WHEN** a user invokes `zpp-legacy-workflow`
- **THEN** it starts or resumes its declared generic sequence and requests kernel assessment only for the selected actions that require lifecycle control

#### Scenario: Encounter an old stage skill
- **WHEN** a machine retains a ZPP 1.x `zpp-flow-*` skill
- **THEN** the current workflow family does not treat it as a workflow stage or migration source

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
A complete user-scope ZPP workflow integration SHALL include the five current complete `zpp-*` playbooks, guard-only `zpps-workflow-kernel`, the seven substantive bounded stage skills, the eleven substantive procedure-complete OpenSpec adapters, `zpps-verify-repository`, and the `zpp-traits` automatic context hook. It SHALL NOT include `zpp-workflow`, `zpps-onboard`, broad `zpps-plan-change`, `zpps-verify`, or `zpps-archive` identities, generated `openspec-*` operation skills, `zpp-workspace-management`, or a ZPP 1.x stage or hook identity.

#### Scenario: Conformance trace for the canonical workflow identity sequence
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Ready installed workflow operation set","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Preserve one deterministic public inventory"}`
- **THEN** executable acceptance authority is `features/consolidated_workflow_skill/consolidated_workflow_skill.feature::Preserve one deterministic public inventory`

## REMOVED Requirements

### Requirement: One distributed ZPP workflow skill
**Reason**: The single packaged skill is replaced by multiple complete user-facing playbooks and substantive bounded component skills guarded by one lifecycle kernel.

**Migration**: Invoke `zpp-auto` or a specific current `zpp-*` playbook; use `zpp-legacy-workflow` for the former generic outcome.
