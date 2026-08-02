# extension-trait-packs Specification

## Purpose

Defines how ZPP discovers validated read-only trait sources from the active plugins of the invoking supported agent without copying plugin content into user-owned profile state.

## Requirements

### Requirement: Invocation-scoped active plugin discovery
When resolution names Codex, Claude, or Pi as the invoking agent, ZPP SHALL discover only the plugins reported as active by that agent's authoritative installed-state contract. It SHALL NOT union installations from another agent or treat an available-but-uninstalled, disabled, stale, orphaned, or merely cached plugin as active.

A direct resolution invocation without an agent identity SHALL preserve existing ZPP-only behavior and SHALL NOT discover external plugin sources.

#### Scenario: Discover only the invoking agent's active plugins
- **WHEN** resolution identifies Codex as the invoking agent while different plugins are active in Codex, Claude, and Pi
- **THEN** only Codex's active plugin roots are eligible as external trait sources

#### Scenario: Ignore inactive plugin material
- **WHEN** an agent installation contains marketplace, disabled, orphaned, or stale cached plugin material that its active installed-state contract does not select
- **THEN** none of that material participates in trait discovery

#### Scenario: Resolve directly without an agent
- **WHEN** a user invokes `zpp resolve` without `--agent`
- **THEN** ZPP resolves its ordinary user and repository layers without discovering any editor plugin source

### Requirement: Conventional read-only trait source
An eligible plugin root containing the conventional `trait.json` and `traits/*.md` authored shape SHALL participate as a read-only external trait source. Its valid trigger rules SHALL participate in ordinary activation, while valid trait definitions omitted from its trigger list SHALL remain available for a later user-owned layer to activate. ZPP SHALL NOT copy, rewrite, or create derived state inside the plugin root.

#### Scenario: Resolve declared and manual plugin traits
- **WHEN** an active plugin source declares one valid trigger and contains another valid trait definition omitted from `trait.json`
- **THEN** the declared trigger participates and the omitted definition remains inactive unless a later participating user-owned layer activates it

#### Scenario: Preserve the external source
- **WHEN** ZPP validates, compiles, or resolves an active plugin trait source
- **THEN** the plugin's authored files remain byte-for-byte unchanged and any derived state is stored outside the plugin root

### Requirement: Source-authoritative external freshness
ZPP SHALL keep derived external-source state independently namespaced and SHALL re-evaluate the invoking agent's active plugin identity, resolved root, active version, and trait-source freshness before relying on it. A disabled, updated, moved, or uninstalled plugin SHALL cease contributing its prior source, and stale derived state SHALL NOT remain effective.

#### Scenario: Follow an updated active plugin
- **WHEN** the invoking agent replaces an active plugin version or resolved root
- **THEN** subsequent resolution uses only the newly active source and does not emit traits from the displaced source

#### Scenario: Stop resolving an uninstalled plugin
- **WHEN** the invoking agent no longer reports a plugin as active
- **THEN** subsequent resolution excludes its traits even if its former files or ZPP-derived cache still exist

### Requirement: External source validation failure
A malformed declared external trait source SHALL fail complete resolution with a source-oriented diagnostic and empty trait output. ZPP SHALL NOT silently skip the declared source or emit stale or partial fallback traits.

#### Scenario: Reject a malformed active plugin source
- **WHEN** an active plugin declares the conventional trait-source shape but its authored control document or trait definition is invalid
- **THEN** resolution identifies that external source, fails completely, and emits no trait context

### Requirement: Deterministic external source identity and conflicts
ZPP SHALL order distinct active external sources by stable plugin identity before composing them. Byte-identical trait definitions with the same name MAY deduplicate while their valid trigger rules remain eligible for ordinary trigger composition. Different content for the same trait name from distinct active plugin identities SHALL fail complete resolution with every conflicting source identified rather than selecting an implicit winner.

#### Scenario: Deduplicate identical external definitions
- **WHEN** distinct active plugin sources provide byte-identical definitions for one trait name
- **THEN** the definition participates once and valid trigger rules compose through ordinary activation semantics

#### Scenario: Reject conflicting external definitions
- **WHEN** distinct active plugin sources provide different content for the same trait name
- **THEN** resolution fails completely, identifies the conflicting plugin sources, and emits no trait context
