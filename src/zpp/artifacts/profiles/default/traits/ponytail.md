---
name: ponytail
description: Prefer focused composition with proportionate mature dependencies
order: 300
config:
  useThis: true
skill_lookup: []
---
Keep feature wiring thin by composing small focused utilities. Before building
a utility, compare requirement complexity with the portion of a mature
dependency that would actually be used. Adopt the dependency only when that
coverage is proportionate; avoid large imports for narrow behavior.
