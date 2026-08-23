## Why

ZPP currently depends on OpenLease for document binding, configuration overlays, sessions, authority coordination, and workspace operations even though the desired model is registered OpenSpec store authority plus framework-owned composition. ZPP should hard-cut to `openspec-bundler`, own its schemas and behavior explicitly, and retain no OpenLease compatibility surface.

## What Changes

- **BREAKING** Remove the OpenLease dependency, state model, environment variables, identifiers, callbacks, adapters, and compatibility paths from ZPP.
- Bind `.zpp` TOML documents and `zpp.behave.yaml` as raw repository attachments while ZPP owns parsing, validation, initialization payloads, and execution.
- Read ZPP store configuration from bare-key `[extensions.zpp-traits]` namespaces and compose only the repository input plus the selected store's root-to-child chain, excluding siblings.
- Make `zpp-workflow` automatically acquire one durable Bundler store/change bundle before governed OpenSpec mutation and record/complete it as changes archive, without sessions, claims, permits, or a separate go-ahead command.
- Keep read-only trait resolution session-free and state-free.
- Move ZPP-owned lease state under the selected ZPP home without reading, converting, or deleting prior `openlease` state.
- Remove the complete `zpp workspace` command group, `zpp-workspace-management` skill, legacy hook identity, and all old selections instead of aliasing them.
- Use Bundler parent/child containment and explicit multi-root bundles for related work; add no OpenLease-style dependency edge.

## Capabilities

### New Capabilities

- `openspec-bundler-integration`: Define ZPP's hard-cut dependency, attachment composition, store lease lifecycle, and absence of OpenLease compatibility.

### Modified Capabilities

- `automatic-trait-hooks`: Keep automatic trait injection while removing session establishment and renaming the hook to `zpp-traits`.
- `behavior-verification`: Keep direct verification execution and remove OpenLease callbacks and coordination state.
- `blast-surface-permit`: Remove claims, closure previews, permits, explicit go-ahead, and unlock behavior.
- `consolidated-workflow-skill`: Automatically coordinate Bundler leases around governed OpenSpec mutation and remove workspace-management delegation.
- `openlease-session-lifecycle`: Remove registration, session, space, and relationship-gate behavior.
- `openspec-skill-provisioning`: Project the renamed hook and stop discovering the removed workspace companion.
- `product-home-lifecycle`: Replace the OpenLease state child with an isolated Bundler lease-state child without migrating old state.
- `repository-trait-bootstrap`: Use Bundler repository attachments and remove the `workspace` command group.
- `toml-trait-catalog`: Compose repository input with the selected store's root-to-child `zpp-traits` chain instead of repository/space/global sources.
- `workspace-management-skill`: Remove the packaged manual workspace lifecycle skill.
- `zpp-coordination-commands`: Remove the explicit OpenLease coordination command surface.

## Impact

- Affects ZPP dependencies, lockfile, utilities, CLI, product-home state, packaged skills, canonical specifications, unit tests, and multiple capability-owned Behave roots.
- Pins the completed Bundler single-schema checkpoint and uses `[extensions.zpp-traits]` from version-1 store manifests.
- Reconciles repository traits, behavior verification, session lifecycle, blast-surface permits, coordination commands, product-home lifecycle, automatic hooks, workflow instructions, and workspace management in one hard cut.
- Successor creation, reconciliation, handoff, dependency edges, cleanup, preparation repair, and their recovery state are removed rather than replaced.
