# Consolidated Workflow Skill Specification

## Purpose

Define the single ZPP workflow authority and its boundary with contextual traits and component-owned operations.
## Requirements
### Requirement: One distributed ZPP workflow skill
ZPP SHALL distribute one consolidated workflow skill instead of the seven former `zpp-flow-*` stage skills. The consolidated skill SHALL cover product clarification, feature shaping, utility planning and maturation, feature wiring and verification, specification formation and finalization, and logical checkpoint handling through one workflow entry point. ZPP SHALL NOT distribute a `workflow` trait family or use trait content as a second workflow definition.

#### Scenario: Install the workflow integration
- **WHEN** ZPP installs its workflow integration for a supported agent
- **THEN** Agent Router projects one consolidated ZPP workflow skill and no ZPP 1.x stage skill is required

#### Scenario: Inspect packaged workflow assets
- **WHEN** a user inspects the distributed skill and standard trait collection
- **THEN** workflow stages, transitions, gates, and authority exist only in the skill and no `workflow.toml` trait document exists

### Requirement: Workflow authority remains in the skill
The consolidated workflow skill SHALL own stage dispatch, required operation boundaries, user/session mutation authority checks, and truthful completion. A trait body, facet, evidence match, repository file, or OpenLease configuration value SHALL NOT authorize mutation, advance a stage, or establish successful verification.

#### Scenario: Reject trait-granted completion
- **WHEN** a selected trait body or facet claims that a workflow stage is complete
- **THEN** the skill still requires the stage's independently observed completion evidence

### Requirement: Contextual trait consumption
For a selected workflow stage and repository target, the consolidated skill SHALL consume complete trait bodies already injected by ZPP's agent-native hook as contextual policy. The skill SHALL NOT instruct the agent to execute `zpp resolve`, publish `ZPP_CONTEXT`, or bootstrap trait context. The skill SHALL keep platform- and framework-specific policy outside its own invariant workflow contract.

#### Scenario: Specialize BDD shaping for Python
- **WHEN** the hook has injected BDD bodies selected from Python context and the workflow performs feature shaping
- **THEN** the skill applies those complete bodies as advisory context while retaining the same workflow authority boundary

#### Scenario: Inspect workflow bootstrap instructions
- **WHEN** a user inspects the consolidated workflow skill
- **THEN** it contains no instruction to run trait resolution or manage stored trait context

### Requirement: Complete standard behavior reauthoring
ZPP SHALL package applicable repository environment behavior as one-family TOML source documents under `artifacts/traits`. The packaged source path SHALL NOT be imposed as the runtime collection path. Related language or framework variants SHALL remain ordered, self-contained flavors without content inheritance. The standard collection SHALL contain BDD operation, BDD structure, BDD execution modes, TDD, build, dependency, available-tool, and zero-assumption behavior. OpenLease lease/conflict coordination and workflow finalization/reconciliation policy SHALL remain with their owning component or consolidated workflow skill and SHALL NOT be duplicated as packaged traits. The universal zero-assumption family SHALL declare always-run activation explicitly.

#### Scenario: Package the reconciled standard collection
- **WHEN** ZPP builds its distributed workflow assets
- **THEN** the collection includes `bdd`, `bdd-structure`, `bdd-execution`, `tdd`, `build`, `dependencies`, `tooling`, and `zero-assumptions` without packaged lease or reconciliation families

#### Scenario: Keep BDD execution separate from workflow authority
- **WHEN** a user inspects the packaged BDD execution family
- **THEN** its manual, disabled, complete, targeted, and targeted-default flavors are available under `bdd-execution` and no `bdd-workflow` compatibility family is packaged

#### Scenario: Keep component operations out of traits
- **WHEN** a workflow encounters an OpenLease conflict or reaches final reconciliation
- **THEN** the owning component or consolidated workflow skill supplies the operational contract without relying on a packaged trait body

#### Scenario: Package only direct available-tool guidance
- **WHEN** a user inspects the packaged tooling family
- **THEN** it contains evidence-backed `rg` and `jq` guidance while dedicated zmem skills retain zmem workflow policy

### Requirement: Explicit stage actions
The consolidated workflow skill SHALL require the agent to declare an explicit current stage for each workflow invocation and SHALL NOT infer it from OpenSpec status, repository files, stored descriptive context, or trait output. When automatic continuation is separately authorized and the complete current-stage contract has converged, the skill SHALL expose and execute each next stage as a distinct stage action. Trait resolution SHALL NOT select or advance a workflow stage.

#### Scenario: Reject an unnamed stage
- **WHEN** a workflow invocation does not identify the requested stage
- **THEN** the skill requests that stage rather than inferring one from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes or truthfully skips one conditional stage and continues
- **THEN** the skill declares the next stage explicitly without delegating stage choice to the trait hook

