@toml-trait-catalog
Feature: Author one complete trait family per TOML document
  A trait author can understand one named family without following inheritance,
  templates, providers, or content assembled from other flavors.

  Scenario: Load ordered independent flavors from one document
    Given a bdd trait document with ordered python, python-uv, and flutter flavors
    When ZPP loads the trait document
    Then the document basename identifies the bdd family
    And the flavors retain their authored order and complete bodies
    And no flavor body is assembled from another flavor

  Scenario: Default a family to automatic activation
    Given a trait document that omits activation metadata
    When ZPP loads the trait document
    Then the family activation is automatic

  Scenario: Load an explicit family activation mode
    Given a trait document that declares manual activation
    When ZPP loads the trait document
    Then the family activation is manual

  Scenario: Reject an unsupported activation mode
    Given a trait document that declares an unsupported activation mode
    When ZPP validates the document
    Then the complete document is rejected
    And the failure identifies "meta.activation"

  Scenario: Reject an invalid document atomically
    Given a trait document whose second flavor has no content body
    When ZPP validates the document
    Then the complete document is rejected
    And the failure identifies "trait.1.content"

  Scenario: Reject an unsupported selection policy
    Given a trait document with an unsupported selection policy
    When ZPP validates the document
    Then the complete document is rejected
    And the failure is a trait validation error rather than a stack trace

  Scenario: Reject a non-string categorical facet value
    Given a trait document whose flavor declares a non-string categorical facet
    When ZPP validates the document
    Then the complete document is rejected
    And the failure is a trait validation error rather than a stack trace
