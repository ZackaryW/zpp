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
When mode is automatic, or the user delegates a change end to end, continue
across satisfied workflow stages without requesting approval at checkpoints,
successful verification, or ordinary handoffs. Pause only for unresolved
clarification, a new product boundary, or a missing or changed utility shape.
Skill lookup remains passive and grants no authority or failed-gate bypass.
