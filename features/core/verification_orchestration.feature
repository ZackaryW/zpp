Feature: Run repository-owned affected verification
  ZPP users can execute a committed verification command against only its
  deterministically affected targets while retaining a conservative complete path.

  Scenario: Initialize and preserve a behavior mapping without inventing commands
    Given the current directory is a Git worktree root without zpp.behave.yaml
    And Nx is unavailable
    When the user runs zpp behave init twice
    Then the first invocation creates a valid empty committed behavior mapping
    And both invocations report that Nx is unavailable without failing
    And the second invocation preserves the mapping byte-for-byte

  Scenario: Reject an invalid or unknown command before execution
    Given the repository behavior mapping is invalid or does not declare command "bdd"
    And every possible process invocation is recorded
    When the user runs zpp behave bdd
    Then verification fails as a domain error identifying command "bdd" or the invalid mapping
    And no configured process is started

  Scenario: Select the deterministic affected target subset
    Given command "bdd" declares three ordered targets and their repository impact globs
    And tracked, staged, unstaged, and untracked local changes map conclusively to the first and third targets
    When the user runs zpp behave bdd
    Then only the first and third declared target values are submitted in mapping order
    And no changed path or target value becomes executable command syntax

  Scenario: Compare explicit revisions
    Given command "bdd" declares mapped verification targets
    And the exact requested base and head revisions differ only in paths mapped to one target
    When the user runs zpp behave bdd with that base and head
    Then only that declared target is submitted
    And the working tree does not change the revision comparison

  Scenario: Unknown impact falls back to every target
    Given command "bdd" declares multiple verification targets
    And at least one changed repository path matches no declared impact glob
    When the user runs zpp behave bdd
    Then every target declared by command "bdd" is submitted in mapping order

  Scenario: A clean mapped change is a successful no-op
    Given command "bdd" declares valid verification targets
    And the repository has no local change relative to HEAD
    When the user runs zpp behave bdd
    Then verification succeeds and reports that no targets are affected
    And no configured process is started

  Scenario: Explicit complete selection preserves provider cache policy
    Given command "bdd" declares multiple verification targets and a cache-capable provider
    And command "bdd-audit" separately declares repository-owned uncached provider arguments
    When the user runs zpp behave bdd --all
    Then every target declared by command "bdd" is submitted
    And ZPP does not add an uncached flag to command "bdd"
    When the user runs zpp behave bdd-audit --all
    Then only the explicitly declared audit provider arguments control uncached behavior

  Scenario: Expand provider-neutral targets without a shell
    Given command "bdd" declares a typed argv provider with exactly one target expansion position
    And an affected target value contains shell metacharacters
    When the user runs zpp behave bdd
    Then each selected target is passed as one distinct argv value at that position
    And no shell evaluates the executable, arguments, changed paths, or target values

  Scenario: Use only an existing repository-owned Nx surface
    Given command "bdd" selects Nx projects and target "bdd"
    And both a compatible repository-local Nx wrapper and a PATH Nx executable are available
    And a repository-owned plugin exposes every declared project and target
    When the user runs zpp behave bdd --all
    Then ZPP prefers the repository-local Nx wrapper
    And ZPP validates and invokes only the declared project and target surface
    And ZPP does not install, migrate, download, connect, or interpret Nx or its plugins

  Scenario: Do not switch providers when configured Nx is unavailable
    Given command "bdd" selects Nx
    And no compatible Nx executable or declared workspace surface is available
    And another provider-neutral command could run in the repository
    When the user runs zpp behave bdd
    Then verification fails identifying the unavailable Nx requirement
    And no package runner, alternate provider, or configured process is started
