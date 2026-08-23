## Context

ZPP currently centralizes OpenLease integration in document and coordination adapters, but direct code also imports OpenLease Git, process, error, callback, space, and configuration types. Bundler now provides raw repository attachments, exact store namespaces, registered-store parent topology, and durable atomic multi-root lease bundles. The removed OpenLease spaces, dependency edges, callbacks, successors, reconciliation, handoff, cleanup, and preparation-repair concepts are not ZPP requirements after this cutover.

The Bundler manifest correction is a prerequisite: ZPP will use `[extensions.zpp-traits]` in the sole version-1 schema and will not support the prior version-2 draft.

## Goals / Non-Goals

**Goals:**

- Remove OpenLease as a runtime and build dependency without compatibility code.
- Keep ZPP schemas, composition, behavior execution, and mutation authority explicit in ZPP.
- Use store UUIDs and parent relationships as the authority graph and explicit multi-root bundles as temporary crews, without a second dependency graph.
- Keep ordinary resolution read-only and state-free.

**Non-Goals:**

- Migrating, deleting, or interpreting old OpenLease state.
- Retaining old environment variables, flags, IDs, or command aliases.
- Recreating a generic configuration runtime inside ZPP.
- Recreating removed OpenLease workspace lifecycle behavior in Bundler or ZPP.

## Decisions

### Introduce one ZPP Bundler composition adapter

A new ZPP-owned utility constructs `OpenSpecStoreProvider`, `AttachmentService`, and `LeaseCoordinator` with a lease repository beneath the selected ZPP home. CLI and application code depend on ZPP ports rather than importing Bundler types everywhere.

### Parse and compose attachments in ZPP

Repository trait families remain separately enumerated exact documents, and `zpp.behave.yaml` remains a dedicated repository document. ZPP reads their raw bytes through Bundler and owns TOML/YAML parsing. Store attachment input comes from `zpp-traits` namespaces selected along the root-to-target topology chain; siblings never participate.

### Let the workflow own automatic mutation-time leases

Read-only resolution has no session. When a workflow is about to open or mutate one or more OpenSpec changes, it supplies one durable owner identity and the exact store/change members and acquires the atomic Bundler bundle before mutation. As each member archives, the workflow records it and explicitly completes the bundle after all members are archived. Conflict remains visible and blocks mutation. There is no separate claim, preview, go-ahead, permit, unlock, or workspace command flow.

### Use only Bundler containment and multi-root crews

Store-manifest `parent` relationships provide hierarchical closure. Independent stores that participate in one workflow are requested as multiple roots in one atomic bundle. This already expresses ZPP's authority need, so the cutover removes OpenLease dependency relationships instead of adding a second non-containment Bundler edge.

### Remove workspace lifecycle and compatibility identities

The `zpp workspace` command group, `zpp-workspace-management` packaged skill, `zpp-session` hook identity, successor and reconciliation state, handoff, cleanup, preparation repair, and all corresponding adapters are deleted. Automatic trait injection remains under the new `zpp-traits` hook identity, and automatic workflow progression performs the Bundler lease lifecycle at the governed mutation boundary.

### Isolate new state without touching old state

ZPP supplies an explicit `LeaseStateRepository` rooted at the selected home's `bundler` child. Reset manages only that new boundary after cutover. The old `openlease` child is outside mutation authority and remains ignored.

## Risks / Trade-offs

- **Automatic acquisition can encounter a conflict at mutation time** → Surface the Bundler conflict and perform no governed mutation; no stale preview or separate go-ahead is retained.
- **Removed workspace commands may have existing callers** → This is an intentional breaking cut with no aliases or translation layer.
- **Removing sessions changes CLI and hook outputs** → Shape replacement behavior from the accepted no-session contract and remove obsolete scenario targets rather than aliasing them.
- **ZPP must own codec and process utilities** → Reuse standard-library TOML and subprocess facilities plus the existing YAML dependency surface; keep utilities narrow and covered by focused tests.

## Migration Plan

1. Pin the completed Bundler single-schema change.
2. Replace dependencies, state layout, document adapters, and automatic workflow coordination in one breaking series with no mixed provider runtime.
3. Remove the workspace CLI, companion skill, session hook identity, dependency edges, and every OpenLease import, feature target, specification reference, environment variable, flag, and lockfile entry.
4. Verify the complete ZPP public surface and archive only when residual searches show no compatibility code.
