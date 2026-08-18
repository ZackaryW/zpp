# Product Home Lifecycle Specification

## Purpose

Define ZPP home selection, native folder opening, and the complete integration lifecycle: first-time root initialization, drift-selected synchronization, confirmed state replacement, all-agent reset preflight, reset ownership exclusions, and the shared projection inventory those commands share.
## Requirements
### Requirement: Selected ZPP home layout
ZPP SHALL treat root `--path` as the selected ZPP home and SHALL default it to `~/.zpp`. Every OpenLease-backed ZPP operation SHALL use the exact `openlease` child of that selected home as its state root, and that state root SHALL hold registered repository topology, authorities, relationships, sessions, and leases in addition to bound configuration. Selecting or resolving a home SHALL NOT by itself create the home or state; establishing a session SHALL create the home and state when they are absent.

#### Scenario: Use the default ZPP home
- **WHEN** a caller omits root `--path`
- **THEN** ZPP selects `~/.zpp` as its home and supplies `~/.zpp/openlease` to OpenLease-backed operations

#### Scenario: Use an alternate ZPP home
- **WHEN** a caller supplies root `--path` with an eligible custom directory
- **THEN** ZPP treats that exact directory as the ZPP home and supplies only its `openlease` child as managed state

#### Scenario: Avoid eager home mutation
- **WHEN** a caller only requests help, version, or another operation that does not require filesystem state
- **THEN** selecting the ZPP home creates no directory or OpenLease state

#### Scenario: BDD target — Create home state when establishing a session
- **WHEN** executable behavior is covered by `features/product_home_lifecycle/product_home_lifecycle.feature::Create home state when establishing a session`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

### Requirement: Explicit native home opening
Root `zpp open` SHALL create the selected ZPP home when absent and open that exact directory through the host platform's native folder-opening facility without a command shell. It SHALL report the resolved home path. It SHALL NOT open only the OpenLease child, inspect or rewrite home contents, initialize OpenLease state, install agent assets, or execute repository behavior.

#### Scenario: Open an existing default home
- **WHEN** a caller invokes `zpp open` with an existing eligible default home
- **THEN** ZPP launches the native folder opener for `~/.zpp` and reports that path without changing its contents

#### Scenario: Create and open an alternate home
- **WHEN** a caller supplies an eligible absent `--path` and invokes `zpp open`
- **THEN** ZPP creates exactly that home directory, opens it natively, and does not create its `openlease` child

#### Scenario: Report an unavailable native opener
- **WHEN** the selected home is valid but the platform folder opener cannot launch
- **THEN** ZPP reports the launch failure without deleting the explicitly created home or falling back to a shell command

### Requirement: Confirmed complete product reset
Root `zpp reset` SHALL require `--yes` before inspecting or mutating external state. A confirmed reset SHALL target every supported agent's ZPP-owned `zpp-workflow` skill, every discovered packaged companion skill, `zpp-session` hook, and six canonical ZPP-provisioned OpenSpec operation skills in user scope, prepare fresh OpenLease state, remove every selected asset through Agent Router, and replace only the selected home's `openlease` child after projection cleanup succeeds. Reset SHALL apply ordinary complete preflight and ownership-safe removal to the packaged ZPP skills and native hook. It SHALL force-delete only the canonical OpenSpec skills by stable name under Agent Router's explicit forced-owned deletion contract, retain no backup or history for them, and SHALL NOT invoke OpenSpec generation. It SHALL NOT expose or accept the former `--overwrite-global-traits` option.

#### Scenario: Reject unconfirmed reset
- **WHEN** a caller invokes `zpp reset` without `--yes`
- **THEN** ZPP rejects the command before inspecting agent projections, preparing state, or changing the filesystem

#### Scenario: Reset complete user integration and state
- **WHEN** a caller confirms reset, existing preflight passes, and every selected removal succeeds or is already absent
- **THEN** ZPP removes all present ZPP-owned user workflow, companion, OpenSpec operation skills, and hooks through Agent Router and replaces the exact OpenLease state child with fresh state

#### Scenario: Target every discovered companion skill
- **WHEN** a caller confirms reset and the packaged companion inventory contains skills beyond the packaged authoring pair
- **THEN** reset targets every discovered companion skill for each supported agent without requiring a declared list of skill names

