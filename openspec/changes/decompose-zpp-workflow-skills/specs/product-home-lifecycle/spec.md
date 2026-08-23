## ADDED Requirements

### Requirement: Ownership-safe obsolete workflow retirement
Every lifecycle migration SHALL inspect one exact finite obsolete workflow inventory containing `zpp-workflow` and the six formerly generated `openspec-*` operation-skill identities. ZPP SHALL NOT expand that inventory by prefix, glob, directory enumeration, inferred version, or a native destination's contents. When Agent Router reports that ZPP owns an obsolete projection in the exact selected scope, reconciliation SHALL first install and verify the complete current family in that same scope and only then remove the owned obsolete projection through Agent Router. An unowned, modified, ambiguous, or ownership-unsafe obsolete identity SHALL be preserved and reported as a conflict. ZPP SHALL NOT adopt, overwrite, translate, or directly delete any obsolete identity.

If current-family installation or verification fails, every owned obsolete projection SHALL remain. If retirement fails after the current family verifies, the operation SHALL report a partial migration containing the exact installed current entries, surviving obsolete entries, and failure; it SHALL NOT claim the selected scope is reconciled.

#### Scenario: Conformance trace for unowned obsolete preservation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Ownership-safe obsolete workflow retirement","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Preserve an unowned obsolete OpenSpec identity during synchronization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Preserve an unowned obsolete OpenSpec identity during synchronization`

### Requirement: Explicit scope-aware lifecycle migration
Root `zpp sync` SHALL run the shared current-plus-obsolete reconciliation in user scope and SHALL treat an owned old-only installation as installed rather than uninitialized. Grouped `zpp workflow update` SHALL run the same reconciliation in exactly its selected scope and, for project scope, exact selected project root. Neither command SHALL inspect, project, verify, or retire the other scope. Package installation or upgrade alone SHALL perform no projection migration; migration begins only through an explicit ZPP lifecycle command.

#### Scenario: Conformance trace for old-only user migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"Explicit scope-aware lifecycle migration","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Migrate an owned old-only user installation`

## MODIFIED Requirements

### Requirement: Shared lifecycle projection inventory
Root initialization, synchronization, reset, and grouped workflow lifecycle SHALL derive one shared deterministic per-agent current inventory containing every current complete `zpp-*` workflow playbook, the guard-only `zpps-workflow-kernel`, every substantive `zpps-*` phase skill, the eleven substantive procedure-complete OpenSpec adapters, `zpps-verify-repository`, `zpp-traits`, and every remaining packaged companion skill. They SHALL derive the separate exact finite obsolete inventory through the same scope-aware reconciliation boundary. The current inventory SHALL contain no `zpp-workflow`, `zpps-onboard`, broad `zpps-plan-change`, `zpps-verify`, or `zpps-archive` identity, generated `openspec-*` operation skill, `zpp-session`, `zpp-workspace-management`, or ZPP 1.x stage identity.

#### Scenario: Share one current projection inventory
- **WHEN** lifecycle operations enumerate current ZPP integration assets
- **THEN** initialization, synchronization, and reset use the same deterministic hard-cut packaged inventory

#### Scenario: Exclude removed workflow assets
- **WHEN** lifecycle operations inspect a machine retaining `zpp-workflow` or generated `openspec-*` skills
- **THEN** those identities are outside the current projection inventory and participate only in ownership-safe obsolete retirement

### Requirement: First-time root initialization boundary
Root `zpp init` SHALL initialize a selected agent carrying no current or obsolete ZPP projection. When a selected agent carries only Agent Router-owned obsolete projections in user scope, initialization SHALL classify it as an old-only installation and run the shared user-scope reconciliation: install and verify the complete current family, then retire the owned obsolete projections. It SHALL NOT layer current assets beside obsolete assets and report ordinary first installation. When any current-family projection is present, initialization SHALL reject that agent and direct the caller to `zpp sync`, including when the current inventory is partial. An unowned obsolete collision SHALL block migration and remain unchanged.

Rejection and migration SHALL apply per selected agent. A truly absent selected agent MAY still initialize in the same invocation. `zpp init` SHALL NOT expose a force-reprojection mode.

#### Scenario: Initialize an agent without any projection
- **WHEN** a selected agent carries no current or obsolete ZPP skill or hook at its user-scope target
- **THEN** root initialization projects its complete current integration

#### Scenario: Conformance trace for old-only initialization migration
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Migrate an owned old-only user installation during initialization"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Migrate an owned old-only user installation during initialization`

#### Scenario: Reject an agent carrying current entries
- **WHEN** a selected agent already carries any current ZPP skill or hook
- **THEN** root initialization rejects that agent, directs the caller to `zpp sync`, and changes none of its projections

#### Scenario: Conformance trace for obsolete initialization conflict
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"product-home-lifecycle","requirement":"First-time root initialization boundary","feature":"features/product_home_lifecycle/product_home_lifecycle.feature","scenario":"Block initialization on an unowned obsolete collision"}`
- **THEN** executable acceptance authority is `features/product_home_lifecycle/product_home_lifecycle.feature::Block initialization on an unowned obsolete collision`
