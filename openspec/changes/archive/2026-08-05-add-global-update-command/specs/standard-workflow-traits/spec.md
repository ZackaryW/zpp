## MODIFIED Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands. Top-level global update and user-global workflow install and update SHALL add packaged standard trait files and trigger entries that are absent from a valid persistent default while preserving every existing same-name file, trigger value, configuration value, and custom trait. Repository-local workflow lifecycle operations and workflow removal SHALL NOT mutate the persistent default. A malformed persistent default SHALL reject global update or a global workflow install or update before any included agent surface changes.

The `default` profile SHALL be provisioned as an inactive reusable preset and SHALL NOT participate in trait resolution merely because it exists, was refreshed, or because `zpp init` or `zpp update` completed. Its trigger configuration SHALL select `automatic-workflow`, `codespace-claim-guard`, `zero-assumptions`, and `ponytail` conditionlessly when the profile explicitly participates. It SHALL select `use-rg`, `use-jq`, and `use-zmem` only through their corresponding executable conditions. Packaged ecosystem workflow and BDD-structure traits SHALL remain inactive until explicitly triggered by a user-owned layer.

Persistent use of the preset in the global layer SHALL require `zpp global activate default`. `ZPP_PROFILE=default` SHALL remain an explicit temporary profile selection and SHALL NOT replace or mutate global authored state.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once or preserved unchanged without participating in trait resolution automatically

#### Scenario: Explicitly select the default profile
- **WHEN** a user explicitly selects `default` through `ZPP_PROFILE` or activates it into global
- **THEN** its conditionless base traits and executable-guarded tool traits participate only through the selected temporary or persistent path while ecosystem traits remain manually selected

#### Scenario: Upgrade the persistent default additively
- **WHEN** top-level global update or a user-global workflow install or update finds a valid persistent default missing newly packaged standard entries
- **THEN** ZPP adds only the missing entries and preserves all existing authored values and content

#### Scenario: Keep local lifecycle independent from the global profile
- **WHEN** a user performs a repository-local workflow lifecycle operation or removes a workflow projection
- **THEN** the persistent default remains byte-for-byte unchanged
