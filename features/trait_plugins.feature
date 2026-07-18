Feature: Agent-surface plugins as a trait source
  Plugins opt in by shipping a traits/ folder. Gathering is live and gated by
  --tool (one surface per invocation). Only traits/*.md are extracted.

  Scenario: Tool flag folds in that surface's plugin traits
    Given a claude plugin "acme" shipping trait "acme-style" with content "ACME PLUGIN STYLE"
    When I run "zpp trait list --tool claude --json"
    Then the command succeeds
    And the listing includes "acme-style" with source "plugin"
    And the plugin trait "acme-style" reports provenance tool "claude" plugin "acme"

  Scenario: No tool flag means no plugin gathering
    Given a claude plugin "acme" shipping trait "acme-style" with content "ACME PLUGIN STYLE"
    When I run "zpp trait list --json"
    Then the command succeeds
    And no trait named "acme-style" is listed

  Scenario: A plugin without a traits folder contributes nothing
    Given a claude plugin "skillsonly" shipping only a skill
    When I run "zpp trait list --tool claude --json"
    Then the command succeeds
    And no trait named "skillsonly-skill" is listed

  Scenario: Only traits are extracted, not skills or manifests
    Given a claude plugin "mixed" shipping trait "good-rule" and also skills and a manifest
    When I run "zpp trait list --tool claude --json"
    Then the command succeeds
    And the listing includes "good-rule" with source "plugin"
    And no trait named "plugin" is listed

  Scenario: Plugin cannot shadow a builtin
    Given a claude plugin "hijack" shipping trait "ponytail" with content "PLUGIN PONYTAIL"
    When I run "zpp trait show ponytail --tool claude"
    Then the command succeeds
    And the output does not contain "PLUGIN PONYTAIL"
    And the plugin copy of "ponytail" is listed as shadowed under tool "claude"

  Scenario: Plugin outranks a remote pack
    Given a saucepan pack "remote" containing trait "shared-x" with content "REMOTE X"
    And a claude plugin "acme" shipping trait "shared-x" with content "PLUGIN X"
    When I run "zpp trait show shared-x --tool claude"
    Then the command succeeds
    And the output contains "PLUGIN X"

  Scenario: Override wins over auto-detection
    Given a claude plugins override directory holding plugin "override-pack" with trait "over-rule"
    When I run "zpp trait list --tool claude --json" against that repo
    Then the command succeeds
    And the listing includes "over-rule" with source "plugin"
