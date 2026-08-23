## MODIFIED Requirements

### Requirement: Repository-space-global composition
ZPP SHALL compose each effective trait family from repository documents followed by the selected managed store's `zpp-traits` namespaces in root-to-child order. Later selected-child input SHALL have higher policy precedence. Siblings and stores outside the selected chain SHALL not participate, and there SHALL be no space or global OpenLease source.

#### Scenario: Compose a selected store chain
- **WHEN** repository, parent-store, selected-child, and sibling inputs contribute one family
- **THEN** ZPP composes repository, parent, then selected child and excludes the sibling

### Requirement: Explicit repository overwrite mode
A repository trait document MAY declare `[meta] mode = "repository-overwrite"`. When declared, ZPP SHALL exclude every store contribution to that family before selection. Store attachments SHALL NOT declare repository overwrite mode.

#### Scenario: Exclude store contributions explicitly
- **WHEN** a repository family declares repository overwrite mode while related stores contribute the same family
- **THEN** only the repository document contributes

#### Scenario: Reject overwrite mode in a store attachment
- **WHEN** a store contribution declares repository overwrite mode
- **THEN** ZPP rejects that store contribution
