## Why

`zpp init --agent <agent>` currently creates only the selected agent's native hooks, so first-time setup can succeed while the ZPP workflow skills required to use the integration remain absent. Selecting an agent during initialization must install that agent's missing global workflow skill surfaces as part of setup.

## What Changes

- Make every agent selected explicitly or interactively during `zpp init` receive its missing user-global ZPP workflow bundle and OpenSpec core operation skills in addition to its native lifecycle hooks.
- Preflight all selected agent skill and hook destinations before changing any selected agent, while retaining the existing boundary that neutral ZPP user-state initialization may complete before a later agent conflict is reported.
- Preserve compatible existing selected-agent projections without rewriting them, and replace intact outdated managed projections through the established complete-installation rules so the selected agent receives every current required skill.
- Keep initialization without a selected agent, an empty interactive selection, and a cancelled selection free of workflow-skill changes.
- Keep unselected-agent discovery and general installed-state maintenance under `zpp update`; initialization reconciles only the agents explicitly or interactively selected for setup.
- Preserve initialization's existing default-profile ownership rule: create the bundled default only when absent and leave an existing valid user-owned default byte-for-byte unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `global-bootstrap-and-agent-setup`: selected-agent initialization changes from hook-only setup to complete missing global agent setup, and its help and selection outcomes must say so.
- `workflow-skill-distribution`: initialization becomes an additional entry point for the complete current global ZPP and OpenSpec skill integration of selected agents without taking over unselected-agent discovery.

## Impact

- Affects `zpp init`, initialization help, selected-agent setup orchestration, global workflow/OpenSpec projection planning, bootstrap BDD, focused CLI and planning tests, and setup documentation.
- Reuses the established agent-native global roots, isolated OpenSpec generation, managed ownership manifests, and selected-agent mutation transaction.
- Adds no command option, dependency, projection root, or persisted-state format.

## Unresolved — Do Not Assume

None. The owner explicitly corrected initialization to install the complete skill integration for each selected target agent; top-level update retains responsibility for discovering and maintaining unselected installed integrations.
