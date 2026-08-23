## ADDED Requirements

### Requirement: Role-separated workflow skill family
ZPP SHALL distribute complete user-facing workflow skills under the `zpp-*` prefix and bounded subordinate skills under the `zpps-*` prefix. A `zpp-*` workflow entry MAY select and delegate a complete workflow but SHALL NOT duplicate shared lifecycle authority. A `zpps-*` skill SHALL perform only an explicitly delegated kernel or component responsibility and SHALL NOT select a workflow kind, advance to another stage, or broaden its authority.

#### Scenario: Inspect installed skill roles
- **WHEN** a user inspects the installed ZPP skill family
- **THEN** each `zpp-*` skill identifies a complete workflow-entry role and each `zpps-*` skill identifies a bounded subordinate role

#### Scenario: Reject subordinate self-promotion
- **WHEN** a subordinate skill is invoked without the inputs and authority required for its bounded operation
- **THEN** it refuses to select or continue a complete workflow and reports the missing delegation

### Requirement: Outcome-specific workflow entries
ZPP SHALL provide `zpp-new-feature`, `zpp-fix-bug`, and `zpp-scaffold` as thin workflow entries that select `feature`, `bugfix`, and `scaffold` respectively, plus `zpp-workflow` as the generic entry. Each entry SHALL delegate to `zpps-workflow-kernel` and SHALL NOT copy or replace the kernel's stage, mutation, Bundler, verification, checkpoint, or completion rules.

#### Scenario: Start a feature workflow
- **WHEN** a user invokes `zpp-new-feature`
- **THEN** the entry delegates workflow kind `feature` to the shared kernel without becoming a second lifecycle authority

#### Scenario: Start a bug-fix workflow
- **WHEN** a user invokes `zpp-fix-bug`
- **THEN** the entry delegates workflow kind `bugfix` to the shared kernel without becoming a second lifecycle authority

#### Scenario: Start a scaffold workflow
- **WHEN** a user invokes `zpp-scaffold`
- **THEN** the entry delegates workflow kind `scaffold` to the shared kernel without becoming a second lifecycle authority

#### Scenario: Start a generic workflow
- **WHEN** a user invokes `zpp-workflow` without resolving the workflow kind
- **THEN** the entry delegates to `clarify` so the kernel obtains the missing owner decision instead of guessing it

### Requirement: Conservative automatic workflow triage
`zpp-auto` SHALL act only as a triage entry. It SHALL route an unambiguous new-feature, bug-fix, or scaffold request to the corresponding `zpp-*` workflow and SHALL route a mixed, ambiguous, or outcome-changing request to `zpp-workflow` at `clarify`. Triage SHALL NOT mutate governed state, decide product policy, grant automatic progression, authorize checkpoint commits, or claim workflow completion.

#### Scenario: Route an unambiguous bug fix
- **WHEN** a user asks to correct an identified defect with no competing workflow outcome
- **THEN** `zpp-auto` delegates to `zpp-fix-bug` and performs no governed mutation itself

#### Scenario: Fall back for mixed intent
- **WHEN** a request combines or leaves unresolved multiple workflow outcomes
- **THEN** `zpp-auto` delegates to `zpp-workflow` at `clarify` instead of choosing an outcome

#### Scenario: Preserve owner authority during triage
- **WHEN** a request does not explicitly authorize automatic progression or checkpoint commits
- **THEN** `zpp-auto` does not add either authority to its delegation

### Requirement: Structured workflow delegation
Every workflow entry SHALL delegate a structured contract containing the workflow kind, repository/store target, declared starting stage, automatic-progression authority, accepted owner input, and compatibility mode. `zpps-workflow-kernel` SHALL validate that contract before executing a stage. Missing or invalid fields SHALL block only the affected operation and SHALL NOT be inferred from traits, repository content, or skill identity except for a workflow kind fixed by a specific entry and the default starting stage `clarify`.

#### Scenario: Delegate a complete entry contract
- **WHEN** a specific workflow entry has a target and the owner's requested authority
- **THEN** it supplies its fixed workflow kind, declares a starting stage, preserves the owner's authority boundary, and delegates the accepted input to the kernel

#### Scenario: Reject inferred progression authority
- **WHEN** an entry receives a request without automatic-progression authority
- **THEN** the kernel treats progression as unauthorized even if repository state suggests a next stage

