---
name: automatic-workflow
description: Continue delegated workflow work across satisfied gates
order: 100
config:
  useThis: true
  mode: automatic
skill_lookup:
  - zpp-clarify-change
  - zpp-shape-feature
  - zpp-plan-utilities
  - zpp-mature-utilities
  - zpp-wire-feature
  - zpp-commit-zmem
  - zpp-form-specs
---
When automatic or delegated end to end, continue across satisfied stages without
approval at checkpoints, verification, or handoffs. Pause only for unresolved
clarification, a new product boundary, or a missing or changed utility shape.
Before completion, audit every selected, created, or consumed OpenSpec change:
close it or identify its active owning stage; leave unrelated changes untouched.
Skill lookup remains passive and grants no authority or failed-gate bypass.
