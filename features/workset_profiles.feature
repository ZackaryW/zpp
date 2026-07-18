Feature: Workset config profiles
  A workset carries named zpp.toml-shaped profiles. Members resolve to the
  default profile unless they point elsewhere; the repo's own zpp.toml always
  wins. A committed .zpp-workset file beside the .code-workspace shares
  profiles with collaborators, referencing members by name only.

  Scenario: A member resolves to the default profile
    Given a workset "demo" with member "api" and a default profile applying trait "ponytail"
    When I resolve config for member "api"
    Then the effective traits include "ponytail" from tier "workset"

  Scenario: An explicit pointer selects another profile
    Given a workset "demo" with member "web" pointing at profile "webapp" that binds store "gov"
    And the store "gov" is registered
    When I resolve governance for member "web"
    Then the governance mode is "externally-governed" by rule 3 with store "gov"

  Scenario: Repo zpp.toml overrides the profile
    Given a workset "demo" with member "api" and a default profile setting zmem mode "present"
    And member "api" commits a zpp.toml setting zmem mode "apply"
    When I resolve config for member "api"
    Then the effective zmem mode is "apply" from tier "repo"

  Scenario: Committed binding beats a profile binding
    Given a workset "demo" with member "api" whose default profile binds store "gov-b"
    And member "api" commits a zpp.toml binding store "gov-a"
    And the stores "gov-a, gov-b" are registered
    When I resolve governance for member "api"
    Then the governance mode is "externally-governed" by rule 2 with store "gov-a"

  Scenario: Shared .zpp-workset file wins over the sidecar
    Given a workset "demo" with member "api" and a sidecar default profile applying trait "coverage"
    And a shared .zpp-workset file whose default profile applies trait "ponytail"
    When I resolve config for member "api"
    Then the effective traits include "ponytail" from tier "workset"
    And the effective traits do not include "coverage"

  Scenario: Bind command is gone
    When I run "zpp workset bind api gov"
    Then the command fails

  Scenario: A profile can extend another
    Given a workset "demo" with member "api" and a default profile applying trait "ponytail"
    And the shared concept aside, profile "store-dev" extends "default" and binds store "gov"
    And member "api" points at profile "store-dev"
    And the store "gov" is registered
    When I resolve config for member "api"
    Then the effective traits include "ponytail" from tier "workset"
    When I resolve governance for member "api"
    Then the governance mode is "externally-governed" by rule 3 with store "gov"

  Scenario: Doctor flags a shared-file member the workspace lacks
    Given a workset "demo" with member "api" and a sidecar default profile applying trait "coverage"
    And a shared .zpp-workset file naming a member "ghost" with profile "default"
    When I run "zpp workset doctor"
    Then the command fails
    And the output contains "ghost"
