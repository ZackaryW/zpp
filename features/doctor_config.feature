Feature: Configurable doctor and bootstrap via the [doctor] config section
  [doctor] rides the standard config tiers, path-aware. exclude binds doctor
  and bootstrap equally; [[doctor.more]] adds detect-only tools whose
  successnote is usage guidance shown when the tool is present.

  Scenario: Excluded tool is neither checked nor installed
    Given a self-governed repo whose zpp.toml sets doctor exclude to "codegraph"
    And PATH is emptied so every tool is missing
    When I run "zpp doctor" against that repo
    Then the command fails
    And the output does not contain "codegraph"
    When I run "zpp bootstrap --dry-run" against that repo
    Then the output does not contain "codegraph"

  Scenario: Store tier and repo tier union their doctor entries
    Given a self-governed repo whose store tier adds doctor tool "git" and whose repo tier adds doctor tool "jq"
    When I run "zpp doctor" against that repo
    Then the output contains "git"
    And the output contains "jq"

  Scenario: Degraded resolution keeps doctor alive
    Given a repo with an invalid zpp.toml
    When I run "zpp doctor" against that repo
    Then the output contains "builtin table"
    And the output contains "openspec"

  Scenario: Present more-tool shows its usage note
    Given a self-governed repo whose repo tier adds doctor tool "git" with note "commits follow the zmem grammar"
    When I run "zpp doctor" against that repo
    Then the output contains "commits follow the zmem grammar"

  Scenario: Missing more-tool reports plainly and fails
    Given a self-governed repo whose repo tier adds doctor tool "definitely-absent-tool-xyz" with note "never shown"
    When I run "zpp doctor" against that repo
    Then the command fails
    And the output contains "definitely-absent-tool-xyz"
    And the output does not contain "never shown"

  Scenario: Bootstrap ignores more-tools entirely
    Given a self-governed repo whose repo tier adds doctor tool "definitely-absent-tool-xyz" with note "never shown"
    When I run "zpp bootstrap --dry-run" against that repo
    Then the command succeeds
    And the output does not contain "definitely-absent-tool-xyz"
