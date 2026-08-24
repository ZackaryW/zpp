# Product Home Lifecycle Specification

## Purpose

Define ZPP home selection, native folder opening, and the complete integration lifecycle: first-time root initialization, explicit prior-version migration, drift-selected synchronization, scope-aware grouped workflow reconciliation, confirmed state replacement, all-agent reset preflight, reset ownership exclusions, and the shared projection inventory those commands share.
## Requirements
### Requirement: Selected ZPP home layout
ZPP SHALL treat root `--path` as the selected ZPP home and default it to `~/.zpp`. Bundler-backed lease operations SHALL use exactly the selected home's `bundler` child as their `LeaseStateRepository` root. Selecting or resolving a home and performing read-only attachment resolution SHALL NOT create the home or state. ZPP SHALL ignore and never migrate, delete, or inspect a sibling `openlease` child.

#### Scenario: Select the default home without creation
- **WHEN** no explicit path is supplied for a read-only operation
- **THEN** ZPP selects `~/.zpp`, derives its `bundler` child, and creates neither path

#### Scenario: Create state on first lease acquisition
- **WHEN** automatic workflow coordination acquires its first Bundler bundle
- **THEN** ZPP creates state only beneath the selected home's exact `bundler` child

### Requirement: Explicit native home opening
Root `zpp open` SHALL create and open the selected ZPP home through the host platform's native folder-opening facility without a command shell. It SHALL NOT initialize Bundler state, inspect legacy state, install agent assets, or execute repository behavior.

#### Scenario: Open a missing home natively
- **WHEN** a caller selects a missing ZPP home and invokes `zpp open`
- **THEN** ZPP creates and opens exactly that home without creating its `bundler` child

### Requirement: Confirmed complete product reset
Root `zpp reset` SHALL require `--yes`, remove every ownership-safe selected ZPP projection through Agent Router, and replace only the selected home's exact `bundler` child with fresh empty lease state after projection cleanup succeeds. It SHALL target the `zpp-traits` hook and remaining packaged companions, exclude the removed workspace skill, and never inspect or change legacy `openlease` state.

#### Scenario: Reset complete user integration and state
- **WHEN** confirmed reset preflight succeeds and every selected removal succeeds or is absent
- **THEN** ZPP removes the current owned integration and replaces only the `bundler` state child

### Requirement: Complete reset preflight and retry safety
Before reset mutation, ZPP SHALL inspect every selected current projection, validate the exact `bundler` child, and prepare replacement Bundler lease state. Any unmanaged or unsafe projection or state target SHALL abort before mutation. Any removal failure SHALL leave prior Bundler state unchanged, and retry SHALL treat already absent projections as eligible.

#### Scenario: Preserve state after runtime removal failure
- **WHEN** a planned Agent Router removal fails after preflight
- **THEN** ZPP reports the failure and leaves prior Bundler state unchanged

### Requirement: Reset ownership and destructive-path boundary
Reset SHALL preserve the selected ZPP home and every path outside its exact `bundler` child, including legacy `openlease` state, repository documents, project projections, plugins, and worktrees. It SHALL reject broad, symlinked, or incompatible state targets and SHALL NOT follow a symlink.

#### Scenario: Preserve legacy and user-authored content
- **WHEN** the selected home contains an `openlease` child or other user-authored paths outside `bundler`
- **THEN** reset changes none of them

### Requirement: Concise reset reporting
Confirmed reset SHALL print one concise summary by default identifying projection outcomes and the Bundler state result; `--json` SHALL emit the complete deterministic report.

#### Scenario: Report successful reset concisely
- **WHEN** confirmed reset completes without `--json`
- **THEN** ZPP prints one line summarizing integration cleanup and Bundler state replacement

### Requirement: Drift-selected integration synchronization
Root `zpp sync` SHALL inspect the shared current and obsolete lifecycle inventories in user scope for each selected agent that carries at least one current or Agent Router-owned obsolete ZPP projection, and SHALL reproject only current entries whose observed state is not current. A selected agent carrying no current or obsolete ZPP projection SHALL be reported and left unmodified, because first-time projection belongs to root initialization. An owned old-only installation SHALL be reconciled as an installed prior version rather than reported uninitialized.

Synchronization SHALL report every inspected entry's observed state so that an unchanged integration is visibly current rather than silently omitted. When the caller supplies `--force`, synchronization SHALL reproject every ZPP-owned entry regardless of its observed state.

