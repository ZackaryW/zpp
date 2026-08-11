@automatic-trait-hooks
Feature: Inject repository traits through agent-native hooks
  Each supported agent receives environment policy automatically while the workflow
  skill remains the sole ZPP workflow authority.

  Scenario Outline: Package the native hook for each supported agent
    Given ZPP packages the <agent> workflow integration
    When Agent Router inspects its native hook
    Then the hook uses the <event> context injection form
    And it resolves the current repository with <agent> as the invoking agent

    Examples:
      | agent      | event              |
      | codex      | JSON SessionStart  |
      | claude     | JSON SessionStart  |
      | kimi       | TOML SessionStart  |
      | pi         | before_agent_start |

  Scenario: Install the skill and hook together
    Given a user selects a supported agent and integration scope
    When ZPP installs the workflow integration
    Then Agent Router projects one consolidated workflow skill
    And Agent Router projects that agent native trait hook

  Scenario: Remove the skill and hook together
    Given Agent Router owns an intact ZPP workflow skill and native trait hook
    When a user removes that workflow integration
    Then Agent Router removes both assets from the selected scope

  Scenario: Reset every supported user hook through Agent Router
    Given every supported agent user hook is absent or ownership-safe removable
    When a user confirms a complete ZPP reset
    Then Agent Router removes every present selected user hook
    And ZPP does not inspect or change any project hook

  Scenario: Preserve every hook when reset preflight conflicts
    Given one supported agent user hook cannot be inspected or ownership-safe removed
    When a user confirms a complete ZPP reset
    Then reset stops before removing any selected hook
    And OpenLease state remains unchanged

  Scenario: Inject successful prompt-ready trait output
    Given an installed native hook starts in a repository with active traits
    When its public resolver command succeeds
    Then the hook injects the returned complete bodies as advisory environment policy
    And it does not select execute or complete a workflow stage

  Scenario: Isolate a hook resolution failure
    Given an installed native hook starts in a repository
    When its public resolver command fails
    Then the failure remains visible through the native hook contract
    And no partial stale or cached trait body is injected as successful context
