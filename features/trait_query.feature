Feature: Realtime trait query surface
  Agents consume traits live - list, show, effective - with provenance.
  No compiled agent artifact exists anywhere.

  Scenario: Show prints a single trait's content
    Given a user trait "acme-style" with content "ACME STYLE RULES"
    When I run "zpp trait show acme-style"
    Then the command succeeds
    And the output contains "ACME STYLE RULES"

  Scenario: Show fails loudly for an unknown trait
    When I run "zpp trait show nope"
    Then the command fails
    And the error output contains "unknown trait"

  Scenario: Effective concatenates in tier application order
    Given a self-governed repo whose store tier applies "ponytail" and whose repo tier applies "structure"
    When I run "zpp trait effective" against that repo
    Then the command succeeds
    And trait "ponytail" appears before trait "structure" in the output

  Scenario: Effective JSON carries per-trait tier provenance
    Given a self-governed repo whose store tier applies "ponytail" and whose repo tier applies "structure"
    When I run "zpp trait effective --json" against that repo
    Then the effective JSON attributes "ponytail" to tier "store" and "structure" to tier "repo"