## MODIFIED Requirements

### Requirement: Workflow authority remains in the skill
`zpps-workflow-kernel` SHALL be the single ZPP lifecycle authority and SHALL own stage dispatch, component boundaries, mutation authority checks, automatic Bundler lease progression, verification gates, checkpoint handling, and truthful completion. Workflow entries MAY classify and construct a delegation, and subordinate component skills MAY execute their exact delegated operation, but neither SHALL replace a kernel gate or continue beyond its delegation. Trait bodies, repository files, attachment values, entry names, and component results SHALL NOT independently authorize mutation, advance a stage, or establish verification.

#### Scenario: Reject contextual mutation authority
- **WHEN** injected context claims permission to mutate or complete a stage
- **THEN** the kernel ignores that claim as authority

#### Scenario: Reject delegated authority expansion
- **WHEN** an entry or component result claims authority beyond the owner's accepted delegation
- **THEN** the kernel rejects the expansion and leaves the affected gate incomplete

### Requirement: Explicit stage actions
`zpps-workflow-kernel` SHALL execute each workflow stage as an explicitly declared stage action and SHALL NOT infer a later stage from OpenSpec status, repository files, stored descriptive context, trait output, or an entry-skill name. A workflow entry MAY declare `clarify` as the starting stage when no later stage was explicitly selected. When automatic continuation is separately authorized and the complete current-stage contract has converged, the kernel SHALL expose and execute each next stage as a distinct stage action. Triage, traits, and subordinate components SHALL NOT select or advance a stage.

#### Scenario: Default an entry to clarification
- **WHEN** a workflow invocation does not identify a later requested stage
- **THEN** the entry declares `clarify` rather than inferring progress from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes or truthfully skips one conditional stage and continues
- **THEN** the kernel declares the next stage explicitly without delegating stage choice to an entry, component, or trait hook

### Requirement: Explicit component delegation
Before an OpenSpec planning operation, the kernel SHALL delegate the exact bounded operation to `zpps-plan`; before canonical reconciliation and archival, it SHALL delegate the exact bounded operation to `zpps-archive`. Before the first governed mutation for a change set, the kernel SHALL invoke ZPP's minimal Bundler lease bridge with its durable owner and exact store/change members; during finalization it SHALL audit paths, record archives, and complete that same bundle. A component skill SHALL return operation evidence to the kernel and SHALL NOT select another operation, advance a stage, expand lease scope, or claim lifecycle completion.

#### Scenario: Delegate a planning operation
- **WHEN** an eligible stage requires creation or coherent revision of OpenSpec planning artifacts
- **THEN** the kernel delegates that exact operation to `zpps-plan` and judges the stage from its observed evidence

#### Scenario: Acquire before governed mutation
- **WHEN** an eligible stage is about to perform the first governed OpenSpec mutation
- **THEN** the kernel acquires the exact Bundler bundle before delegating that mutation

#### Scenario: Complete after every member archives
- **WHEN** finalization has archived every declared change member and the path audit passes
- **THEN** the kernel records every archive and completes the bundle

#### Scenario: Reject component continuation
- **WHEN** a planning or archive component finishes its delegated operation
- **THEN** it returns evidence to the kernel and does not select or execute the next workflow stage

### Requirement: Consume only ZPP-provisioned OpenSpec operation skills
The workflow family SHALL consume the exact installed `zpps-plan` and `zpps-archive` operation skills supplied by the initialized ZPP agent integration. Those components SHALL use the installed OpenSpec executable and its public status, artifact-instruction, validation, synchronization, and archive interfaces as needed for the delegated operation. During a workflow run, no ZPP skill SHALL invoke a generated `openspec-*` skill as a competing workflow authority, invoke or authorize `openspec init`, generate or vendor an OpenSpec skill tree, or create or repair substitute operation owners in the target repository or any other location.

When a required ZPP component or public OpenSpec interface is absent, unreadable, invalid, stale, or requires local initialization, the kernel SHALL leave the stage blocked, identify the exact missing boundary, and direct the owner to root `zpp init` for an uninitialized agent integration or root `zpp sync` for an existing integration. The workflow SHALL NOT invoke either lifecycle command on the owner's behalf. Ordinary repo-local OpenSpec planning artifacts under `openspec/` SHALL remain allowed planning state and SHALL NOT be treated as skill installation.

