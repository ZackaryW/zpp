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
  Scenario: Acquire automatically before governed OpenSpec mutation
    Given an automatic workflow with exact store and change members
    When the workflow begins governed mutation through the minimal lease bridge
    Then one Bundler bundle holds the declared roots and descendant closure before mutation
    And no session claim permit or dependency edge is created

  @lease @archive
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
