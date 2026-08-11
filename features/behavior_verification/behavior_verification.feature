@behavior-verification
Feature: Run repository-owned affected verification through ZPP
  A repository declares its verification surface once while ZPP selects only
  validated targets and delegates execution through an explicit provider.

  Scenario: Initialize the dedicated behavior mapping without a space
    Given an unregistered Git worktree has no zpp.behave.yaml
    When a user runs zpp behave init from within that worktree
    Then ZPP initializes a root version-one YAML mapping with empty commands through zpp.behave
    And it reports provider diagnostics without creating OpenLease topology or a space

  Scenario: Preserve an existing version-one mapping
    Given a repository has a valid authored version-one zpp.behave.yaml
    When a user runs zpp behave init
    Then ZPP validates the dedicated root mapping without wrapping or rewriting it
    And provider discovery changes only the reported machine-local diagnostics

  Scenario: Reject an invalid mapping before execution
    Given a behavior mapping contains an unsafe path duplicate target value invalid gate or unknown field
    When a user selects one of its commands
    Then ZPP rejects the complete mapping before starting a configured process
    And no legacy behavior implementation runs as fallback

  Scenario: Run only conclusively affected targets
    Given a command declares several ordered targets with repository path rules
    And every changed path maps conclusively to a proper subset
    When a user runs that command without a selection override
    Then ZPP submits only the affected declared target values in declaration order

  Scenario: Broaden uncertain impact to every target
    Given a command declares several verification targets
    And at least one changed path is invalid unmapped or uncertain
    When ZPP performs default affected selection
    Then every target declared by the selected command is submitted

  Scenario: Complete without provider execution when no target is affected
    Given a valid command and mapping are selected
    And repository evidence contains no changed path
    When ZPP performs default affected selection
    Then it reports that no target is affected
    And it starts no provider process

  Scenario: Apply one explicit selection mode
    Given a command declares ordered targets and a valid command-local gate
    When a user selects exact targets a gate all targets or a paired revision range
    Then ZPP applies only that requested selection mode
    And repeated exact targets are submitted once in declaration order

  Scenario: Reject ambiguous or incomplete selection
    Given a valid behavior command is available
    When a user combines selection modes or supplies only one revision endpoint
    Then ZPP rejects the invocation before process creation
    And it does not fall back to affected or complete execution

  Scenario Outline: Delegate through an explicitly configured provider
    Given a command selects the valid <provider> provider and its required surface is available
    When ZPP submits the selected declared target values
    Then the <provider> adapter constructs one validated shell-free argument sequence
    And ZPP does not infer install download or select another provider

    Examples:
      | provider |
      | argv     |
      | nx       |
      | go-task  |

  Scenario: Leave registered behavior callbacks inactive
    Given zpp.behave registers its supported reconciliation callbacks
    And a repository contains zpp.behave.yaml
    When reconciliation selects no behavior callback
    Then no behavior command is invoked

  Scenario Outline: Run one explicitly selected behavior callback
    Given reconciliation explicitly selects a valid zpp.behave <event> callback in <mode> mode
    And the selection names its behavior command selection mode and target context
    When OpenLease invokes the callback against the real reconciliation context
    Then ZPP resolves the exact target repository mapping and returns the configured outcome

    Examples:
      | event                       | mode    |
      | reconcile before repository | gate    |
      | reconcile before repository | observe |
      | reconcile after repository  | observe |
      | reconcile after cohort      | observe |

  Scenario: Reject incomplete callback policy
    Given reconciliation selects a behavior callback
    When its command selection mode event mode or required target context is absent
    Then OpenLease rejects the callback plan instead of guessing repository policy
