@trait-resolution
Feature: Deliver resolved trait bodies through the public boundary
  A workflow receives deterministic complete bodies and inspectable diagnostics
  without hidden authority. Selection-policy, evidence, and context-authority
  case matrices are proven by unit tests; these scenarios prove that resolution
  reaches a caller through `zpp resolve`.

  Background:
    Given a repository carrying an automatic and a manual trait family

  Scenario: Render complete bodies for prompt injection by default
    When a caller resolves the repository for Python
    Then the automatic family's complete body is rendered
    And no structured diagnostics are rendered

  Scenario: Exclude manual families from common resolution
    When a caller resolves the repository for Python
    Then the manual family's body is not rendered

  Scenario: Query a manual family with normal activation
    When a caller resolves only the manual family for Python
    Then the manual family's complete body is rendered

  Scenario: Reject an unknown named family
    When a caller resolves an unknown named family
    Then resolution is rejected and identifies the unknown family

  Scenario: Render structured diagnostics only when requested
    When a caller resolves the repository for Python with explanation
    Then structured selection diagnostics are rendered

  Scenario: Leave an unmatched family inactive
    When a caller resolves the repository for an unmatched language
    Then no trait body is rendered
