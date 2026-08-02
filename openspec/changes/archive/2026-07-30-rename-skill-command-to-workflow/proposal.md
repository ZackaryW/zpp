## Why

The public `skill` command name suggests generic management of arbitrary individual skills, while ZPP actually manages one owned standard workflow bundle. Naming the command `workflow` presents the product concept and keeps the bundle's internal composition out of the public interface.

## What Changes

- **BREAKING** Replace the `zpp skill` command group with `zpp workflow`.
- Expose the existing `install`, `update`, and `remove` operations and their accepted arguments and options under `zpp workflow`.
- Remove `skill` from root help and present `workflow` as management of ZPP's standard workflow bundle.
- Update user-facing validation, prompts, reports, executable feature contracts, packaged workflow guidance, and canonical command references to use the new public name.
- Preserve the existing bundle lifecycle behavior, agent selection, global and local scopes, compatibility checks, ownership checks, confirmation behavior, and automatic-trait governance boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Rename the public lifecycle command group from `skill` to `workflow` without changing its lifecycle behavior.
- `global-bootstrap-and-agent-setup`: Present `workflow`, rather than `skill`, in the root command surface.

## Impact

- Public CLI: root help and the standard workflow bundle lifecycle command paths.
- Executable behavior: `features/bootstrap_and_agents.feature` and `features/workflow_skill_distribution.feature`.
- Implementation: Typer command registration, lifecycle command diagnostics, and affected step bindings.
- Distribution guidance: packaged permanent workflow skills that name the public lifecycle command.
- Canonical contracts: the two modified capabilities listed above.
- Dependencies and utility algorithms: no change is required by the accepted product outcome.

## Unresolved — Do Not Assume

None. The owner explicitly selected `workflow` and approved the breaking rename.
