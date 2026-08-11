## Why

ZPP's consolidated workflow requires component-owned OpenSpec operation skills, but a fresh `zpp init` currently installs only the ZPP workflow skill and native trait hook. The resulting integration cannot follow its own specification authority without a separate undocumented setup step.

## What Changes

- Restore generation of the six canonical OpenSpec operation skills from the locally installed OpenSpec CLI for every selected agent.
- Make root `zpp init` the only OpenSpec provisioning surface and force fresh generation before Agent Router reconciles the generated user-scope skills.
- Keep grouped `zpp workflow install|update|remove` limited to the consolidated workflow skill and native hook, with no OpenSpec update option or separate generated-skill control surface.
- Validate the OpenSpec version and the complete generated inventory for every selected agent before projecting any integration asset.
- Add ZPP provenance to generated OpenSpec skills so Agent Router can safely reconcile and remove them without ZPP writing native destinations directly.
- Extend confirmed product reset to delete the six ZPP-provisioned OpenSpec skills for every supported agent in user scope by canonical name through Agent Router.
- Keep installation of the OpenSpec CLI outside ZPP authority and fail cleanly before projection mutation when the executable or generated inventory is unavailable.

## Capabilities

### New Capabilities

- `openspec-skill-provisioning`: Defines generated OpenSpec operation skill inventory, provenance, validation, scope policy, Agent Router projection, and lifecycle failure behavior.

### Modified Capabilities

- `consolidated-workflow-skill`: Defines a complete installed workflow integration as the consolidated ZPP skill, native hook, and required OpenSpec operation skills.
- `product-home-lifecycle`: Extends complete reset cleanup to force-delete ZPP-provisioned OpenSpec operation skills after the existing complete preflight boundary.

## Impact

- Public CLI: no new OpenSpec update command or workflow lifecycle option is introduced; root initialization performs regeneration.
- Runtime utilities: a focused OpenSpec generator adapter detects the CLI version, generates per-agent skills in temporary repositories, validates the exact inventory, and attaches provenance.
- Agent integration: Agent Router remains the only owner of native skill projection and removal.
- Reset: the all-agent user cleanup expands to delete six generated OpenSpec skills per agent through Agent Router.
- Tests, feature contracts, README, and packaging metadata cover fresh bootstrap, forced owned cleanup, generation failures, unchanged workflow lifecycle commands, and complete reset.

## Unresolved — Do Not Assume

None.
