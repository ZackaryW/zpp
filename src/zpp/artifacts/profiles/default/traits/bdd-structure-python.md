---
name: bdd-structure-python
description: Keep Python BDD suites capability-cohesive and independently executable.
order: null
config: {}
skill_lookup: []
---
Preserve the repository's established Python BDD runner. Organize features into
stable capability-owned execution roots, keep decorated step bindings small and
local to the roots that load them, and move reusable fixtures and mechanics into
explicit non-step support. Bind through the public system and enforce the layout
with a fast structural check. Do not activate or install a runner implicitly.
