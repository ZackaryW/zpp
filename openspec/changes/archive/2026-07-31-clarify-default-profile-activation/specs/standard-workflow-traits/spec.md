## MODIFIED Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands.

The `default` profile SHALL be provisioned as an inactive reusable preset and SHALL NOT participate in trait resolution merely because it exists or because `zpp init` completed. Its trigger configuration SHALL select `automatic-workflow`, `zero-assumptions`, and `ponytail` when the profile explicitly participates; independently authored `python-bdd`, `python-tdd`, and `python-build` traits SHALL remain inactive until triggered.

Persistent use of the preset in the global layer SHALL require `zpp global activate default`. `ZPP_PROFILE=default` SHALL remain an explicit temporary profile selection and SHALL NOT replace or mutate global authored state.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once or preserved unchanged without participating in trait resolution automatically

#### Scenario: Explicitly select the default profile
- **WHEN** a user explicitly selects `default` through `ZPP_PROFILE` or activates it into global
- **THEN** its base-trait trigger configuration participates only through the selected temporary or persistent path
