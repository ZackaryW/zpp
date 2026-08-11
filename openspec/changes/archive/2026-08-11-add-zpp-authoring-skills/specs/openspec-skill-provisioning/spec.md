## MODIFIED Requirements

### Requirement: Initialization-only OpenSpec provisioning
Root `zpp init` SHALL be the only ZPP command that generates or projects OpenSpec operation skills. Every invocation with selected agents SHALL freshly detect OpenSpec and regenerate the exact operation inventory for every selected agent before projecting any selected workflow skill, native hook, packaged authoring skill, or generated skill. ZPP SHALL also load the complete packaged `zpp-configure-behave` and `zpp-author-trait` source set before projection. After complete preparation succeeds, Agent Router SHALL install or safely reconcile the consolidated skill, native hook, two packaged authoring skills, and six generated OpenSpec skills in each selected agent's user scope.

Within each selected agent, result and projection order SHALL be `zpp-workflow`, `zpp-session`, `zpp-configure-behave`, `zpp-author-trait`, then the canonical OpenSpec operation skill order. Grouped `zpp workflow install|update|remove` SHALL continue to manage only `zpp-workflow` and `zpp-session` in their selected scope. ZPP SHALL expose no authoring-skill or OpenSpec lifecycle option on that command group.

#### Scenario: Initialize a ready workflow integration
- **WHEN** root initialization succeeds for one or more selected agents
- **THEN** Agent Router installs or safely reconciles the consolidated skill, native hook, two packaged authoring skills, and all six freshly generated OpenSpec skills in each selected agent's user scope

#### Scenario: Abort multi-agent initialization before projection
- **WHEN** packaged skill loading, generation, or validation fails for any selected agent during root initialization
- **THEN** ZPP projects no workflow skill, hook, authoring skill, or OpenSpec skill for any selected agent in that request

#### Scenario: Regenerate on repeated initialization
- **WHEN** a caller runs root initialization after a packaged authoring skill, local OpenSpec generator, or generated content changes
- **THEN** ZPP reloads the packaged skills, freshly generates all selected inventories, and lets Agent Router safely reconcile changed owned projections

#### Scenario: Keep grouped workflow lifecycle unchanged
- **WHEN** a caller installs, updates, or removes the grouped workflow integration in user or project scope
- **THEN** ZPP manages only the consolidated skill and native hook and exposes no authoring-skill or OpenSpec option
