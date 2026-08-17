## MODIFIED Requirements

### Requirement: Initialization-only OpenSpec provisioning
Root `zpp init` SHALL be the only ZPP command that generates and projects
OpenSpec operation skills for a selected agent carrying no ZPP projection. Root
`zpp sync` SHALL be the only ZPP command that freshly regenerates those operation
skills and safely reconciles them for a selected agent carrying an existing ZPP
projection. Both commands SHALL generate only inside disposable temporary
repositories, validate the exact generated inventory, and project only through
Agent Router into the selected agent's user scope. A workflow run, grouped
workflow lifecycle command, or any other ZPP operation SHALL NOT invoke OpenSpec
skill initialization, generate or project an operation skill, or create a
project-scope operation-skill installation.

Every root `zpp init` invocation with selected uninitialized agents SHALL freshly
detect OpenSpec and regenerate the exact operation inventory for every such agent
before projecting any selected workflow skill, native hook, packaged companion
skill, or generated skill. ZPP SHALL also load the complete discovered packaged
companion source set before projection. After complete preparation succeeds,
Agent Router SHALL install the consolidated skill, native hook, every discovered
packaged companion skill, and six generated OpenSpec skills in each selected
agent's user scope.

Within each selected agent, result and projection order SHALL be `zpp-workflow`,
`zpp-session`, every packaged companion skill in the deterministic packaged
order, then the canonical OpenSpec operation skill order. Grouped
`zpp workflow install|update|remove` SHALL continue to manage only
`zpp-workflow` and `zpp-session` in their selected scope. ZPP SHALL expose no
companion-skill or OpenSpec lifecycle option on that command group.

#### Scenario: Initialize a ready workflow integration
- **WHEN** root initialization succeeds for one or more selected uninitialized agents
- **THEN** Agent Router installs the consolidated skill, native hook, every discovered packaged companion skill, and all six freshly generated OpenSpec skills in each selected agent's user scope

#### Scenario: Report one lifecycle result per projected asset
- **WHEN** root initialization completes for one selected agent
- **THEN** the ordered lifecycle report contains exactly one result for the workflow skill, one for the native hook, one for each discovered companion skill, and one for each generated OpenSpec skill

#### Scenario: Abort multi-agent initialization before projection
- **WHEN** packaged skill loading, generation, or validation fails for any selected uninitialized agent during root initialization
- **THEN** ZPP projects no workflow skill, hook, companion skill, or OpenSpec skill for any selected uninitialized agent in that request

#### Scenario: Generate current sources for a later initialization
- **WHEN** root initialization prepares a newly selected uninitialized agent after a packaged companion skill, local OpenSpec generator, or generated content changes
- **THEN** ZPP reloads the packaged skills, freshly generates that agent's exact inventory, and lets Agent Router project the current sources

#### Scenario: Regenerate an installed integration during synchronization
- **WHEN** root synchronization inspects a selected installed agent
- **THEN** ZPP freshly generates the exact current OpenSpec inventory in disposable repositories and lets Agent Router safely reconcile only the selected user-scope entries

#### Scenario: Reject workflow-owned skill bootstrap
- **WHEN** a workflow run needs an OpenSpec operation skill that is missing, invalid, or stale
- **THEN** the workflow performs no OpenSpec initialization or projection and leaves lifecycle repair to root initialization or synchronization

#### Scenario: Keep grouped workflow lifecycle unchanged
- **WHEN** a caller installs, updates, or removes the grouped workflow integration in user or project scope
- **THEN** ZPP manages only the consolidated skill and native hook and exposes no companion-skill or OpenSpec option

## REMOVED Requirements

### Requirement: Forced complete initialization
**Reason**: Root initialization now creates only integrations for agents carrying no ZPP projection; repair and complete owned reprojection belong exclusively to synchronization.

**Migration**: Use root `zpp init` for an uninitialized agent, root `zpp sync` for drift-selected repair, and root `zpp sync --force` for complete ownership-safe reprojection of an installed integration.
