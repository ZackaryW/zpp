Feature: Session trait override via ZPP_TRAITS
  ZPP_TRAITS replaces the personal (workset) tier for one session only.
  Committed tiers always survive - discipline cannot be shed by an env var.

  Scenario: Env replaces the workset tier only
    Given a workset-bound repo whose workset tier applies "coverage" and whose repo tier applies "structure"
    And the session sets ZPP_TRAITS to "ponytail"
    When I run "zpp trait effective" against that repo
    Then the command succeeds
    And trait "ponytail" appears before trait "structure" in the output
    And the output does not contain "<!-- trait: coverage"

  Scenario: Committed tiers survive an empty env override
    Given a workset-bound repo whose workset tier applies "coverage" and whose repo tier applies "structure"
    And the session sets ZPP_TRAITS to ""
    When I run "zpp trait effective" against that repo
    Then the command succeeds
    And the output contains "<!-- trait: structure"
    And the output does not contain "<!-- trait: coverage"

  Scenario: Provenance names the env tier
    Given a workset-bound repo whose workset tier applies "coverage" and whose repo tier applies "structure"
    And the session sets ZPP_TRAITS to "ponytail"
    When I run "zpp trait effective --json" against that repo
    Then the effective JSON attributes "ponytail" to tier "env" and "structure" to tier "repo"

  Scenario: An env typo warns instead of silently changing the session
    Given a workset-bound repo whose workset tier applies "coverage" and whose repo tier applies "structure"
    And the session sets ZPP_TRAITS to "ponytial"
    When I run "zpp trait effective" against that repo
    Then the command succeeds
    And the output warns about unknown trait "ponytial"
