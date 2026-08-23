## MODIFIED Requirements

### Requirement: Automatically hold atomic store bundles through archival completion
Before governed OpenSpec mutation, the active mutation-authorized complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) or a directly invoked mutating `zpps-*` component SHALL request `zpps-workflow-kernel` to acquire one atomic Bundler lease bundle for the exact resolved repository/change targets. The kernel SHALL invoke ZPP's Python runtime, which SHALL automatically register an unambiguously resolved repo-local OpenSpec root when needed, create or validate its store-owned Bundler UUID manifest, resolve its exact store UUID, and use a ZPP-managed durable owner identity from the selected product home without asking the user for any internal coordination identifier. Skills SHALL NOT implement registration, identity persistence, environment handling, or lease transitions. A parent member SHALL use Bundler's descendant closure, and independent related members SHALL be requested as explicit multi-roots without a dependency edge. ZPP SHALL surface genuine registration, manifest, topology, ownership, and lease conflicts before product mutation, audit changed OpenSpec paths, record each successful member archive, and complete the bundle only after every member is archived; explicitly authorized bundle abandonment SHALL be the only recovery release. Neither the kernel nor a component SHALL select workflow continuation or expand the acquired member set.

#### Scenario: BDD target — Bootstrap runtime coordination without internal prompts
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Bootstrap runtime coordination without internal prompts"}`
- **THEN** executable acceptance authority is `features/openspec_bundler_integration/openspec_bundler_integration.feature::Bootstrap runtime coordination without internal prompts`

#### Scenario: Reuse automatic coordination identities
- **WHEN** a later authorized workflow targets a prepared store through the same selected ZPP home
- **THEN** ZPP reuses the stored store UUID and durable owner identity while acquiring only the new exact change member

#### Scenario: Surface a real bundle conflict
- **WHEN** automatic preparation resolves a store closure already held by an incompatible active bundle
- **THEN** ZPP reports the conflict before product mutation and does not bypass or replace the existing bundle

#### Scenario: BDD target — Honor strict coordination overrides without bypassing the lease
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Honor strict coordination overrides without bypassing the lease"}`
- **THEN** executable acceptance authority is `features/openspec_bundler_integration/openspec_bundler_integration.feature::Honor strict coordination overrides without bypassing the lease`

#### Scenario: Reject an invalid coordination override
- **WHEN** `ZPP_WORKFLOW_COORDINATION` is malformed, unsupported, ambiguous, or inconsistent with registered store evidence
- **THEN** ZPP reports the override error before registration, manifest, lease, or product mutation

#### Scenario: BDD target — Retain an automatic bundle until every change archives
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Retain an automatic bundle until every change archives"}`
- **THEN** executable acceptance authority is `features/openspec_bundler_integration/openspec_bundler_integration.feature::Retain an automatic bundle until every change archives`

#### Scenario: BDD target — Acquire automatically before governed OpenSpec mutation
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Acquire automatically before governed OpenSpec mutation"}`
- **THEN** executable acceptance authority is `features/openspec_bundler_integration/openspec_bundler_integration.feature::Acquire automatically before governed OpenSpec mutation`

### Requirement: Expose a minimal Bundler lease bridge
ZPP SHALL expose only the Bundler lease operations required by its automatic workflow: prepare registered or repo-local store targets, acquire exact store/change members with a ZPP-managed durable owner by default, audit changed OpenSpec paths, record one member archive, complete an all-archived bundle, inspect retained bundles for recovery, and perform explicitly owner-authorized abandonment. The Python bridge SHALL own automatic preparation and environment-override validation. It SHALL accept explicit owner and UUID-member input for diagnostics or recovery, SHALL expose resolved Bundler UUIDs and bundle results, and SHALL NOT require ordinary workflow callers, skills, or users to supply store UUIDs, owner strings, or bundle-management commands. It SHALL NOT reproduce OpenLease workspace terminology or operations.

#### Scenario: Drive a seamless workflow bundle through the minimal bridge
- **WHEN** an authorized workflow supplies repository roots and change names without internal coordination identifiers
- **THEN** ZPP prepares and acquires the exact members, audits changed paths, records every archive, and completes the bundle through its managed owner identity

#### Scenario: Preserve explicit recovery controls
- **WHEN** an operator supplies an explicit owner and UUID-addressed member for diagnosis or recovery
- **THEN** the minimal bridge preserves that explicit identity and returns the raw Bundler result without creating another coordination model
