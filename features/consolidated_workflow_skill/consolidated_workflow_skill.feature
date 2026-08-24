@consolidated-workflow-skill
Feature: Load the packaged ZPP workflow family
  The package exposes one deterministic validated family while lifecycle conduct
  remains specification authority rather than asserted prose.

  Background:
    Given the packaged workflow family is available

  # zpp-spec: {"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Bounded workflow phase skills","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Load entries kernel and stages in lifecycle order"}
  Scenario: Load entries kernel and stages in lifecycle order
    When the current workflow family is loaded
    Then the six entries precede the kernel and seven stages
    And every packaged workflow member is valid for every supported agent

  # zpp-spec: {"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Complete bounded OpenSpec adapter set","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Cover operational OpenSpec workflows without onboarding"}
  Scenario: Cover operational OpenSpec workflows without onboarding
    When the OpenSpec operation coverage is inspected
    Then the eleven exact adapters are packaged in deterministic order
    And onboarding and broad operation aliases are absent
    And repository verification is one separate final family member

  # zpp-spec: {"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Skill-owned invariant policy","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Load only contextual trait specialization"}
  Scenario: Load only contextual trait specialization
    When the packaged trait collection is decoded
    Then only the five contextual trait families remain
    And BDD execution retains its five repository-selected modes

  # zpp-spec: {"root":"repo:openspec","capability":"consolidated-workflow-skill","requirement":"Ready installed workflow operation set","feature":"features/consolidated_workflow_skill/consolidated_workflow_skill.feature","scenario":"Preserve one deterministic public inventory"}
  Scenario: Preserve one deterministic public inventory
    When the current workflow family is loaded
    Then the six workflow entries have the canonical entry order
    And the workflow family has the exact canonical identity sequence