An entry whose target ZPP does not own SHALL be reported and left unmodified under every option, because Agent Router does not replace an artifact it did not install and ZPP reaches projections only through public projection contracts. An entry that ZPP owns but whose content no longer matches its ownership record SHALL be reported and left unmodified by default, and SHALL be repaired only when the caller supplies `--force`, through ownership-safe removal followed by projection. Synchronization SHALL NOT adopt, directly delete, or overwrite a native asset outside those contracts.

#### Scenario: Reproject only drifted entries
- **WHEN** a selected installed agent carries some entries reporting a drifted or absent state and others reporting current
- **THEN** synchronization reprojects exactly the drifted and absent entries and leaves the current entries unmodified

#### Scenario: Report an already current integration
- **WHEN** every inspected entry for a selected installed agent reports current
- **THEN** synchronization reports each entry's observed state, performs no projection, and does not claim a change

#### Scenario: Reproject every owned entry under force
- **WHEN** a caller supplies `--force` and inspected entries report current
- **THEN** synchronization reprojects every ZPP-owned entry regardless of its observed state

#### Scenario: Report a locally modified owned entry by default
- **WHEN** synchronization encounters an entry ZPP owns whose content no longer matches its ownership record and the caller supplied no `--force`
- **THEN** synchronization reports that entry as modified, leaves its content unchanged, and identifies the option that would repair it

#### Scenario: Repair a locally modified owned entry under force
- **WHEN** a caller supplies `--force` and an owned entry's content no longer matches its ownership record
- **THEN** synchronization removes it ownership-safely, projects the packaged asset, and restores the packaged content

#### Scenario: Preserve an unowned entry under force
- **WHEN** synchronization encounters a target ZPP does not own, including under `--force`
- **THEN** synchronization reports that entry, leaves it unmodified, and does not delete or overwrite it outside Agent Router's projection contracts

#### Scenario: Skip an agent without any projection
- **WHEN** a selected agent carries no ZPP skill or hook at its target surface
- **THEN** synchronization reports that agent as uninitialized, projects nothing for it, and directs the caller to root initialization

### Requirement: First-time root initialization boundary
Root `zpp init` SHALL initialize a selected agent carrying no current or obsolete ZPP projection. For each selected agent, ZPP SHALL inspect both shared lifecycle inventories before mutation. When the agent carries only Agent Router-owned obsolete projections in user scope, initialization SHALL reconcile that old-only installation by installing and verifying the complete current family before retiring owned obsolete projections. It SHALL NOT layer the new family beside the obsolete one and report ordinary first installation. When any current-family projection is present, initialization SHALL reject the agent, identify it, and direct the caller to `zpp sync`, including when the current inventory is partial. An unowned obsolete collision SHALL block migration and remain unchanged.

Rejection and migration SHALL apply per selected agent. Selected agents carrying no projection SHALL still be initialized in the same invocation, and a rejected agent SHALL NOT prevent them. `zpp init` SHALL NOT expose a `--force` option or any other reprojection mode, because reprojection of a current installed agent belongs to `zpp sync`.

#### Scenario: Initialize an agent without any projection
- **WHEN** a selected agent carries no ZPP skill or hook at its target surface
- **THEN** root initialization projects its complete integration

#### Scenario: Reject an installed agent
- **WHEN** a selected agent already carries a ZPP skill or hook
- **THEN** root initialization rejects that agent, identifies it, directs the caller to `zpp sync`, and changes none of its projections

#### Scenario: Treat a partially projected agent as installed
- **WHEN** a selected agent carries some but not all of its inventory entries
- **THEN** root initialization treats that agent as installed and rejects it rather than completing the missing entries

#### Scenario: Conformance trace for old-only initialization migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation during initialization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Migrate an owned old-only user installation during initialization`

#### Scenario: Conformance trace for obsolete initialization conflict
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Block initialization on an unowned obsolete collision"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Block initialization on an unowned obsolete collision`

#### Scenario: Initialize absent agents alongside a rejected one
- **WHEN** one selected agent is installed and another carries no projection
- **THEN** root initialization initializes the agent carrying no projection, rejects the installed agent, and reports both outcomes

#### Scenario: Omit the obsolete initialization force mode
- **WHEN** a caller inspects root initialization help or supplies the former force option
- **THEN** ZPP exposes no initialization force mode and rejects the unsupported option

### Requirement: Ownership-safe obsolete workflow retirement
Every lifecycle migration SHALL inspect one exact finite obsolete workflow inventory containing `zpp-workflow` and the six formerly generated `openspec-*` operation-skill identities. ZPP SHALL NOT expand that inventory by prefix, glob, directory enumeration, inferred version, or native destination contents. Reconciliation SHALL install and verify the complete current family in the exact selected scope before removing an Agent Router-owned obsolete projection in that same scope. Unowned, modified, ambiguous, or ownership-unsafe obsolete identities SHALL be preserved and reported as conflicts; ZPP SHALL NOT adopt, overwrite, translate, or directly delete them.

