## ADDED Requirements

### Requirement: Reference store assignment
A workset MAY have zero or more **reference stores** assigned to it:
registered OpenSpec stores that serve as read-only knowledge corpora for
tasks rather than as governance authorities. Assignment SHALL be durable and
recorded in the machine-local sidecar (`~/.zpp/worksets/<name>.toml`), and
SHALL NOT require the store to be a member of the workspace. zpp SHALL
provide explicit commands to assign and unassign a reference store by
registered store id, validating the id against openspec's registry read-only
at assignment time and never writing to that registry. An assigned reference
store SHALL contribute no traits, no configuration, no policy, no lease, and
no isolated governance worktree, and SHALL NOT participate in zpp's
read/write governance cycle; its content is reached through openspec's own
`--store <id>` commands. `zpp workset doctor` SHALL report an assigned
reference store whose id is no longer registered or whose root path is
missing, and SHALL NOT report healthy assignments.

#### Scenario: Assigning a reference store
- **WHEN** the owner assigns a registered store id as a reference store of a
  workset
- **THEN** the assignment is recorded in that workset's machine-local sidecar
  and persists across sessions

#### Scenario: Assignment does not require workspace membership
- **WHEN** the assigned store is not a folder in the workset's
  `.code-workspace`
- **THEN** the assignment succeeds and the at-most-one-dedicated-store rule is
  not consulted

#### Scenario: Reference store is not a governance participant
- **WHEN** a workset has an assigned reference store and resolution, config,
  and trait composition run for one of its members
- **THEN** the reference store contributes no traits or configuration, holds
  no lease, and has no governance worktree provisioned

#### Scenario: Assigning an unregistered id
- **WHEN** the owner assigns a store id that openspec's registry does not know
- **THEN** the assignment is refused, naming the unknown id, and the registry
  is not modified

#### Scenario: Assigned store vanishes from the registry
- **WHEN** doctor inspects a workset whose assigned reference store id is no
  longer registered or whose root path no longer exists
- **THEN** doctor reports that assignment as a problem with a fix suggestion

#### Scenario: Healthy assignments are not findings
- **WHEN** doctor inspects a workset whose assigned reference stores are all
  registered with existing roots
- **THEN** doctor reports nothing about them
