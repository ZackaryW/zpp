Feature: The zpp-governance MCP prompt
  The Claude Desktop chat surface has no session-start hook, so the zpp-mcp
  server exposes a `zpp-governance` prompt that composes the same mount block
  scripts/zpp-mount.sh emits for the hook surfaces: a governance header,
  effective trait content, and - only when resolution degrades - the doctor
  report. Silent degradation: an ungoverned, clean context mounts nothing.

  Scenario: A governed repo mounts its header and traits
    Given a self-governed repo applying trait "ponytail"
    When I request the zpp-governance prompt for it
    Then the prompt output opens a "zpp-governance" block
    And the prompt output contains "governance: self-governed"
    And the prompt output contains the trait "ponytail"
    And the prompt output has no doctor report

  Scenario: An ungoverned clean context mounts nothing
    Given an ungoverned directory with a reachable store registry
    When I request the zpp-governance prompt for it
    Then the prompt output is empty

  Scenario: A degraded environment appends the doctor report
    Given a repo bound to a store with the store registry unavailable
    When I request the zpp-governance prompt for it
    Then the prompt output opens a "zpp-governance" block
    And the prompt output contains "environment degraded - doctor report:"
