# local-layer-initialization Specification

## Purpose

Defines explicit repository and subfolder ZPP layer creation while keeping all project-local state discoverable through Git ancestry.

## Requirements

### Requirement: Git-scoped local initialization
`zpp local init` SHALL initialize one neutral authored `.zpp` layer at an existing directory inside a Git worktree. The target SHALL default to the current directory and MAY identify the worktree root or any nested directory. ZPP SHALL NOT create a derived cache during local initialization.

Missing targets, file targets, directories outside Git worktrees, and targets outside the worktree reported by Git SHALL be rejected as domain errors without surrounding filesystem changes.

#### Scenario: Initialize root and nested local layers
- **WHEN** local initialization targets existing Git-worktree directories
- **THEN** each target receives exactly one neutral authored ZPP layer without derived cache state and no other directory is modified

#### Scenario: Reject an undiscoverable local target
- **WHEN** local initialization targets a missing path, a file, or a directory outside a Git worktree
- **THEN** it fails with the target identified and leaves surrounding state unchanged

### Requirement: Safe local reinitialization
Local initialization SHALL preserve valid existing authored bytes, fill only missing required entries, and be idempotent. It SHALL validate existing managed sources before writing, and invalid managed local state SHALL reject the operation without partial changes.

#### Scenario: Complete valid partial local state
- **WHEN** local initialization encounters a valid authored layer with required entries missing
- **THEN** only the missing entries are created and repeated initialization makes no further change

#### Scenario: Reject invalid partial local state
- **WHEN** local initialization encounters an invalid managed source and another required entry is missing
- **THEN** it fails with the invalid source identified and leaves the complete worktree unchanged
