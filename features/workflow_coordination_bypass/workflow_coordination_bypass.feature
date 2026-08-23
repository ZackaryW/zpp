@workflow-coordination-bypass
Feature: Run one explicitly authorized command without Bundler coordination
  ZPP provides a visible one-command escape hatch without turning ordinary
  environment overrides into an unleased mode.

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Scope unleased bypass to one explicit command","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Warn and scope one acknowledged bypass command"}
  @bypass @warning
  Scenario: Warn and scope one acknowledged bypass command
    Given a child command that reports ZPP bypass state
    When the owner runs it through an acknowledged ZPP bypass with a reason
    Then the child reports active bypass
    And the bypass marker is absent from a later ordinary command

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Make bypass execution unmistakable","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Report warned structured bypass state"}
  @bypass @warning @runtime
  Scenario: Report warned structured bypass state
    Given a governed mutation child command
    When the owner runs it through an acknowledged ZPP bypass with a reason
    Then ZPP warns before reporting structured bypass state

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-coordination-bypass","requirement":"Scope unleased bypass to one explicit command","feature":"features/workflow_coordination_bypass/workflow_coordination_bypass.feature","scenario":"Reject bypass without complete authorization"}
  @bypass @authority
  Scenario: Reject bypass without complete authorization
    Given a child command that would leave an execution marker
    When bypass acknowledgement is omitted
    Then ZPP refuses to run the child and identifies the missing acknowledgement
    And the child execution marker remains absent
