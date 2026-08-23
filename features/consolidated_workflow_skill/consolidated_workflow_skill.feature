@consolidated-workflow-skill
Feature: Package one consolidated ZPP workflow authority
  ZPP packages exactly one workflow skill alongside a standard trait collection
  whose families, activation, and facets load and decode from the distribution.
  Workflow conduct obligations are canonical requirements, not scenarios.

  Background:
    Given the packaged workflow assets are loaded

  Scenario: Package one consolidated workflow skill
    Then the packaged skill is named zpp-workflow
    And the packaged skill is compatible with every supported agent
    And the packaged skill carries a SKILL.md document

  Scenario: Package automatic Bundler lease progression
    Then the workflow acquires exact store change members before governed mutation
    And it records archives and completes the bundle during finalization
    And it delegates no workspace successor reconciliation or cleanup operation

  Scenario: Keep workflow authority out of the trait collection
    Then no workflow authority family is packaged

  Scenario: Package the reconciled standard behavior collection
    Then the packaged trait families are exactly the standard collection

  Scenario: Declare BDD execution modes as trait facets
    When the bdd-execution family is decoded
    Then its flavors declare the manual disabled complete and targeted modes with a trailing default
    And every bdd-execution flavor carries a non-empty body

  Scenario: Declare universal activation and tool facets
    When the zero-assumptions and tooling families are decoded
    Then zero-assumptions declares always-run activation
    And tooling declares exactly the rg and jq facets
