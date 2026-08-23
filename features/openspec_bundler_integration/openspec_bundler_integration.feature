@openspec-bundler-integration
Feature: Integrate OpenSpec Bundler without an OpenLease compatibility surface
  ZPP needs raw framework-owned attachments and automatic store/change leasing
  without retaining the former workspace coordination model.

  @attachments @monorepo
  Scenario: Compose repository and selected-store inputs without a sibling
    Given a monorepo with repository traits and parent child and sibling zpp-traits namespaces
    When ZPP resolves traits for the selected child through its public interface
    Then repository parent and selected-child inputs are composed in order
    And the sibling input and lease state are absent

  @lease @workflow
  # zpp-spec: {"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Acquire automatically before governed OpenSpec mutation"}
  Scenario: Acquire automatically before governed OpenSpec mutation
    Given an automatic workflow with exact store and change members
    When the workflow begins governed mutation through the minimal lease bridge
    Then one Bundler bundle holds the declared roots and descendant closure before mutation
    And no session claim permit or dependency edge is created

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Bootstrap runtime coordination without internal prompts"}
  @lease @runtime @bootstrap
  Scenario: Bootstrap runtime coordination without internal prompts
    Given a fresh ZPP home and an unprepared registered OpenSpec store
    When the runtime coordinates the exact store and change without internal identifiers
    Then the store and selected ZPP home gain stable coordination identities
    And one exact Bundler bundle is acquired under the managed owner

  # zpp-spec: {"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Honor strict coordination overrides without bypassing the lease"}
  @lease @runtime @override
  Scenario: Honor strict coordination overrides without bypassing the lease
    Given a prepared store and a strict workflow owner override
    When the runtime coordinates the exact store and change without internal identifiers
    Then the exact bundle uses the overridden owner
    And coordination remains leased rather than bypassed

  @lease @archive
  # zpp-spec: {"root":"repo:openspec","capability":"openspec-bundler-integration","requirement":"Automatically hold atomic store bundles through archival completion","feature":"features/openspec_bundler_integration/openspec_bundler_integration.feature","scenario":"Retain an automatic bundle until every change archives"}
  Scenario: Retain an automatic bundle until every change archives
    Given an automatic workflow bundle with two store and change members
    When the workflow records only one member archive
    Then the complete bundle remains held
    When the workflow records the remaining archive and completes the bundle
    Then the complete bundle is released

  @hard-cut
  Scenario: Expose no OpenLease workspace compatibility surface
    Given the installed ZPP command hook and packaged-skill inventories
    When their public identities are inspected
    Then the minimal lease bridge and zpp-traits hook are present
    And workspace sessions permits dependencies successors and compatibility aliases are absent

  @state
  Scenario: Ignore legacy state while using the Bundler state boundary
    Given a selected ZPP home containing legacy OpenLease state
    When an automatic workflow acquires its first store bundle
    Then only the selected home's bundler child gains lease state
    And the legacy state remains unchanged
