## MODIFIED Requirements

### Requirement: Automatically hold atomic store bundles through archival completion
Before governed OpenSpec mutation, the active mutation-authorized complete playbook (`zpp-new-feature`, `zpp-fix-bug`, `zpp-scaffold`, or `zpp-legacy-workflow`, whether selected directly or routed by `zpp-auto`) or a directly invoked mutating `zpps-*` component SHALL request `zpps-workflow-kernel` to acquire one atomic Bundler lease bundle for its durable owner identity and exact registered store UUID/change members. A parent member SHALL use Bundler's descendant closure, and independent related members SHALL be requested as explicit multi-roots without a dependency edge. ZPP SHALL surface conflicts before mutation, audit changed OpenSpec paths, record each successful member archive, and complete the bundle only after every member is archived; explicitly authorized bundle abandonment SHALL be the only recovery release. Neither the kernel nor a component SHALL select workflow continuation or expand the acquired member set.

#### Scenario: BDD target — Retain an automatic bundle until every change archives
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Retain an automatic bundle until every change archives`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps

#### Scenario: BDD target — Acquire automatically before governed OpenSpec mutation
- **WHEN** executable behavior is covered by `features/openspec_bundler_integration/openspec_bundler_integration.feature::Acquire automatically before governed OpenSpec mutation`
- **THEN** that exact feature scenario is the executable authority and this specification does not repeat its steps
