## ADDED Requirements

### Requirement: Canonical packaged ZPP workflow skill set
ZPP SHALL package and validate the complete current workflow skill family defined by the consolidated-workflow capability as Agent Router skills, including the complete `zpp-*` playbooks, guard-only kernel, substantive phase skills, eleven substantive procedure-complete OpenSpec adapters, and the separately classified `zpps-verify-repository` evidence component. It SHALL record onboarding as explicitly excluded and SHALL package no `zpps-onboard`, broad planning/verification/archive compatibility adapter, or generated upstream `openspec-*` skill. It SHALL NOT execute OpenSpec repository initialization, create a disposable repository, or generate, patch, provenance-stamp, or project any upstream `openspec-*` skill.

#### Scenario: Conformance trace for packaged workflow preparation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Canonical packaged ZPP workflow skill set","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Prepare the exact packaged workflow inventory"}`
- **THEN** executable acceptance authority is `features/openspec_skill_provisioning/openspec_skill_provisioning.feature::Prepare the exact packaged workflow inventory`

#### Scenario: Reject an invalid packaged member
- **WHEN** one required packaged workflow skill is missing or invalid
- **THEN** ZPP rejects the incomplete workflow family and projects no partial replacement set

### Requirement: Lifecycle independence and runtime OpenSpec compatibility
Root initialization, synchronization, and reset SHALL NOT detect an OpenSpec version, execute an OpenSpec process, initialize an OpenSpec repository, generate or load OpenSpec skills, write OpenSpec provenance, or condition packaged projection on executable availability. Each ZPP-owned OpenSpec adapter SHALL validate executable availability and only the public interfaces required by its bounded operation when that operation is invoked. A missing, failed, or unsupported runtime interface SHALL block that operation before governed mutation and SHALL NOT alter the packaged integration.

#### Scenario: Conformance trace for lifecycle independence from OpenSpec
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Lifecycle independence and runtime OpenSpec compatibility","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Reconcile lifecycle without invoking OpenSpec"}`
- **THEN** executable acceptance authority is `features/openspec_skill_provisioning/openspec_skill_provisioning.feature::Reconcile lifecycle without invoking OpenSpec`

#### Scenario: Block an unavailable runtime interface
- **WHEN** a resolved adapter cannot invoke the public OpenSpec interface required by its bounded operation
- **THEN** it reports the exact runtime incompatibility and performs no governed operation or packaged-integration mutation

### Requirement: Initialization and synchronization own packaged projection
Root `zpp init` SHALL initially project the complete packaged workflow family for an uninitialized selected agent, and root `zpp sync` SHALL reconcile that same family for an existing integration. Projection order SHALL place current complete `zpp-*` playbooks first, `zpps-workflow-kernel` next, substantive bounded `zpps-*` phase and operation skills in deterministic order, the `zpp-traits` hook, and remaining packaged companion skills in deterministic order. Neither operation SHALL execute OpenSpec or contain an OpenSpec-generated projection pass.

#### Scenario: Conformance trace for initial packaged projection
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Initialization and synchronization own packaged projection","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Initialize the current user integration"}`
- **THEN** executable acceptance authority is `features/openspec_skill_provisioning/openspec_skill_provisioning.feature::Initialize the current user integration`

#### Scenario: Conformance trace for current packaged projection
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"Initialization and synchronization own packaged projection","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Report a complete packaged integration as current"}`
- **THEN** executable acceptance authority is `features/openspec_skill_provisioning/openspec_skill_provisioning.feature::Report a complete packaged integration as current`

#### Scenario: Synchronize one changed packaged phase
- **WHEN** a packaged phase skill changes in an existing owned integration
- **THEN** root synchronization reconciles that skill through the shared lifecycle inventory

### Requirement: ZPP-only tool distribution boundary
The built ZPP distribution SHALL declare OpenSpec Bundler as a library dependency and SHALL expose `zpp` as its tool command. OpenSpec Bundler SHALL remain without a console-script entry point and SHALL NOT require or support a separate `uv tool install` step in the ZPP setup procedure. Installing the built ZPP wheel as a `uv` tool SHALL create one ZPP tool environment, make `zpp` executable, and install OpenSpec Bundler only inside that environment as a dependency rather than as another installed tool.

ZPP SHALL expose one release version consistently through project distribution metadata, `zpp.__version__`, `zpp --version`, and the built wheel metadata. A mismatch SHALL fail release and distribution verification.

#### Scenario: Conformance trace for the built tool boundary
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-skill-provisioning","requirement":"ZPP-only tool distribution boundary","feature":"features/openspec_skill_provisioning/openspec_skill_provisioning.feature","scenario":"Install the built ZPP distribution as the only tool"}`
- **THEN** executable acceptance authority is `features/openspec_skill_provisioning/openspec_skill_provisioning.feature::Install the built ZPP distribution as the only tool`

## MODIFIED Requirements

### Requirement: Agent Router projection authority
ZPP SHALL use Agent Router's public skill and hook lifecycle for every packaged workflow, phase, operation, hook, and companion integration asset. ZPP SHALL preserve selected-agent order and deterministic within-agent asset order in result reporting and SHALL expose component rejections without adopting, overwriting, or directly deleting native destinations.

#### Scenario: Preserve a packaged skill conflict during initialization
- **WHEN** Agent Router rejects one packaged workflow member as conflicting or unmanaged
- **THEN** ZPP reports that lifecycle result and performs no direct native mutation, generated fallback, or compatibility alias

## REMOVED Requirements

### Requirement: Canonical generated OpenSpec skill set
**Reason**: ZPP now owns bounded OpenSpec-facing phase and operation skills and no longer accepts generated upstream skills as workflow components.

**Migration**: Initialize or synchronize the packaged ZPP workflow family and use its `zpps-*` operation boundaries.

### Requirement: Generated skill provenance
**Reason**: No OpenSpec skill is generated or patched, so detected OpenSpec versions no longer form skill source provenance.

**Migration**: Use packaged ZPP asset provenance and treat the detected executable version only as compatibility evidence.

### Requirement: Initialization-only OpenSpec provisioning
**Reason**: Initialization and synchronization now project packaged ZPP workflow skills rather than generating six OpenSpec skills.

**Migration**: Use root `zpp init` for first projection and root `zpp sync` for reconciliation of the shared packaged inventory; executable compatibility is checked only by the invoked runtime adapter.
