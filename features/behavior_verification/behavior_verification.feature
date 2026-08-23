@behavior-verification
Feature: Run repository-owned verification through zpp behave
  A repository declares its own verification commands, targets, and gates, and
  ZPP selects affected targets deterministically without creating lease state.
  Mapping validation and impact-selection case matrices are
  proven by unit tests; these scenarios prove the public boundary.

  Scenario: Initialize the dedicated behavior mapping without lease state
    Given a committed repository
    When the caller initializes behavior verification
    Then a version-one behavior mapping exists
    And no session or lease state is created

  Scenario: Preserve an existing version-one mapping
    Given a committed repository with a declared behavior mapping
    When the caller initializes behavior verification again
    Then the mapping is reported as validated
    And the authored mapping content is unchanged

  Scenario: Complete without provider execution when no target is affected
    Given a committed repository with a declared behavior mapping
    When the caller runs the declared bdd command
    Then no targets are reported as affected

  Scenario: Run only conclusively affected targets
    Given a committed repository with a declared behavior mapping
    And a change under one declared target's paths
    When the caller runs the declared bdd command
    Then the provider receives only that target

  Scenario: Apply the complete selection mode
    Given a committed repository with a declared behavior mapping
    When the caller runs the declared bdd command for every target
    Then the provider receives every declared target

  Scenario: Apply an explicit repeated target selection
    Given a committed repository with a declared behavior mapping
    When the caller runs the declared bdd command for one target twice
    Then the provider receives that target once

  Scenario: Apply a declared workflow gate
    Given a committed repository with a declared behavior mapping
    When the caller runs the declared bdd command for the zpp-workflow gate
    Then the provider receives the gate's declared target set

  Scenario: Reject ambiguous selection
    Given a committed repository with a declared behavior mapping
    When the caller combines complete and explicit target selection
    Then the invocation is rejected as mutually exclusive
