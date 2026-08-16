## MODIFIED Requirements

### Requirement: Packaged manual authoring skill set
ZPP SHALL package its portable Agent Router skills under declared roles and SHALL derive the packaged inventory from those roles rather than from a fixed list of skill names. The `workflow` role SHALL resolve to exactly one skill. The `companion` role SHALL resolve to every skill it contains, in one deterministic order that does not depend on filesystem enumeration order. A packaged skill SHALL be recognised only when its directory carries a valid skill document; any other directory entry SHALL be ignored.

ZPP SHALL package `zpp-configure-behave` and `zpp-author-trait` in the companion role, and MAY package further companion skills. Every companion skill SHALL be a manually invoked operation guide for an explicit request and SHALL NOT run from an agent hook, trait activation, workflow stage transition, initialization side effect beyond projection, or repository detection alone. Companion skills SHALL introduce no new ZPP command.

A role that resolves to no skill, a `workflow` role that does not resolve to exactly one skill, and an invalid packaged skill document SHALL each fail packaged loading with a visible error rather than yielding a partial inventory.

#### Scenario: Inspect the discovered companion inventory
- **WHEN** a caller loads ZPP's packaged companion skills
- **THEN** it receives every skill in the companion role as valid detached Agent Router skills in the deterministic packaged order
- **AND** that inventory includes `zpp-configure-behave` and `zpp-author-trait`

#### Scenario: Add a packaged companion skill without redeclaring the inventory
- **WHEN** a new valid skill directory is packaged into the companion role
- **THEN** it appears in the loaded companion inventory without any change to a declared list of skill names

#### Scenario: Ignore a companion entry that is not a skill
- **WHEN** the companion role contains a file or a directory carrying no skill document
- **THEN** packaged loading omits that entry and still returns the valid companion skills

#### Scenario: Reject an unusable packaged role
- **WHEN** the workflow role does not resolve to exactly one skill, a role resolves to no skill, or a packaged skill document is invalid
- **THEN** packaged loading fails with a visible error and returns no partial inventory

#### Scenario: Leave companion skills dormant
- **WHEN** an installed agent starts a session or runs the consolidated workflow without an explicit request that a companion skill covers
- **THEN** no companion skill edits a repository, invokes verification, resolves a trait, or advances workflow state

## ADDED Requirements

### Requirement: Vendored repository memory skills
ZPP SHALL package the `zmem-author-commits` and `zmem-query-memory` skills as companion skills so that installing ZPP makes durable repository-memory authoring and querying guidance available to every supported agent. These skills SHALL be vendored copies of their upstream sources and SHALL be subject to the same discovery, projection, preflight, and removal behavior as every other companion skill. ZPP SHALL NOT package `zmem-design-extensions`.

Vendored companion skill content SHALL remain a faithful copy of its upstream source. ZPP SHALL provide an automated synchronisation that replaces each vendored skill directory from its upstream source so that a vendored copy does not silently diverge.

#### Scenario: Install repository memory guidance with ZPP
- **WHEN** a caller completes ZPP initialization for a supported agent
- **THEN** `zmem-author-commits` and `zmem-query-memory` are projected for that agent alongside the packaged authoring skills

#### Scenario: Exclude the extension design skill
- **WHEN** a caller inspects the packaged companion inventory
- **THEN** it contains no `zmem-design-extensions` skill

#### Scenario: Refresh a drifted vendored skill
- **WHEN** the upstream source of a vendored companion skill changes and synchronisation runs
- **THEN** the vendored directory is replaced with the upstream content and the difference is visible for review
