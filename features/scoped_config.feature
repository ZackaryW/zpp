Feature: Target-scoped zpp configuration
  One governance root can contain language subtrees whose ordinary policy
  applies only to targets beneath the declaring zpp.toml.

  Scenario: Python policy applies only to its subtree
    Given a self-governed monorepo with Rust policy at its root
    And the monorepo has Python policy under "sdk/python"
    When I resolve config for the root, the Python subtree, and sibling "crates/core"
    Then only the Python subtree resolves the Python BDD and TDD stacks

  Scenario: Nested authority is rejected without changing governance
    Given a self-governed monorepo with Rust policy at its root
    And "sdk/python/zpp.toml" declares nested governance and profiles
    When I resolve config for "sdk/python"
    Then scoped resolution fails naming the file and both authority sections
    And governance resolution still reports the monorepo root