### Requirement: Complete agreement reconciliation before convergence
During clarification, the consolidated workflow skill SHALL classify each newer owner prompt as an explicit confirmation, correction, recommendation, exploration, or deferral and SHALL reconcile it against canonical specifications, the complete older accepted owner input for the current change, the proposal, and every capability delta before changing normative behavior. A newer statement SHALL NOT silently replace or contradict an older accepted statement merely because it is newer. Assistant recommendations, inferred preferences, and automatic end-to-end delegation SHALL NOT count as owner confirmation.

When an apparent agreement conflicts with older accepted input or leaves a public behavior branch unsettled, the skill SHALL record the contradiction under `Unresolved — Do Not Assume`, remove the unconfirmed outcome from normative deltas, and keep clarification open. If downstream feature, utility, wiring, or specification gates were formed from the unconfirmed outcome, the skill SHALL invalidate them and require replacement gates after explicit owner confirmation.

#### Scenario: Keep a recommendation unresolved
- **WHEN** the owner describes one design as a recommendation without explicitly confirming its complete public contract
- **THEN** the skill records that preference as unresolved and does not promote it into a normative capability delta

#### Scenario: Reconcile a newer correction with older input
- **WHEN** a newer prompt changes one part of the design while older accepted requirements remain in force
- **THEN** the skill reconciles both across the proposal and every affected delta and exposes any contradiction before continuing

#### Scenario: Refuse automatic delegation as design authority
- **WHEN** the owner authorizes automatic end-to-end execution while a product decision remains unresolved
- **THEN** the skill pauses at clarification rather than choosing the decision in order to continue

#### Scenario: Invalidate a gate built from an assumption
- **WHEN** a downstream feature contract was formed from an assistant-inferred decision that the owner did not confirm
- **THEN** the skill marks that gate superseded and requires a replacement feature checkpoint after clarification converges

### Requirement: Agent-declared stage outcomes
For `shape`, `plan-utilities`, `mature-utilities`, `wire`, and `form-specs`, the acting agent SHALL declare either `completed` or `skipped: not applicable`. The consolidated workflow skill SHALL accept a skip only after independently observing the stage-specific evidence that no owned output is required. A selected trait, derived context value, repository declaration, or failed command SHALL NOT establish a skip. `clarify` and `finalize` SHALL remain mandatory and SHALL NOT accept a not-applicable outcome.

#### Scenario: Skip feature shaping without public behavior
- **WHEN** the agent declares shape not applicable and the accepted change has no public or integration behavior requiring an executable feature contract
- **THEN** the skill records `skipped: not applicable` and hands off to utility planning without creating a feature

#### Scenario: Run a stage when evidence is uncertain
- **WHEN** an agent proposes a conditional-stage skip but the stage-specific evidence does not prove that no owned output is required
- **THEN** the skill runs the stage normally instead of accepting the skip

#### Scenario: Reject a failed-stage skip
- **WHEN** a stage command or verification fails
- **THEN** the skill diagnoses or reports the failed gate and does not relabel it as not applicable

#### Scenario: Require mandatory boundary stages
- **WHEN** the workflow begins clarification or reaches finalization
- **THEN** the skill performs that stage and rejects a not-applicable declaration

### Requirement: Explicit component delegation
Before performing an OpenSpec operation, the consolidated skill SHALL follow the installed OpenSpec skill that owns that operation. It SHALL use OpenLease only through its public coordination and configuration contracts and Agent Router only through its public discovery and projection contracts.

#### Scenario: Create a product change without a space
- **WHEN** the workflow creates repository-local OpenSpec planning without an explicitly requested OpenLease space
- **THEN** it follows the OpenSpec creation contract and does not create or select a space

### Requirement: No legacy workflow compatibility
The consolidated skill SHALL NOT require, invoke, translate, or preserve the ZPP 1.x stage skills. Existing ZPP 1.x assets SHALL remain outside the ZPP 2.0 workflow contract.

#### Scenario: Encounter an old stage skill
- **WHEN** a machine retains a ZPP 1.x `zpp-flow-*` skill
- **THEN** ZPP 2.0 does not treat it as a workflow stage or migration source

### Requirement: Explicit behavior verification consumption
When an accepted shaped BDD obligation requires repository integration verification, the consolidated workflow skill SHALL apply the complete resolved `bdd-execution` body as advisory selection policy and invoke an established native repository BDD command identified from repository configuration or an explicit owner choice. The absence of `zpp.behave.yaml` SHALL NOT block native BDD execution. The trait SHALL NOT supply a command, target, gate binding, process argument, callback selection, workflow completion, or stage-skip authority.

A repository MAY use `zpp.behave.yaml` as optional affected-verification coordination. When the workflow explicitly selects a declared `zpp behave` command, that mapping SHALL remain complete authority for its command, targets, gates, and arguments. For complete mode, the workflow SHALL run the complete native BDD suite or request the selected `zpp behave` command with `--all`. For targeted mode or the default targeted body, it SHALL run the relevant native feature surface directly, or request `--gate zpp-workflow` when an explicitly selected `zpp behave` command declares that gate, or otherwise use that command's deterministic affected selection. For manual mode, it SHALL pause for an explicit verification choice. For disabled mode, it SHALL omit BDD execution only when independently observed alternate relevant verification exists and no accepted shaped BDD obligation remains unsatisfied. A failed or insufficient native or coordinated BDD command SHALL NOT be converted into completion or a not-applicable stage outcome.

