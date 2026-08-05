Feature: Compile authored traits for resolution
  ZPP users resolve source-authoritative Markdown traits while derived caches stay
  lazy, independent, and invisible to the meaning of the returned guidance.

  Scenario: Resolution compiles only participating authored layers
    Given an initialized global layer has multiple valid activated authored traits
    And one trait omits optional frontmatter while another contains order, config, skill lookup, and UTF-8 text
    And an inactive profile also has an authored trait
    And no derived trait cache exists
    When the user runs zpp resolve for an existing directory
    Then resolution succeeds with complete native documents for the activated global traits
    And the resolved bodies preserve their authored whitespace and UTF-8 text
    And the participating global layer gains one independent compiled cache
    And no cache is created for the inactive profile
    And every authored trait file remains byte-for-byte unchanged

  Scenario: Changed authored Markdown supersedes stale derived data
    Given an activated authored trait has previously been resolved
    And its authored body changes after the derived cache was certified
    When the user runs zpp resolve for its target
    Then resolution succeeds with the changed advisory body
    And no stale advisory body is returned
    And the authored trait remains authoritative

  Scenario: Invalid participating traits reject the complete resolution
    Given a participating layer has stale derived data
    And multiple authored traits in that layer are invalid
    When the user runs zpp resolve for its target
    Then resolution fails as a managed-state rejection
    And stdout is empty
    And stderr identifies every invalid authored source without a stack trace
    And no valid subset or stale trait document is returned
