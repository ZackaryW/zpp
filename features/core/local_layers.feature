Feature: Initialize repository and subfolder ZPP layers
  ZPP users can create neutral authored layers inside a Git worktree without
  creating derived cache state.

  Scenario: Initialize the current repository root and an explicit nested subfolder
    Given the current working directory is the root of a Git worktree
    And an existing directory "src\nested" is inside that worktree
    And neither target has local ZPP state
    When the user runs zpp local init
    And the user runs zpp local init "src\nested"
    Then both local initializations succeed
    And each target contains one neutral authored ZPP layer
    And neither target contains derived cache state
    And no other directory gains local ZPP state

  Scenario: Reinitialization preserves valid authored content and fills only missing state
    Given an existing Git-worktree directory "src"
    And "src/.zpp" contains valid distinctive trait.json and config.json bytes
    And "src/.zpp/traits" is absent
    When the user runs zpp local init "src"
    And the user repeats zpp local init "src"
    Then both local initializations succeed
    And the distinctive authored bytes are unchanged
    And "src/.zpp/traits" exists as a directory
    And "src/.zpp" contains no derived cache state

  Scenario: Invalid existing local state prevents every write
    Given an existing Git-worktree directory "src"
    And "src/.zpp" contains an invalid managed source
    And another required local-layer artifact is absent
    And the complete worktree state is recorded
    When the user runs zpp local init "src"
    Then the command is rejected with exit code 1
    And the diagnostic identifies the invalid managed source path
    And the complete worktree state is unchanged

  Scenario Outline: Reject a target that cannot own a discoverable local layer
    Given <target state>
    And the complete surrounding state is recorded
    When the user runs zpp local init <target>
    Then the command is rejected with exit code 1
    And the diagnostic identifies <target>
    And the complete surrounding state is unchanged

    Examples:
      | target state                                             | target                 |
      | "C:\missing" does not exist                             | "C:\missing"           |
      | "C:\work\file.txt" is an existing file                 | "C:\work\file.txt"     |
      | "C:\outside" is an existing directory outside Git       | "C:\outside"           |
