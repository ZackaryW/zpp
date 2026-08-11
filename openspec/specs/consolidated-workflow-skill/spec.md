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
ZPP SHALL reauthor the applicable standard workflow trait behavior from the separate reference repository into one-family TOML source documents under `artifacts/traits`. The packaged source path SHALL NOT be imposed as the runtime collection path. Related language or framework variants SHALL become ordered, self-contained flavors without content inheritance. Automatic workflow progression and workflow authority behavior SHALL move into the consolidated skill, and every other reference behavior SHALL be represented or explicitly excluded with a product-grounded reason.

#### Scenario: Package the standard collection
- **WHEN** ZPP builds its distributed workflow assets
- **THEN** the collection includes the reauthored BDD structure, BDD operation, TDD, build, dependency, tool, lease, reconciliation, and zero-assumption behavior rather than one generic BDD replacement

### Requirement: Explicit stage actions
The consolidated workflow skill SHALL require an explicit requested stage for each workflow invocation and SHALL NOT infer the stage from OpenSpec status, repository files, stored environment context, or trait output. When automatic continuation is separately authorized, the skill SHALL expose and execute each next stage as a distinct stage action. Automatic hook resolution SHALL remain stage-neutral and SHALL NOT select or advance a workflow stage.

#### Scenario: Reject an unnamed stage
- **WHEN** a workflow invocation does not identify the requested stage
- **THEN** the skill requests that stage rather than inferring one from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes one stage and continues
- **THEN** the skill invokes the next stage explicitly without delegating stage choice to the trait hook

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
