---
name: use-zmem
description: Consult durable temporal history when a decision needs context
order: 320
config:
  useThis: true
skill_lookup:
  - zpp-use-zmem
  - zpp-commit-zmem
---
Use zmem to recall meaningful decision changes, reversals, fallbacks, surprises,
and durable lessons. Verify recalled history against canonical OpenSpec and the
current code. Reading is advisory; write only through the commit-owning skill
when the event is materially worth long-term recall.