#### Scenario: Force-delete modified generated skills
- **WHEN** a confirmed reset encounters a modified canonical OpenSpec skill with valid matching Agent Router ownership
- **THEN** Agent Router deletes that exact skill and its ownership state without backup or OpenSpec regeneration

#### Scenario: Omit obsolete global-trait replacement
- **WHEN** a caller inspects reset help or supplies the former overwrite option
- **THEN** ZPP exposes no global-trait overwrite mode and rejects the unsupported option

### Requirement: Complete reset preflight and retry safety
Before any reset mutation, ZPP SHALL inspect every supported agent's user-scope `zpp-session` hook, `zpp-workflow` skill, and every discovered packaged companion skill through Agent Router, validate the selected home and exact state child, and prepare replacement OpenLease state. An absent preflighted projection SHALL be eligible and require no standard removal. Any modified, unmanaged, ambiguous, conflicting, unknown, or failed preflight inspection SHALL abort the complete reset without removing any projection or replacing state.

After successful preflight, ZPP SHALL attempt the standard preflighted removals and forced canonical OpenSpec skill removals in deterministic supported-agent and within-agent asset order and SHALL aggregate runtime failures. Within each agent, standard removal SHALL follow hook, workflow skill, then every packaged companion skill in the deterministic packaged order, before forced OpenSpec removals. Forced OpenSpec removal SHALL treat a wholly absent skill and ownership record as an eligible no-op, remove modified content only with valid matching Agent Router ownership, and reject a present unmanaged target or invalid ownership. Any removal failure SHALL leave the prior OpenLease state unchanged. Earlier successful removals MAY remain removed; a retry SHALL treat already absent assets as eligible and SHALL converge without adopting or directly deleting native assets.

#### Scenario: Abort on one projection conflict
- **WHEN** any selected user-scope workflow skill, packaged companion skill, or hook is not absent or ownership-safe removable during preflight
- **THEN** reset identifies the agent and asset and changes no selected projection or OpenLease state

#### Scenario: Preserve state after runtime removal failure
- **WHEN** standard preflight succeeds but one standard or forced Agent Router removal fails
- **THEN** reset attempts the remaining planned removals, reports all outcomes, leaves prior OpenLease state unchanged, and does not claim completion

#### Scenario: Reject an unmanaged same-named OpenSpec skill
- **WHEN** forced reset cleanup encounters a present canonical OpenSpec skill without valid matching Agent Router ownership
- **THEN** Agent Router preserves that skill, reset reports the conflict, and OpenLease state is not replaced

#### Scenario: Retry after partial cleanup
- **WHEN** reset is retried after an earlier runtime failure removed some selected projections
- **THEN** absent assets are eligible, remaining owned assets are removed through Agent Router, and state replacement occurs only after cleanup succeeds

### Requirement: Reset ownership and destructive-path boundary
Reset SHALL preserve the selected ZPP home itself and every path outside its exact `openlease` child. Repository `.zpp` documents, repository `zpp.behave.yaml`, project-scope projections, plugins, external worktrees, and unrelated user agent assets SHALL remain outside reset authority. Reset SHALL reject a selected home or state child that is broad, symlinked, non-directory where a directory is required, or otherwise cannot be proven safe, and SHALL NOT follow a symlink during preparation or replacement.

#### Scenario: Preserve repository and project assets
- **WHEN** confirmed reset runs while repositories contain traits, behavior mappings, project projections, plugins, or external worktrees
- **THEN** reset changes none of those assets and operates only on the selected user projections and OpenLease state child

#### Scenario: Preserve other ZPP-home contents
- **WHEN** the selected ZPP home contains user-authored files outside `openlease`
- **THEN** reset preserves those files byte-for-byte and never recursively deletes the complete home

#### Scenario: Reject an unsafe reset boundary
- **WHEN** the selected home or `openlease` child is a broad destructive target, unsafe symlink, or incompatible filesystem object
- **THEN** reset fails before projection or state mutation and does not follow or delete the unsafe path

### Requirement: Concise reset reporting
Confirmed root `zpp reset --yes` SHALL print exactly one concise human summary line by default after successful cleanup and state replacement. The summary SHALL aggregate removed and already-absent integration outcomes and identify the OpenLease state result without printing inspection or removal arrays. When the caller supplies `--json`, reset SHALL instead emit its complete deterministic inspection, removal, and state report as valid JSON.

