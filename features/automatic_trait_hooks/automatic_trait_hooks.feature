@automatic-trait-hooks
Feature: Inject repository traits through agent-native hooks
  Each supported agent receives environment policy automatically while the
  workflow skill remains the sole ZPP workflow authority. Injection semantics
  and failure isolation are canonical requirements of the native hook contract,
  verified by inspection rather than by scenarios.

  Scenario Outline: Package the native hook for each supported agent
    Given ZPP packages the <agent> workflow integration
    When the packaged native hook is inspected
    Then the hook declares the <format> native format
    And the hook is compatible with only that agent
    And the hook resolves the current repository with <agent> as the invoking agent

    Examples:
      | agent  | format  |
      | codex  | json    |
      | claude | json    |
      | kimi   | toml    |
      | pi     | pi-file |

  Scenario: Keep guard and prompt events out of the packaged hook
    Given ZPP packages the codex workflow integration
    When the packaged native hook is inspected
    Then the hook declares no guard and no prompt-submit event

  Scenario: Install the skill and hook together
    Given a disposable project root
    When a user installs the codex workflow integration into that project
    Then Agent Router projects exactly the workflow skill and the native hook

  Scenario: Remove the skill and hook together
    Given a disposable project root
    And the codex workflow integration is installed into that project
    When a user removes that workflow integration
    Then Agent Router removes exactly the workflow skill and the native hook

  Scenario: Resolve traits from a native hook without coordination state
    Given a disposable repository with no Bundler lease state
    When the packaged hook resolution runs against that repository
    Then the repository traits resolve
    And no session or Bundler lease state is created

  Scenario: Package the hard-cut trait hook identity
    Given ZPP packages the codex workflow integration
    When the packaged native hook is inspected
    Then the hook identity is zpp-traits
    And no zpp-session compatibility hook is packaged
