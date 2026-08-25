@workflow-auditing
Feature: Audit complete workflows through disposable changes
  Maintainers can drive one synthetic OpenSpec change at a time from a reusable
  mock base, close its feedback, and only then advance without contaminating live state.

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Bootstrap one reusable mock project","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Clone a reusable mock base for one workflow"}
  Scenario: Clone a reusable mock base for one workflow
    Given one reusable mock base project
    When the coordinator assigns the next workflow
    Then one fresh clone has exact Git and OpenSpec identities
    And the base was initialized only once

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Run and review one workflow at a time","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Complete one workflow before assigning the next"}
  Scenario: Complete one workflow before assigning the next
    Given one reusable mock base project
    When one synthetic change follows its complete workflow sequence
    Then every declared stage and required branch is observed
    And its result and contamination status are checked before another assignment

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Reconcile gaps against design and implementation","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Track and classify gaps through sequence closeout"}
  Scenario: Track and classify gaps through sequence closeout
    Given one reusable mock base project
    When one synthetic sequence encounters fixture gaps
    Then every initial failure remains in a typed gap ledger
    And fixture repairs are distinguished from unresolved source gaps

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Close feedback before advancing","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Re-enter full phases before advancing"}
  Scenario: Re-enter full phases before advancing
    Given one completed workflow result with accepted feedback
    When the coordinator re-enters the full phases and reruns it
    Then the same workflow uses a fresh clone and product home
    And no later workflow is assigned before its feedback closes
