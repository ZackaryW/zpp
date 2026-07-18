Feature: Trait content sources and precedence
  Trait content resolves from three sources - user, builtin, saucepan -
  with fixed precedence user > builtin > saucepan. Remote packs can never
  shadow shipped discipline.

  Scenario: User trait shadows a builtin
    Given a user trait "ponytail" with content "USER PONYTAIL OVERRIDE"
    When I run "zpp trait show ponytail"
    Then the command succeeds
    And the output contains "USER PONYTAIL OVERRIDE"
    And trait "ponytail" is listed with source "user"

  Scenario: Remote pack cannot shadow a builtin
    Given a saucepan pack "acme" containing trait "structure" with content "REMOTE STRUCTURE"
    When I run "zpp trait show structure"
    Then the command succeeds
    And the output does not contain "REMOTE STRUCTURE"
    And trait "structure" is listed with source "builtin"
    And the saucepan copy of "structure" is listed as shadowed

  Scenario: Builtin discipline set is present out of the box
    When I run "zpp trait list --json"
    Then the command succeeds
    And traits "ponytail, structure, coverage, commit-stage" are listed with source "builtin"

  Scenario: Unknown applied trait warns and continues
    Given a repo applying traits "structure, ghost"
    When I run "zpp trait effective" against that repo
    Then the command succeeds
    And the output warns about unknown trait "ghost"
    And the output contains the content of builtin trait "structure"
