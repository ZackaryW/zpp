Feature: Remote trait packs via saucepan
  saucepan fetches remote packs. Managed mode (default) self-fetches the
  release binary under ~/.zpp/bin; system mode requires PATH and never
  installs anything.

  Scenario: Managed mode fetches the release binary on first use
    Given a fake saucepan release is served at a file URL
    And a repo applying traits "structure"
    When I run "zpp trait fetch acme-pack" against that repo
    Then the command succeeds
    And the output contains "fetching saucepan"
    And a managed saucepan binary exists under the zpp home

  Scenario: System mode never installs
    Given a repo configured with saucepan mode "system"
    And saucepan is absent from PATH
    When I run "zpp trait fetch acme-pack" against that repo
    Then the command fails
    And the error output contains "saucepan"
    And no managed saucepan binary exists under the zpp home

  Scenario: Remote pack traits are listed with their version
    Given a saucepan pack "acme" at version "1.2.0" containing trait "acme-style"
    When I run "zpp trait list --json"
    Then the command succeeds
    And the listing shows "acme-style" from "saucepan" at version "1.2.0"
