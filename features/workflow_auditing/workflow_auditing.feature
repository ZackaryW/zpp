@workflow-auditing
Feature: Audit complete workflows locally
  Maintainers can inspect every complete workflow through isolated simulations
  and compare its declared design with packaged implementation evidence.

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Discover the complete workflow audit set","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Prepare one assignment per complete workflow"}
  Scenario: Prepare one assignment per complete workflow
    When a maintainer prepares the packaged workflow audit
    Then one distinct audit assignment exists per complete workflow contract
    And every assignment resolves its playbook and component evidence

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Isolate one simulation subagent per workflow","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Exercise every workflow in isolated reminder state"}
  Scenario: Exercise every workflow in isolated reminder state
    Given the packaged workflow audit
    When every workflow reminder is simulated independently
    Then every simulation exercises lifecycle and checklist updates
    And simulation state is unique and confined to disposable product homes

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Compare declared design with implementation evidence","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Classify design and implementation evidence per workflow"}
  Scenario: Classify design and implementation evidence per workflow
    Given the packaged workflow audit
    When workflow design and implementation evidence is compared
    Then every workflow result identifies inspected evidence and typed findings
    And blocked or unexecuted evidence is not reported as passing

  # zpp-spec: {"root":"repo:openspec","capability":"workflow-auditing","requirement":"Review audit results interactively","feature":"features/workflow_auditing/workflow_auditing.feature","scenario":"Rerun one selected workflow without replacing other results"}
  Scenario: Rerun one selected workflow without replacing other results
    Given completed results for every workflow audit assignment
    When a maintainer reruns one selected workflow
    Then the rerun uses a fresh assignment for only that workflow
    And all other workflow results remain available
