## MODIFIED Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands. User-global workflow install and update SHALL add packaged standard trait files and trigger entries that are absent from a valid persistent default while preserving every existing same-name file, trigger value, configuration value, and custom trait. Repository-local workflow lifecycle operations and workflow removal SHALL NOT mutate the persistent default. A malformed persistent default SHALL reject a global install or update before any selected agent surface changes.

The `default` profile SHALL be provisioned as an inactive reusable preset and SHALL NOT participate in trait resolution merely because it exists or because `zpp init` completed. Its trigger configuration SHALL select `automatic-workflow`, `codespace-claim-guard`, `zero-assumptions`, and `ponytail` conditionlessly when the profile explicitly participates. It SHALL select `use-rg`, `use-jq`, and `use-zmem` only through their corresponding executable conditions. Packaged ecosystem workflow and BDD-structure traits SHALL remain inactive until explicitly triggered by a user-owned layer.

Persistent use of the preset in the global layer SHALL require `zpp global activate default`. `ZPP_PROFILE=default` SHALL remain an explicit temporary profile selection and SHALL NOT replace or mutate global authored state.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once or preserved unchanged without participating in trait resolution automatically

#### Scenario: Explicitly select the default profile
- **WHEN** a user explicitly selects `default` through `ZPP_PROFILE` or activates it into global
- **THEN** its conditionless base traits and executable-guarded tool traits participate only through the selected temporary or persistent path while ecosystem traits remain manually selected

#### Scenario: Upgrade the persistent default additively
- **WHEN** a user-global workflow install or update finds a valid persistent default missing newly packaged standard entries
- **THEN** ZPP adds only the missing entries and preserves all existing authored values and content

#### Scenario: Keep local lifecycle independent from the global profile
- **WHEN** a user performs a repository-local workflow lifecycle operation or removes a workflow projection
- **THEN** the persistent default remains byte-for-byte unchanged

## ADDED Requirements

### Requirement: Optional ecosystem BDD-structure traits
The packaged standard profile SHALL provide independent, inactive definitions named `bdd-structure-python`, `bdd-structure-ts`, and `bdd-structure-flutter`. A user-owned global, profile, saved, or repository trigger SHALL be required to activate each definition, and selecting one ecosystem's structure guidance SHALL NOT activate another ecosystem's runner or structure policy.

Each structure trait SHALL favor capability-cohesive executable test boundaries, local step or binding ownership where its ecosystem supports it, thin bindings to the public system, and explicit shared support over a globally coupled step-definition module. The guidance SHALL follow the selected ecosystem's established runner and test-layout conventions rather than impose Behave's filesystem shape on every language.

Flutter structure guidance SHALL recognize the Flutter SDK's `test` and `integration_test` conventions and SHALL NOT require Gherkin or a third-party BDD package merely because the trait is available. TypeScript guidance SHALL remain compatible with explicitly configured Cucumber step-loading roots rather than assume every TypeScript project uses Cucumber.

#### Scenario: Select one structure policy
- **WHEN** a participating user-owned layer activates the Python BDD-structure definition only
- **THEN** capability-oriented Python guidance joins the effective traits without TypeScript, Flutter, or runner-selection policy

#### Scenario: Preserve runner choice
- **WHEN** a Flutter or TypeScript repository activates its BDD-structure definition without adopting a third-party Gherkin runner
- **THEN** the guidance preserves that repository's established test runner and does not introduce a new one
