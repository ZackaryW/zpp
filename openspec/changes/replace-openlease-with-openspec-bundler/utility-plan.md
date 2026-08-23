# Disposable Utility Plan

## Dependency and process floor

- Replace the OpenLease dependency with `openspec-bundler` from the adjacent checked-out package for this unpublished integration checkpoint, plus an explicit PyYAML dependency for the ZPP-owned behavior codec.
- Add `zpp.utils.processes.ProcessResult`, `ProcessRunner.run(argv, *, cwd) -> ProcessResult`, and `SubprocessRunner.run(...)` so behavior adapters retain a typed shell-free process boundary without importing OpenLease.

## Attachment composition

- Add `zpp.utils.bundler.BundlerDocuments(stores, attachments)` with `read_repository(root) -> BoundRepositoryTraits`, `initialize_context(root) -> BoundTraitDocument`, `initialize_trait(root, family, values) -> BoundTraitDocument`, `read_store_chain(target) -> tuple[BoundTraitSource, ...]`, `initialize_behavior(root) -> BehaviorInitializationReport`, and `run_behavior(root, request) -> BehaviorExecutionReport`.
- Repository reads enumerate only `.zpp/zpp.toml`, `.zpp/traits/*.toml`, and `zpp.behave.yaml` through exact Bundler repository attachments. TOML uses `tomllib`; YAML uses `yaml.safe_load`/`safe_dump`; ZPP owns validation and initialization payloads.
- `read_store_chain` discovers the topology, selects the deepest managed store root containing the target, follows parent UUIDs to the root, reads only `zpp-traits`, converts its `context` and `traits` tables into ordered store sources, and excludes siblings.

## Lease bridge and home boundary

- Add `zpp.utils.bundler.BundlerLeaseService(home, stores)` with `acquire(owner_id, members)`, `status()`, `audit(bundle_uuid, paths)`, `record_archive(bundle_uuid, owner_id, member)`, `complete(bundle_uuid, owner_id)`, and `abandon(bundle_uuid, owner_id)`, delegating directly to `LeaseCoordinator` with `LeaseStateRepository(home.state_root)`.
- Change `ZppHome.state_root` to `<home>/bundler` and rename reset preparation to provider-neutral `PreparedBundlerState`; fresh preparation creates an empty Bundler repository without reading the legacy `<home>/openlease` path.
- Replace `zpp workspace` with the minimal `zpp lease` commands `acquire`, `status`, `audit`, `archive`, `complete`, and `abandon`; accept canonical UUID/member inputs and emit typed JSON from Bundler results.

## Hard-cut removal and artifact identities

- Remove OpenLease adapters, coordination primitives, session/space flags and environment variables, callback behavior, obsolete feature support, and compatibility tests.
- Rename every packaged hook file and inventory identity from `zpp-session` to `zpp-traits`; remove the packaged `zpp-workspace-management` directory and workflow delegation text.
- Update resolution, traits, behavior, reset, workflow projection, examples, and canonical tests to use the new utilities and public surfaces.

This plan is disposable after focused fail-first tests and independent utility verification are GREEN.