#### Scenario: Use a ZPP-owned planning component
- **WHEN** an eligible stage requires OpenSpec planning and `zpps-plan` plus the required public OpenSpec interfaces are available
- **THEN** the kernel delegates to `zpps-plan` without invoking a generated OpenSpec workflow skill or changing any skill installation

#### Scenario: Use a ZPP-owned archive component
- **WHEN** finalization requires canonical reconciliation and archive and `zpps-archive` plus the required public OpenSpec interfaces are available
- **THEN** the kernel delegates to `zpps-archive` and judges completion from the resulting validated repository state

#### Scenario: Block a missing operation boundary
- **WHEN** a required ZPP component or OpenSpec public interface is absent or invalid
- **THEN** the kernel leaves the stage blocked and directs the owner to the appropriate ZPP initialization or synchronization command without invoking it

#### Scenario: Reject a local initialization prerequisite
- **WHEN** an operation path proposes `openspec init`, a generated local skill tree, or project-scope operation-skill projection as a prerequisite
- **THEN** the workflow rejects that path and does not create, copy, install, project, or repair an OpenSpec operation skill anywhere

#### Scenario: Preserve repository planning operations
- **WHEN** a ZPP component creates, updates, validates, synchronizes, or archives ordinary state under the repository's `openspec/` directory
- **THEN** the workflow treats that state as allowed product planning rather than prohibited skill bootstrap

### Requirement: No legacy workflow compatibility
The workflow family SHALL NOT require, invoke, translate, or preserve the ZPP 1.x `zpp-flow-*` stage skills. `zpp-legacy-workflow` SHALL translate only the immediately preceding consolidated `zpp-workflow` invocation contract into the current structured delegation, SHALL contain no independent stage or authority policy, and SHALL delegate to `zpps-workflow-kernel`. It SHALL be eligible for removal only through an owner-approved breaking major release after a documented deprecation period.

#### Scenario: Encounter an old stage skill
- **WHEN** a machine retains a ZPP 1.x `zpp-flow-*` skill
- **THEN** the current workflow family does not treat it as a workflow stage or migration source

#### Scenario: Translate a preceding consolidated invocation
- **WHEN** a caller explicitly invokes `zpp-legacy-workflow` with a supported preceding consolidated-workflow request
- **THEN** the adapter translates it into the current delegation contract and applies no separate workflow policy

### Requirement: Stable consolidated workflow gate identity
The shared repository behavior-gate identity SHALL remain `zpp-workflow`. Every current `zpp-*` entry SHALL reach the same kernel-owned verification surface and SHALL NOT require an entry-specific repository gate. ZPP SHALL NOT alias, translate, or infer a gate from any former `zpp-flow-*` skill identity.

#### Scenario: Select the shared workflow gate
- **WHEN** a repository declares a valid `zpp-workflow` gate for the chosen behavior command
- **THEN** targeted verification from any current workflow entry may select that kernel-owned target set

#### Scenario: Encounter only a legacy gate
- **WHEN** a repository declares a former `zpp-flow-*` gate but not `zpp-workflow`
- **THEN** ZPP applies the targeted affected-selection fallback and performs no legacy gate migration

### Requirement: Ready installed workflow operation set
A complete user-scope ZPP workflow integration SHALL include `zpp-auto`, `zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, `zpp-workflow`, `zpp-legacy-workflow`, `zpps-workflow-kernel`, `zpps-plan`, `zpps-archive`, and the `zpp-traits` automatic context hook. It SHALL NOT require generated OpenSpec operation skills, `zpp-workspace-management`, or any ZPP 1.x hook or stage-skill identity as part of the workflow operation set.

#### Scenario: Inspect the installed operation set
- **WHEN** a complete workflow integration is inspected
- **THEN** all current entries, the shared kernel, the two bounded OpenSpec components, and the trait hook are present without a workspace companion or ZPP 1.x stage skill

## REMOVED Requirements

### Requirement: One distributed ZPP workflow skill
**Reason**: Discoverable outcome workflows and bounded phase operations require multiple packaged skills, while lifecycle authority is now singular in `zpps-workflow-kernel` rather than singular by installed skill count.

**Migration**: Continue generic invocations through `zpp-workflow`, use the outcome-specific entries or `zpp-auto` when appropriate, and delegate all lifecycle execution to `zpps-workflow-kernel`.