If current-family installation or verification fails, every owned obsolete projection SHALL remain. A retirement failure after current-family verification SHALL report a partial migration with the exact current and surviving obsolete identities and SHALL NOT claim reconciliation.

#### Scenario: Conformance trace for owned obsolete retirement
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Ownership-safe obsolete workflow retirement","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Retire an owned obsolete workflow projection during synchronization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Retire an owned obsolete workflow projection during synchronization`

#### Scenario: Conformance trace for unowned obsolete preservation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Ownership-safe obsolete workflow retirement","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Preserve an unowned obsolete OpenSpec identity during synchronization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Preserve an unowned obsolete OpenSpec identity during synchronization`

### Requirement: Explicit scope-aware lifecycle migration
Root `zpp sync` SHALL run shared current-plus-obsolete reconciliation in user scope and SHALL treat an owned old-only installation as installed. Grouped `zpp workflow update` SHALL run that reconciliation in exactly its selected scope and, for project scope, exact project root. Neither command SHALL inspect, project, verify, or retire another scope. Package installation or upgrade alone SHALL perform no projection migration; migration begins only through an explicit ZPP lifecycle command.

#### Scenario: Conformance trace for old-only user migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Explicit scope-aware lifecycle migration","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Migrate an owned old-only user installation`

### Requirement: Shared lifecycle projection inventory
Root initialization, synchronization, reset, and grouped workflow lifecycle SHALL derive one shared deterministic per-agent current inventory containing every current complete `zpp-*` workflow playbook, the guard-only `zpps-workflow-kernel`, every substantive `zpps-*` phase skill, the eleven substantive procedure-complete OpenSpec adapters, `zpps-verify-repository`, `zpp-traits`, and every remaining packaged companion skill. They SHALL derive the separate exact finite obsolete inventory through the same scope-aware reconciliation boundary. The current inventory SHALL contain no `zpp-workflow`, `zpps-onboard`, broad `zpps-plan-change`, `zpps-verify`, or `zpps-archive` identity, generated `openspec-*` operation skill, `zpp-session`, `zpp-workspace-management`, or ZPP 1.x stage identity.

#### Scenario: Share one current projection inventory
- **WHEN** lifecycle operations enumerate current ZPP integration assets
- **THEN** initialization, synchronization, and reset use the same deterministic hard-cut packaged inventory

#### Scenario: Exclude removed workflow assets
- **WHEN** lifecycle operations inspect a machine retaining `zpp-workflow` or generated `openspec-*` skills
- **THEN** those identities are outside the current projection inventory and participate only in ownership-safe obsolete retirement

### Requirement: Concise synchronization reporting
Root `zpp sync` SHALL select agents through the established interactive prompt when no agent is supplied and an interactive terminal is available, and SHALL reject an omitted selection when no interactive terminal is available. It SHALL print exactly one concise human summary line by default, aggregating reprojected, already current, repaired, modified, preserved, and uninitialized outcomes without printing inspection or projection arrays. When the caller supplies `--json`, synchronization SHALL instead emit its complete deterministic inspection and projection report as valid JSON. Synchronization SHALL NOT emit machine-readable output by default.

#### Scenario: Summarize synchronization
- **WHEN** synchronization completes without `--json`
- **THEN** ZPP prints exactly one concise human summary line aggregating its outcomes

#### Scenario: Emit machine-readable synchronization on request
- **WHEN** a caller supplies `--json`
- **THEN** ZPP emits the complete deterministic inspection and projection report as valid JSON instead of the summary line

### Requirement: Exact legacy hook lifecycle reconciliation
The shared initialization and synchronization boundary SHALL include a bounded
migration check for the former `zpp-session` hook ownership identity without adding
that identity to the current packaged inventory. An intact owned predecessor SHALL
make the current hook eligible for ownership-safe migration in the exact selected
scope. A former hook that is unowned or not intact SHALL remain a reported conflict
and SHALL block retirement claims without blocking inspection of unrelated entries.

Package installation or upgrade alone SHALL perform no hook migration. Grouped
workflow update and root synchronization SHALL migrate only in their explicitly
selected scope, and root initialization SHALL apply the same migration when
reconciling an owned prior-version installation.

#### Scenario: Conformance trace for former user hook migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Exact legacy hook lifecycle reconciliation","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Repair former Codex hook ownership during synchronization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Repair former Codex hook ownership during synchronization`