#### Scenario: Summarize confirmed reset
- **WHEN** confirmed reset succeeds without `--json`
- **THEN** ZPP prints one line summarizing removed and already-absent integrations and the replaced OpenLease state

#### Scenario: Request reset JSON
- **WHEN** confirmed reset succeeds with `--json`
- **THEN** ZPP emits the complete deterministic reset report as valid JSON instead of the human summary

### Requirement: Drift-selected integration synchronization
Root `zpp sync` SHALL inspect the shared lifecycle projection inventory in user scope for each selected agent that already carries at least one ZPP projection, and SHALL reproject only the entries whose observed state is not current. A selected agent carrying no ZPP projection SHALL be reported and left unmodified, because first-time projection belongs to root initialization.

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
Root `zpp init` SHALL initialize only a selected agent that carries no ZPP projection at its target surface. For each selected agent, ZPP SHALL inspect the shared lifecycle projection inventory before any mutation for that agent and SHALL reject the agent when any ZPP skill or hook is present, identifying the agent and directing the caller to `zpp sync`. An agent carrying any ZPP projection SHALL count as installed, including one whose inventory is only partially present.

Rejection SHALL apply per selected agent. Selected agents carrying no projection SHALL still be initialized in the same invocation, and a rejected agent SHALL NOT prevent them. `zpp init` SHALL NOT expose a `--force` option or any other reprojection mode, because reprojection of an installed agent belongs to `zpp sync`.

#### Scenario: Initialize an agent without any projection
- **WHEN** a selected agent carries no ZPP skill or hook at its target surface
- **THEN** root initialization projects its complete integration

#### Scenario: Reject an installed agent
- **WHEN** a selected agent already carries a ZPP skill or hook
- **THEN** root initialization rejects that agent, identifies it, directs the caller to `zpp sync`, and changes none of its projections

#### Scenario: Treat a partially projected agent as installed
- **WHEN** a selected agent carries some but not all of its inventory entries
- **THEN** root initialization treats that agent as installed and rejects it rather than completing the missing entries

#### Scenario: Initialize absent agents alongside a rejected one
- **WHEN** one selected agent is installed and another carries no projection
- **THEN** root initialization initializes the agent carrying no projection, rejects the installed agent, and reports both outcomes

#### Scenario: Omit the obsolete initialization force mode
- **WHEN** a caller inspects root initialization help or supplies the former force option
- **THEN** ZPP exposes no initialization force mode and rejects the unsupported option

### Requirement: Shared lifecycle projection inventory
Root initialization, synchronization, and reset SHALL derive their per-agent asset set from one shared projection inventory covering the `zpp-session` hook, the `zpp-workflow` skill, every discovered packaged companion skill, and the canonical ZPP-provisioned OpenSpec operation skills. The inventory SHALL expose inspection, projection, and removal for each entry in deterministic supported-agent and within-agent order. A lifecycle command SHALL NOT enumerate an asset set that diverges from the shared inventory.

#### Scenario: Describe one integration across lifecycle commands
- **WHEN** the packaged companion inventory changes
- **THEN** root initialization, synchronization, and reset all target the changed asset set without a separately maintained list

#### Scenario: Preserve deterministic lifecycle ordering
- **WHEN** any lifecycle command enumerates its per-agent entries
- **THEN** it follows the shared deterministic supported-agent and within-agent order

### Requirement: Concise synchronization reporting
Root `zpp sync` SHALL select agents through the established interactive prompt when no agent is supplied and an interactive terminal is available, and SHALL reject an omitted selection when no interactive terminal is available. It SHALL print exactly one concise human summary line by default, aggregating reprojected, already current, repaired, modified, preserved, and uninitialized outcomes without printing inspection or projection arrays. When the caller supplies `--json`, synchronization SHALL instead emit its complete deterministic inspection and projection report as valid JSON. Synchronization SHALL NOT emit machine-readable output by default.

#### Scenario: Summarize synchronization
- **WHEN** synchronization completes without `--json`
- **THEN** ZPP prints exactly one concise human summary line aggregating its outcomes

#### Scenario: Emit machine-readable synchronization on request
- **WHEN** a caller supplies `--json`
- **THEN** ZPP emits the complete deterministic inspection and projection report as valid JSON instead of the summary line
