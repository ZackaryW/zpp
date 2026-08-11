@toml-trait-catalog
Feature: Author one complete trait family per TOML document
  A trait author can understand one named family without following inheritance,
  templates, providers, or content assembled from other flavors.

  Scenario: Load ordered independent flavors from one document
    Given a bdd trait document declares extend selection
    And it contains ordered Python, Python with uv, and Flutter flavors
    And every flavor has its own complete content body
    When ZPP loads the trait document
    Then the document basename identifies the bdd family
    And the flavors retain their authored order and complete bodies
    And no flavor inherits or generates content from another flavor

  Scenario: Reject an invalid document atomically
    Given one flavor in a trait document has no content body
    When ZPP validates the document
    Then the complete document is rejected
    And the failure identifies the source family flavor position and invalid field
    And no partial family is made available

  Scenario: Reject unsupported metadata and facet values
    Given a trait document has an unsupported selection policy
    And one flavor declares a non-string categorical constraint
    When ZPP validates the document
    Then the complete document is rejected without a stack trace

  Scenario: Layer one family across repository space and global sources
    Given repository space and global sources contribute bdd trait documents
    And each document contains several ordered flavors
    When ZPP composes the effective bdd family
    Then repository flavors precede space flavors
    And space flavors precede global flavors
    And each document retains its authored flavor order
    And the repository document supplies the effective selection policy

  Scenario: Explicitly replace inherited family contributions
    Given a repository bdd document declares repository-overwrite mode
    And space and global bdd documents are available
    When ZPP composes the effective bdd family
    Then only repository flavors remain eligible for selection
    And the repository selection policy governs the family

  Scenario: Reject repository overwrite outside repository scope
    Given a space or global trait document declares repository-overwrite mode
    When ZPP validates that source contribution
    Then the source declaration is rejected
