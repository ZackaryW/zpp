Feature: Manage named profiles and saved override layers
  ZPP users can manage reusable user-level layers without coupling saved overrides
  to named-profile activation.

  Background:
    Given a valid initialized ZPP user state

  Scenario: Create, list, and idempotently preserve named profiles
    Given a valid profile named "alpha" with distinctive authored bytes
    And no profile named "beta" exists
    When the user runs zpp profile create alpha
    And the user runs zpp profile create beta
    Then both profile creations succeed
    And the authored bytes of profile "alpha" are unchanged
    And profile "beta" contains one neutral authored ZPP layer
    And neither profile has a derived cache
    When the user runs zpp profile list
    Then the command succeeds with stdout:
      """
      alpha
      beta
      default
      """

  Scenario Outline: Reject invalid profile creation without partial writes
    Given <precondition>
    And the complete ZPP user state is recorded
    When the user runs <command>
    Then the command is rejected with exit code 1
    And the diagnostic identifies <source>
    And the complete ZPP user state is unchanged

    Examples:
      | precondition                                                               | command                           | source                       |
      | no profile named "Invalid" exists                                         | zpp profile create Invalid        | the invalid profile name     |
      | profile "broken" has invalid managed state and a required artifact absent | zpp profile create broken         | the invalid managed source   |

  Scenario: Remove a named profile only after confirmation
    Given profiles "work" and "keep" and their independent caches exist
    And ZPP_PROFILE is "work"
    When the user runs zpp profile remove work and declines confirmation
    Then profile "work" and its cache remain unchanged
    When the user runs zpp profile remove work -y
    Then the command succeeds
    And profile "work" and its independent cache no longer exist
    And profile "keep" and its independent cache are unchanged
    And ZPP_PROFILE remains "work"
    When the user runs zpp profile list
    Then the command succeeds with stdout:
      """
      default
      keep
      """

  Scenario: The persistent default is the only initial profile
    When the user runs zpp profile list
    Then the command succeeds with stdout:
      """
      default
      """
    When the user runs zpp profile saved list
    Then the command succeeds with empty stdout

  Scenario: The default profile cannot be removed
    Given the complete ZPP user state is recorded
    When the user runs zpp profile remove default -y
    Then the command is rejected with exit code 1
    And the diagnostic identifies the persistent default profile
    And the complete ZPP user state is unchanged

  Scenario: Copy a profile without activating it or copying derived state
    Given profile "source" has distinctive valid authored bytes and an independent cache
    And no profile named "derived" exists
    And the global layer has distinctive authored bytes
    When the user runs zpp profile copy source derived
    Then profile "derived" contains a byte-for-byte copy of the authored source layer
    And profile "derived" has no derived cache
    And profile "source" and its independent cache are unchanged
    And the global layer is unchanged

  Scenario Outline: Reject an invalid profile copy atomically
    Given <precondition>
    And the complete ZPP user state is recorded
    When the user runs <command>
    Then the command is rejected with exit code 1
    And the diagnostic identifies <source>
    And the complete ZPP user state is unchanged

    Examples:
      | precondition                                     | command                                  | source                     |
      | no profile named "missing" exists               | zpp profile copy missing derived         | the missing source profile |
      | profiles "source" and "existing" already exist  | zpp profile copy source existing         | the existing destination   |
      | profile "broken" has invalid managed state       | zpp profile copy broken derived           | the invalid managed source |

  Scenario: Activate a profile while preserving both configurations
    Given the current timestamp for archive naming is 20260730-143522
    And the global layer has distinctive valid authored bytes and derived state
    And the default profile has different distinctive valid authored bytes and derived state
    When the user runs zpp global activate default
    Then profile "20260730-143522-global" contains the prior global authored layer
    And the global layer contains a byte-for-byte copy of the default authored layer
    And the default profile is byte-for-byte unchanged
    And no derived cache or modification sidecar is copied into either authored layer
    And affected derived caches are invalidated
    When the user resolves traits without ZPP_PROFILE
    Then the platform-neutral base traits resolve from global

  Scenario: Persistent activation does not alter a temporary profile selection
    Given ZPP_PROFILE is "work"
    And profiles "work" and "default" exist
    When the user runs zpp global activate default
    Then ZPP_PROFILE remains "work"
    And the default profile still exists unchanged

  Scenario Outline: Reject invalid global activation atomically
    Given <precondition>
    And the complete ZPP user state is recorded
    When the user runs zpp global activate <profile>
    Then the command is rejected with exit code 1
    And the diagnostic identifies <source>
    And the complete ZPP user state is unchanged

    Examples:
      | precondition                               | profile | source                     |
      | no profile named "missing" exists         | missing | the missing source profile |
      | profile "broken" has invalid managed state | broken | the invalid managed source |

  Scenario: Create a neutral saved layer independently of named profiles
    Given "C:\work\b" is an existing directory and no saved layer named "shared" exists
    When the user runs zpp profile saved create shared "C:\work\b"
    Then the saved creation succeeds
    And one authored layer exists at ~/.zpp/saved/shared
    And no saved layer named "shared" exists under ~/.zpp/profiles
    And saved layer "shared" is one neutral authored ZPP layer
    And no independent cache exists for saved layer "shared"
    When the user runs zpp profile saved list
    Then the command succeeds with these saved bindings in canonical-target order:
      | name   | target    |
      | shared | C:\work\b |

  Scenario: Canonical-equivalent bindings reuse authored saved-layer bytes
    Given an existing saved layer named "shared" with distinctive authored bytes bound to "C:\work\b"
    And "C:\work\a" is an existing directory
    And "c:/WORK/B" identifies the same Windows target as "C:\work\b"
    When the user runs zpp profile saved create shared "C:\work\a"
    And the user repeats zpp profile saved create shared "c:/WORK/B"
    Then both saved creations succeed
    And the authored bytes of saved layer "shared" are unchanged
    And the saved index maps exactly both canonical absolute targets to "shared"
    When the user runs zpp profile saved list
    Then the command succeeds with these saved bindings in canonical-target order:
      | name   | target    |
      | shared | C:\work\a |
      | shared | C:\work\b |

  Scenario: Reject rebinding a saved target to another name
    Given "C:\work\a" is canonically bound to saved layer "shared"
    And no saved layer named "other" exists
    And the complete ZPP user state is recorded
    When the user runs zpp profile saved create other "C:\work\a"
    Then the command is rejected with exit code 1
    And the diagnostic identifies "C:\work\a"
    And the complete ZPP user state is unchanged

  Scenario Outline: Reject invalid saved creation without partial writes
    Given <precondition>
    And the complete ZPP user state is recorded
    When the user runs <command>
    Then the command is rejected with exit code 1
    And the diagnostic identifies <source>
    And the complete ZPP user state is unchanged

    Examples:
      | precondition                                                                            | command                                                    | source                       |
      | "C:\work\a" is an existing directory and no saved layer named "Invalid" exists       | zpp profile saved create Invalid "C:\work\a"             | the invalid saved name       |
      | "C:\missing" does not exist and no saved layer named "new" exists                     | zpp profile saved create new "C:\missing"                 | "C:\missing"                |
      | "C:\work\file.txt" is an existing file and no saved layer named "new" exists         | zpp profile saved create new "C:\work\file.txt"           | "C:\work\file.txt"          |
      | saved layer "broken" has invalid managed state and "C:\work\a" is an existing directory | zpp profile saved create broken "C:\work\a"            | the invalid managed source   |

  Scenario: Remove every binding and only the state owned by one saved name
    Given saved layer "shared" has two target bindings and an independent cache
    And saved layer "keep" has the canonical target binding "C:\work\keep" and an independent cache
    When the user runs zpp profile saved remove shared and declines confirmation
    Then saved layer "shared", its bindings, and its cache remain unchanged
    When the user runs zpp profile saved remove shared --yes
    Then the command succeeds
    And every binding for "shared" is absent from the saved index
    And saved layer "shared" and its independent cache no longer exist
    And saved layer "keep", its binding, and its independent cache are unchanged
    When the user runs zpp profile saved list
    Then the command succeeds with these saved bindings in canonical-target order:
      | name | target       |
      | keep | C:\work\keep |
