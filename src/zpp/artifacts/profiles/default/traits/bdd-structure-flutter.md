---
name: bdd-structure-flutter
description: Keep Flutter behavior tests capability-cohesive and SDK-native.
order: null
config: {}
skill_lookup: []
---
Preserve Flutter's established `test/` and `integration_test/` layout and the
repository's existing runner. Group behavior by capability, keep bindings or test
drivers thin, and place reusable fixtures in explicit support modules. Do not
require Gherkin or add a third-party BDD package merely because this guidance is
selected.
