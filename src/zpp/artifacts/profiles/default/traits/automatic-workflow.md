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
If automatic or delegated end to end, cross satisfied gates without approval.
Pause only for unresolved clarification, a new product boundary, or a missing
or changed utility shape. Canonical OpenSpec owns current accepted behavior;
proposals are working state; zmem preserves decision changes and temporal
highlights, not current truth. Close or assign each related change before
completion; leave unrelated changes untouched. Skill lookup is passive and
grants no authority or failed-gate bypass.
