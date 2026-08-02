## Purpose

Defines deterministic selection, composition, ordering, and Markdown emission of effective traits for an existing target directory.

## ADDED Requirements

### Requirement: Resolution target and output channel
`zpp resolve` SHALL resolve an existing directory target and SHALL default to the current directory when no target is supplied. Missing targets and file targets SHALL fail as domain errors.

Successful resolution SHALL emit complete effective trait documents as UTF-8 Markdown on stdout. No active traits SHALL succeed with empty stdout. ZPP SHALL NOT expose public JSON, provenance, layer diagnostics, or cache introspection through resolution.

#### Scenario: Resolve a valid target
- **WHEN** a user resolves an existing directory with zero or more active traits
- **THEN** stdout contains the complete ordered effective Markdown documents or is empty when none activate, with no internal metadata

#### Scenario: Reject an invalid target
- **WHEN** a user resolves a missing path or a file
- **THEN** resolution fails with the target identified and emits no fallback output

### Requirement: Participating layer precedence
Resolution SHALL compose participating layers in this order: global, the optional profile named exclusively by `ZPP_PROFILE`, the closest matching saved override, and repository `.zpp` layers from the Git worktree root toward the target.

Unset `ZPP_PROFILE` SHALL mean global-only profile selection. An unknown named profile SHALL fail resolution. Saved overrides SHALL remain eligible outside Git worktrees, only the longest matching canonical ancestor SHALL participate, and a binding whose saved layer is missing SHALL fail resolution. Repository and subfolder layers SHALL not be required outside Git.

#### Scenario: Resolve every participating layer class
- **WHEN** a target has global, active-profile, multiple matching saved, repository-root, and nested layer context
- **THEN** the active profile follows global, only the closest saved override participates, and repository layers participate root-to-target

#### Scenario: Resolve saved state outside Git
- **WHEN** a target outside every Git worktree descends from a valid saved binding
- **THEN** global and that closest saved layer resolve without any repository layer

#### Scenario: Reject an invalid selected layer
- **WHEN** `ZPP_PROFILE` names an unknown profile or a selected saved binding has no authored layer
- **THEN** resolution fails with the missing selection identified and emits no fallback output

### Requirement: Trait activation
`trait.json` SHALL be the exclusive activation owner. Each rule MUST name one trait and MAY be conditionless or contain exactly one fixed `which` or `workspace_contain` condition. A conditionless rule SHALL activate whenever its layer participates. `which` SHALL match an available executable. `workspace_contain` SHALL match any accepted root-relative path pattern beneath the target.

Workspace matching SHALL exclude Git metadata, ZPP derived-cache directories, and directory symlinks. First activation SHALL determine activation position, and later duplicate matches SHALL NOT activate a trait more than once. Authored or configured traits without a matching activation rule SHALL remain inactive.

#### Scenario: Activate fixed trigger forms
- **WHEN** participating rules are conditionless or match an available executable or included workspace path
- **THEN** each matching trait activates once in first-activation order while unavailable and excluded-only matches remain inactive

### Requirement: Trigger-list composition
Layer trigger lists SHALL extend accumulated activation rules by default. A participating layer with `trait_overwrites` enabled SHALL clear the accumulated trigger list before its own optional rules and later extensions are applied. The replacement boundary SHALL apply even when that layer has no `trait.json` file.

#### Scenario: Replace inherited triggers
- **WHEN** a later participating layer enables trigger replacement and a subsequent layer extends with new rules
- **THEN** inherited activation is discarded and only rules after the replacement boundary can activate traits

### Requirement: Effective document and configuration composition
When multiple participating layers author the same trait name, the latest definition SHALL replace the complete earlier document rather than merge its fields. After selecting each winning document, `traitsConfig` mappings SHALL apply shallow top-level configuration overlays in layer order.

`traitsConfig` SHALL NOT activate a trait, override frontmatter fields such as `order`, or recursively merge nested values. A configured name unavailable from every participating authored index SHALL fail resolution.

#### Scenario: Compose a winning effective trait
- **WHEN** participating layers replace one trait document and apply successive configuration overlays
- **THEN** the latest complete document wins, distinct top-level configuration keys accumulate, and each later nested value replaces the earlier nested value

### Requirement: Effective trait ordering
After activation, document replacement, and configuration overlay, traits with an explicit authored `order` SHALL appear first in ascending numeric order. Equal explicit values SHALL retain first-activation order. Traits without an explicit order SHALL follow in first-activation order.

Replacing a document SHALL replace its order, including removal of an earlier order. A configuration key named `order` SHALL remain ordinary trait configuration and SHALL NOT affect presentation order.

#### Scenario: Order replaced and unordered traits
- **WHEN** active traits contain tied explicit orders, unordered documents, duplicate activation, document replacement, and a configuration key named `order`
- **THEN** explicit traits appear first with stable ties and unordered traits follow in first-activation order using only the winning authored orders

### Requirement: Complete effective Markdown
Every emitted trait SHALL use the native Markdown/YAML envelope with `name`, `description`, effective `order`, effective shallow `config`, ordered `skill_lookup`, and the winning advisory body. Unicode content and authored body whitespace SHALL be preserved in effective output.

Any invalid participating source, unavailable activated definition, invalid configured reference, or invalid resolution context SHALL fail the complete resolution with empty stdout and a source-oriented diagnostic without a stack trace. ZPP SHALL NOT return stale, partial, or fallback trait output.

#### Scenario: Emit one complete effective document
- **WHEN** an activated trait has all accepted metadata, Unicode advisory content, deliberate body whitespace, and a valid configuration overlay
- **THEN** stdout contains one complete native document with semantic effective frontmatter and the exact winning body

#### Scenario: Reject invalid participating state
- **WHEN** any participating source or required effective reference is invalid
- **THEN** resolution fails completely, identifies the relevant context or sources, and emits no stale, partial, or fallback output
