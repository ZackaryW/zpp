Feature: Distribute the permanent ZPP workflow skills
  ZPP users can install and maintain one owned workflow-skill bundle in native
  global or repository-local agent scopes without changing authored ZPP layers.

  Background:
    Given the packaged ZPP workflow bundle contains all seven permanent skills

  Scenario: Install the bundle locally for explicitly selected agents
    Given the current directory is the root of a Git worktree
    And Codex, Pi, and Claude Code have no local ZPP workflow skills
    And the current project has no authored ZPP layer
    When the user runs zpp skill install with agents Codex, Pi, and Claude Code
    Then installation succeeds without offering agent selection
    And one managed bundle is installed in the repository-local shared Codex and Pi skill scope
    And one managed bundle is installed in the repository-local Claude Code skill scope
    And no duplicate Codex or Pi projection is created
    And the current project still has no authored ZPP layer

  Scenario: Install the bundle globally for explicitly selected agents
    Given Codex, Pi, and Claude Code have no global ZPP workflow skills
    When the user runs zpp skill install --global with agents Codex, Pi, and Claude Code
    Then installation succeeds without offering agent selection
    And one managed bundle is installed in the user-global shared Codex and Pi skill scope
    And one managed bundle is installed in the user-global Claude Code skill scope
    And no repository-local skill scope is changed

  Scenario: Install locally into an exact target inside a Git worktree
    Given "C:\work\repo\nested" is an existing directory inside a Git worktree
    And the current directory is outside that worktree
    When the user runs zpp skill install "C:\work\repo\nested" with agent Claude Code
    Then the managed bundle is installed only in that exact directory's local Claude Code skill scope
    And no authored ZPP layer is created or modified

  Scenario Outline: Reject an invalid local target without changes
    Given <target state>
    And every agent skill scope is recorded
    When the user runs zpp skill install <target> with agent Codex
    Then the invocation is rejected as a domain error
    And every agent skill scope is unchanged

    Examples:
      | target state                                      | target          |
      | "C:\missing" does not exist                      | "C:\missing"   |
      | "C:\work\file.txt" is an existing file          | "C:\work\file.txt" |
      | "C:\outside" is an existing directory outside Git | "C:\outside"   |

  Scenario: Global scope rejects a local target
    Given every agent skill scope is recorded
    When the user runs zpp skill install "C:\work\repo" --global with agent Codex
    Then the invocation is rejected as a usage error
    And every agent skill scope is unchanged

  Scenario: Interactive selection configures all selected agents atomically
    Given an interactive terminal is available
    And every supported agent has no ZPP workflow skills
    When the user runs zpp skill install and selects Pi and Claude Code
    Then one selector offers Pi, Codex, and Claude Code
    And the managed bundle is installed in the selected native local scopes
    And Codex receives no independent projection beyond the shared Pi scope

  Scenario: Empty and cancelled interactive selection make no changes
    Given an interactive terminal is available
    And every agent skill scope is recorded
    When the user submits zpp skill install with no checked agent
    Then installation succeeds without changing any agent skill scope
    When the user cancels zpp skill install from the agent selector
    Then installation is cancelled without changing any agent skill scope

  Scenario: Noninteractive invocation requires explicit agents
    Given no interactive terminal is available
    And every agent skill scope is recorded
    When the user runs zpp skill install without an agent option
    Then the invocation is rejected as a usage error
    And every agent skill scope is unchanged

  Scenario: A compatible global bundle suppresses local duplication
    Given Codex has a compatible managed global ZPP workflow bundle
    And Codex has no local ZPP workflow bundle
    When the user runs zpp skill install with agent Codex
    Then installation succeeds and reports that the compatible global bundle is reused
    And no local bundle is installed
    When the user repeats zpp skill install with agent Codex and --force
    Then a compatible managed local bundle is installed
    And both managed scopes are reported without claiming scope precedence

  Scenario: An outdated global bundle does not suppress the current local bundle
    Given Claude Code has an outdated managed global ZPP workflow bundle
    And Claude Code has no local ZPP workflow bundle
    When the user runs zpp skill install with agent Claude Code
    Then the current managed bundle is installed locally
    And the differing managed scope versions are reported without selecting one

  Scenario: Installation is idempotent for an already compatible managed scope
    Given Pi has a compatible managed local ZPP workflow bundle
    And unrelated files surround the managed projection
    When the user runs zpp skill install with agent Pi twice
    Then both installations succeed
    And the managed projection is unchanged
    And the unrelated files are byte-for-byte unchanged

  Scenario: Every selected destination is preflighted before installation
    Given Pi has no local ZPP workflow bundle
    And Claude Code has an unmanaged local conflict at a required skill destination
    When the user runs zpp skill install with agents Pi and Claude Code
    Then installation fails as a managed-state rejection
    And Pi remains unchanged
    And the conflicting Claude Code content is unchanged

  Scenario: Force never overwrites an unmanaged conflict
    Given Codex has an unmanaged local conflict at a required skill destination
    When the user runs zpp skill install with agent Codex and --force
    Then installation fails as a managed-state rejection
    And the conflicting content is unchanged

  Scenario: Update changes only the selected managed scope
    Given Codex has outdated managed global and forced local ZPP workflow bundles
    And Claude Code has an outdated managed global ZPP workflow bundle
    When the user runs zpp skill update --global with agent Codex
    Then only the Codex global managed bundle is updated to the packaged version
    And the forced local Codex bundle is unchanged
    And every Claude Code scope is unchanged
    And the differing Codex scope versions are reported

  Scenario: Update rejects a selected scope that is not ZPP-managed
    Given Claude Code has an unmanaged global skill directory matching a permanent skill name
    And every agent skill scope is recorded
    When the user runs zpp skill update --global with agent Claude Code
    Then update fails as a managed-state rejection
    And every agent skill scope is unchanged

  Scenario: Removal requires confirmation and removes only managed selected state
    Given Pi has a managed local ZPP workflow bundle surrounded by unrelated skills
    And Claude Code has a managed local ZPP workflow bundle
    When the user runs zpp skill remove with agent Pi and declines confirmation
    Then every agent skill scope is unchanged
    When the user runs zpp skill remove with agent Pi and --yes
    Then only the managed shared Codex and Pi projection is removed
    And the unrelated skills are unchanged
    And the Claude Code projection is unchanged

  Scenario: Automatic workflow guidance remains advisory and skill-backed
    Given a participating layer activates a conditionless automatic-workflow trait
    And that trait references the permanent workflow skills through skill lookup
    When the user resolves traits for the target
    Then the effective trait directs unattended continuation only across satisfied gates
    And the skill lookup remains passive frontmatter metadata
    And the trait does not grant mutation authority or bypass a failed gate

  Scenario: Installed skill bodies remain platform-neutral
    When the user installs the managed bundle for every supported agent
    Then every native projection contains the same seven permanent workflow skills
    And each skill retains its required packaged resources and scripts
    And no skill body contains platform, framework, test-runner, or agent-specific policy
    And platform-specific installation behavior remains outside the skill bodies
