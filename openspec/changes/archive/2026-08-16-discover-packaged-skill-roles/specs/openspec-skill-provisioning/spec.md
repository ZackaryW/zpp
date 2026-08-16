## MODIFIED Requirements

### Requirement: Initialization-only OpenSpec provisioning
Root `zpp init` SHALL be the only ZPP command that generates or projects OpenSpec operation skills. Every invocation with selected agents SHALL freshly detect OpenSpec and regenerate the exact operation inventory for every selected agent before projecting any selected workflow skill, native hook, packaged companion skill, or generated skill. ZPP SHALL also load the complete discovered packaged companion source set before projection. After complete preparation succeeds, Agent Router SHALL install or safely reconcile the consolidated skill, native hook, every discovered packaged companion skill, and six generated OpenSpec skills in each selected agent's user scope.

Within each selected agent, result and projection order SHALL be `zpp-workflow`, `zpp-session`, every packaged companion skill in the deterministic packaged order, then the canonical OpenSpec operation skill order. Grouped `zpp workflow install|update|remove` SHALL continue to manage only `zpp-workflow` and `zpp-session` in their selected scope. ZPP SHALL expose no companion-skill or OpenSpec lifecycle option on that command group.

#### Scenario: Initialize a ready workflow integration
- **WHEN** root initialization succeeds for one or more selected agents
- **THEN** Agent Router installs or safely reconciles the consolidated skill, native hook, every discovered packaged companion skill, and all six freshly generated OpenSpec skills in each selected agent's user scope

#### Scenario: Report one lifecycle result per projected asset
- **WHEN** root initialization completes for one selected agent
- **THEN** the ordered lifecycle report contains exactly one result for the workflow skill, one for the native hook, one for each discovered companion skill, and one for each generated OpenSpec skill

#### Scenario: Abort multi-agent initialization before projection
- **WHEN** packaged skill loading, generation, or validation fails for any selected agent during root initialization
- **THEN** ZPP projects no workflow skill, hook, companion skill, or OpenSpec skill for any selected agent in that request

#### Scenario: Regenerate on repeated initialization
- **WHEN** a caller runs root initialization after a packaged companion skill, local OpenSpec generator, or generated content changes
- **THEN** ZPP reloads the packaged skills, freshly generates all selected inventories, and lets Agent Router safely reconcile changed owned projections

#### Scenario: Keep grouped workflow lifecycle unchanged
- **WHEN** a caller installs, updates, or removes the grouped workflow integration in user or project scope
- **THEN** ZPP manages only the consolidated skill and native hook and exposes no companion-skill or OpenSpec option

### Requirement: Forced complete initialization
Root `zpp init` SHALL accept `--force`. Forced initialization SHALL still prepare and validate every selected source before projection, then SHALL request replacement or reprojection of every selected agent's `zpp-workflow` skill, `zpp-session` hook, every discovered packaged companion skill, and six generated OpenSpec skills through Agent Router. It SHALL permit replacement of diverged skill content only when Agent Router confirms matching ownership, SHALL preserve unmanaged or mismatched destinations, and SHALL NOT mutate native destinations directly.

#### Scenario: Reproject a current complete integration
- **WHEN** a caller invokes `zpp init --force` for an agent whose complete integration is already current
- **THEN** ZPP requests Agent Router reprojection for every selected asset rather than treating the request as ordinary idempotent initialization

#### Scenario: Replace an owned diverged skill
- **WHEN** forced initialization encounters a selected skill whose content diverged but whose Agent Router ownership matches
- **THEN** Agent Router replaces that owned skill with the freshly prepared source and initialization continues

#### Scenario: Preserve an unmanaged destination
- **WHEN** forced initialization encounters an unmanaged or mismatched-ownership selected destination
- **THEN** ZPP reports the Agent Router conflict and performs no direct overwrite or ownership adoption
