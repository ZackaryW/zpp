---
name: bdd-structure-ts
description: Keep TypeScript BDD suites capability-cohesive and runner-native.
order: null
config: {}
skill_lookup: []
---
Preserve the repository's established TypeScript test runner. When Cucumber is
already configured, use explicit capability-owned feature and step-loading roots;
otherwise apply the same ownership and shared-support principles through the
runner's native suites. Keep bindings thin and independently executable. Do not
introduce Cucumber or another runner merely because this guidance is selected.