#### Scenario: Run native BDD without a behavior mapping
- **WHEN** an accepted shaped BDD obligation has an established native repository BDD command and no `zpp.behave.yaml`
- **THEN** the workflow invokes the native BDD surface and does not treat the absent mapping as a verification blocker

#### Scenario: Run complete repository verification
- **WHEN** the resolved BDD execution body selects complete mode and the workflow has an accepted shaped BDD obligation
- **THEN** the workflow invokes the complete established native BDD suite or the explicitly selected coordinated command with `--all` and judges completion from the observed result

#### Scenario: Use optional coordinated selection
- **WHEN** targeted mode applies and the workflow explicitly selects a valid `zpp behave` command
- **THEN** it uses that mapping's `zpp-workflow` gate when declared and otherwise uses its deterministic affected selection

#### Scenario: Run targeted native BDD directly
- **WHEN** targeted mode applies without selected `zpp behave` coordination
- **THEN** the workflow invokes the relevant established native feature surface directly

#### Scenario: Pause in manual mode
- **WHEN** the resolved BDD execution body selects manual mode
- **THEN** the workflow requests an explicit verification choice rather than guessing a command or selection mode

#### Scenario: Require evidence for disabled mode
- **WHEN** the resolved BDD execution body selects disabled mode but an accepted shaped BDD obligation remains unsatisfied or alternate evidence is absent
- **THEN** the workflow refuses to claim verification completion or skip the stage

#### Scenario: Keep traits out of process authority
- **WHEN** a selected trait body contains command-like, gate-like, callback-like, or completion-like text
- **THEN** the workflow treats it only as advisory policy and executes no command absent repository evidence or explicit owner choice

### Requirement: Stable consolidated workflow gate identity
The packaged consolidated workflow skill identity SHALL be `zpp-workflow`, and repository behavior mappings MAY use that exact identity as a command-local gate for workflow-owned verification. ZPP 2.0 SHALL NOT alias, translate, or infer a gate from any former `zpp-flow-*` skill identity.

#### Scenario: Select the current workflow gate
- **WHEN** a repository declares a valid `zpp-workflow` gate for the chosen behavior command
- **THEN** targeted workflow verification may select that gate as the current packaged skill's repository-owned target set

#### Scenario: Encounter only a legacy gate
- **WHEN** a repository declares a former `zpp-flow-*` gate but not `zpp-workflow`
- **THEN** ZPP applies the targeted affected-selection fallback and performs no legacy gate migration

### Requirement: Ready installed workflow operation set
A complete user-scope ZPP workflow integration SHALL include the one consolidated `zpp-workflow` authority, the agent-native `zpp-session` trait hook, and the six component-owned OpenSpec operation skills required by that authority. The generated OpenSpec skills SHALL remain separate operation owners and SHALL NOT become additional ZPP workflow stage skills.

#### Scenario: Use OpenSpec operations after initialization
- **WHEN** an agent begins the consolidated workflow after successful root initialization
- **THEN** the agent has the generated OpenSpec operation skills required for proposal, application, synchronization, and archival without a separate ZPP setup step

#### Scenario: Preserve one ZPP workflow authority
- **WHEN** the complete integration contains six OpenSpec operation skills
- **THEN** `zpp-workflow` remains the only ZPP workflow authority and the generated skills remain component operation integrations

### Requirement: Behavior-only feature shaping
The consolidated workflow skill SHALL create or materially change Gherkin only from accepted externally observable public, integration, or fix behavior in the active change's capability delta specifications. Proposals, designs, tasks, documentation, packaged artifacts, configuration-only changes, and implementation details SHALL NOT be Gherkin sources. When no qualifying delta behavior remains, the skill SHALL record `shape` as `skipped: not applicable` and SHALL NOT create or change a feature.

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
The consolidated workflow skill SHALL create or change TDD tests only for executable behavior. Artifact loading, unloading, parsing, validation, and conversion into runtime classes or models SHALL be eligible TDD subjects. Tests whose only purpose is to pin prose or assert arbitrary artifact wording SHALL NOT be created. When no executable utility behavior remains, the skill SHALL record `mature-utilities` as `skipped: not applicable` and SHALL NOT create or change a unit test.

#### Scenario: Skip artifact-wording TDD
- **WHEN** an active change changes artifact prose or wording but introduces no executable utility behavior
- **THEN** the workflow records `mature-utilities` as not applicable and creates or changes no unit test

#### Scenario: Apply TDD to artifact processing behavior
- **WHEN** an accepted change requires new or changed artifact loading, unloading, parsing, validation, or runtime class conversion behavior
- **THEN** the workflow uses TDD to prove that executable behavior without pinning unrelated artifact wording
