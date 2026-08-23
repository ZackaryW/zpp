## MODIFIED Requirements

### Requirement: Expose a minimal Bundler lease bridge
ZPP SHALL expose only the Bundler lease operations required by its automatic workflow: prepare registered or repo-local store targets, acquire exact store/change members with a ZPP-managed durable owner by default, classify host-reported changed paths, audit changed OpenSpec paths, record one member archive, complete an all-archived bundle, inspect retained bundles for recovery, and perform explicitly owner-authorized abandonment. For each changed path, the Python bridge SHALL first resolve the most-specific registered store root. It SHALL submit paths beneath that root's `openspec/` directory to Bundler's authority audit, report paths elsewhere beneath that registered root as ignored by the OpenSpec lease without treating them as violations, and report paths outside every registered root as violations. An OpenSpec path owned by a registered store outside the bundle's held set SHALL remain a violation.

The Python bridge SHALL own automatic preparation, environment-override validation, and changed-path classification. It SHALL accept explicit owner and UUID-member input for diagnostics or recovery, SHALL expose resolved Bundler UUIDs and bundle results, and SHALL NOT require ordinary workflow callers, skills, or users to supply store UUIDs, owner strings, bundle-management commands, or a manually filtered path list. It SHALL NOT reproduce OpenLease workspace terminology or operations.

#### Scenario: Drive a seamless workflow bundle through the minimal bridge
- **WHEN** an authorized workflow supplies repository roots, change names, and its complete changed-path inventory without internal coordination identifiers
- **THEN** ZPP prepares and acquires the exact members, classifies and audits the paths, records every archive, and completes the bundle through its managed owner identity

#### Scenario: BDD target — Ignore repository-local product paths during OpenSpec audit
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Expose a minimal Bundler lease bridge","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Ignore repository-local product paths during OpenSpec audit"}`
- **THEN** executable acceptance authority is `features/openspec_bundler_integration/openspec_bundler_integration.feature::Ignore repository-local product paths during OpenSpec audit`

#### Scenario: Reject changed paths outside registered repositories
- **WHEN** the host reports a changed path outside every registered repository root
- **THEN** ZPP reports that path as a violation rather than silently ignoring an unknown scope

#### Scenario: Preserve explicit recovery controls
- **WHEN** an operator supplies an explicit owner and UUID-addressed member for diagnosis or recovery
- **THEN** the minimal bridge preserves that explicit identity and returns the raw Bundler result without creating another coordination model

