@workflow-auditing
Feature: Audit complete workflows through disposable changes
  Maintainers can drive synthetic OpenSpec changes through every complete
  workflow, reconcile gaps, and close each workflow without contaminating live state.

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Create a disposable Git and OpenSpec audit workspace","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Initialize an empty Git and OpenSpec audit repository"}
  Scenario: Initialize an empty Git and OpenSpec audit repository
    When a maintainer prepares disposable workflow audit repositories
    Then one fresh Git and OpenSpec workspace exists per complete workflow
    And every workspace has a unique isolated ZPP product home

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Run one complete mock sequence per workflow","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Close every declared workflow through a mock change"}
  Scenario: Close every declared workflow through a mock change
    Given disposable audit workspaces for every complete workflow
    When every synthetic change follows its complete workflow sequence
    Then every declared stage and required branch is observed
    And every synthetic change is validated archived and reminder-closed

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Reconcile gaps against design and implementation","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Track and classify gaps through sequence closeout"}
  Scenario: Track and classify gaps through sequence closeout
    Given disposable audit workspaces for every complete workflow
    When incomplete mock fixtures are reconciled through closeout
    Then every initial failure remains in a typed gap ledger
    And fixture repairs are distinguished from unresolved source gaps

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Close gaps interactively and rerun","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Resolve one workflow gap and rerun from scratch"}
  Scenario: Resolve one workflow gap and rerun from scratch
    Given completed mock results for every workflow
    When an accepted workflow gap is rerun
    Then the selected workflow uses a fresh Git OpenSpec and product-home workspace
    And all other workflow results and superseded evidence remain available
