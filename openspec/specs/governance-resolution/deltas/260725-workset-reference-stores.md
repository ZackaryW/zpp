## ADDED Requirements

### Requirement: Resolution reports assigned reference stores
Resolution SHALL report the containing workset's assigned reference stores by
id and root, distinctly from the governing store, so that a listed reference
store can never be read as the governing authority. Reference store
assignments SHALL NOT affect mode, rule selection, store binding, effective
root, governance branch, isolation state, or lease keying. When a workset has
no assignments, or the path belongs to no workset, resolution SHALL report an
empty set rather than omitting the distinction.

#### Scenario: Reference stores reported beside the governing store
- **WHEN** resolution runs for a member of a workset with one assigned
  reference store
- **THEN** the result names the governing store as it always did and reports
  the assigned reference store separately with its id and root

#### Scenario: Assignment does not alter resolution
- **WHEN** the same directory is resolved before and after a reference store
  is assigned
- **THEN** mode, rule, store binding, effective root, and isolation state are
  identical in both results

#### Scenario: No assignments
- **WHEN** resolution runs for a workset with no assigned reference stores
- **THEN** the reported reference-store set is empty rather than absent
