## ADDED Requirements

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
