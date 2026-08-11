## Why

ZPP exposes precise repository behavior and trait schemas, but an agent currently has no packaged operational guidance for authoring those documents well. Users must reconstruct segmentation, activation, selection, evidence, validation, and authority boundaries from implementation details or general documentation.

## What Changes

- Package a manual `zpp-configure-behave` skill that helps an agent inspect a repository, author or revise its root `zpp.behave.yaml`, segment verification around stable execution and cache boundaries, preserve conservative affected selection, and validate the resulting mapping through existing ZPP commands.
- Package a manual `zpp-author-trait` skill that helps an agent create or revise one repository trait family, choose activation and selection deliberately, keep flavors self-contained, distinguish facets from observable evidence, and validate resolution through existing ZPP commands.
- Keep both skills outside hooks, trait resolution, workflow stages, and executable process authority. They act only for an explicit authoring request and introduce no new CLI command.
- Install or safely reconcile both skills in user scope for every agent selected by root `zpp init`, after all selected OpenSpec inventories have passed generation and validation.
- Include both packaged skills in confirmed reset's complete standard preflight and ownership-safe removal. Modified, unmanaged, or ambiguous copies remain conflicts; generated OpenSpec skills retain their separate forced-deletion contract.
- Keep `zpp workflow install|update|remove` unchanged and limited to `zpp-workflow` plus `zpp-session`.
- Verify the authoring content and lifecycle with focused unit and integration tests; no BDD feature surface is added for this skill-authoring change.

## Capabilities

### New Capabilities

- `repository-authoring-skills`: Defines the identities, manual invocation boundaries, authoring guidance, validation responsibilities, and packaging of the behavior-mapping and trait-authoring skills.

### Modified Capabilities

- `openspec-skill-provisioning`: Extends root initialization composition with the two packaged authoring skills while retaining all-agent OpenSpec generation preflight and unchanged grouped workflow commands.
- `product-home-lifecycle`: Extends confirmed reset's standard preflight and removal set with the two packaged authoring skills without expanding forced deletion.

## Impact

- Packaged assets: two new skill directories under `zpp/artifacts/skills`.
- Artifact API: deterministic loading of the packaged authoring skill set.
- Root initialization: two additional Agent Router skill projections per selected agent.
- Confirmed reset: two additional standard inspected and removed projections per supported agent.
- Tests and README: authoring content, installation order, reset safety, unchanged CLI shape, and current installed inventory.
- No new dependency, hook, trait family, behavior mapping, CLI command, provider adapter, or workflow stage is introduced.

## Unresolved — Do Not Assume

None.
