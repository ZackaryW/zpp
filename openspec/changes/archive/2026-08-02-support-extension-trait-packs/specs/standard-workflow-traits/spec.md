## ADDED Requirements

### Requirement: Executable-guarded tool-use traits
The packaged standard profile SHALL define focused `use-rg`, `use-jq`, and `use-zmem` advisory traits. Its `trait.json` SHALL select them only with the corresponding single fixed conditions `which: rg`, `which: jq`, and `which: zmem`. An unavailable executable SHALL leave only its corresponding trait inactive and SHALL NOT block trait resolution or workflow execution.

#### Scenario: Resolve available tool guidance
- **WHEN** the selected standard profile participates and `rg` is available while `jq` is unavailable
- **THEN** `use-rg` activates, `use-jq` remains inactive, and resolution succeeds

#### Scenario: Keep zmem guidance inactive without the executable
- **WHEN** the selected standard profile participates and `zmem` is unavailable
- **THEN** `use-zmem` remains inactive and resolution and unrelated workflow behavior continue

### Requirement: Proportionate dependency guidance
The packaged Ponytail guidance SHALL preserve the upstream ladder's need, reuse, standard-library, native-platform, installed-dependency, and minimum-code ordering. When no earlier rung satisfies a confirmed non-trivial responsibility, ZPP's utility workflow SHALL additionally investigate maintained third-party packages and compare maturity, integration cost, and the proportion of their feature surface required by the accepted need. It SHALL NOT invent a universal percentage threshold.

#### Scenario: Evaluate an external dependency after earlier rungs fail
- **WHEN** a confirmed utility responsibility is not satisfied by reuse, standard library, native behavior, or an installed dependency
- **THEN** utility planning compares mature external packages against focused custom implementation using proportional requirement coverage before settling the dependency choice

### Requirement: Manually selected platform workflow traits
The packaged standard profile SHALL provide inactive definitions named `python-bdd`, `python-tdd`, `python-build`, `python-django-tdd`, `typescript-bdd`, `typescript-tdd`, `flutter-bdd`, and `flutter-tdd`. None SHALL appear in the packaged standard `trait.json`; a user-owned global, profile, saved, or repository trigger SHALL be required to activate one. Language files or globally available framework commands SHALL NOT automatically select a project's BDD, TDD, or build policy.

#### Scenario: Resolve a project without platform selection
- **WHEN** a selected standard profile supplies platform definitions but no participating user-owned layer triggers one
- **THEN** no Python, Django, TypeScript, or Flutter workflow trait activates

#### Scenario: Select platform policy explicitly
- **WHEN** a participating user-owned layer triggers one or more packaged platform workflow traits
- **THEN** only those selected definitions join the effective trait output through ordinary layer semantics

## MODIFIED Requirements

### Requirement: Persistent default profile
ZPP SHALL create the packaged `default` profile beneath the user profiles namespace only when absent. Once created, it SHALL remain user-owned, survive initialization byte-for-byte, and SHALL NOT be removable through profile or workflow lifecycle commands.

The `default` profile SHALL be provisioned as an inactive reusable preset and SHALL NOT participate in trait resolution merely because it exists or because `zpp init` completed. Its trigger configuration SHALL select `automatic-workflow`, `codespace-claim-guard`, `zero-assumptions`, and `ponytail` conditionlessly when the profile explicitly participates. It SHALL select `use-rg`, `use-jq`, and `use-zmem` only through their corresponding executable conditions. The packaged Python, Django, TypeScript, and Flutter workflow traits SHALL remain inactive until explicitly triggered by a user-owned layer.

Persistent use of the preset in the global layer SHALL require `zpp global activate default`. `ZPP_PROFILE=default` SHALL remain an explicit temporary profile selection and SHALL NOT replace or mutate global authored state.

#### Scenario: Initialize the persistent default
- **WHEN** a user initializes ZPP with the default profile absent or already valid
- **THEN** the profile is created once or preserved unchanged without participating in trait resolution automatically

#### Scenario: Explicitly select the default profile
- **WHEN** a user explicitly selects `default` through `ZPP_PROFILE` or activates it into global
- **THEN** its conditionless base traits and executable-guarded tool traits participate only through the selected temporary or persistent path while platform traits remain manually selected
