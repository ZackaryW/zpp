## ADDED Requirements

### Requirement: Worksets contain at most one dedicated store
A workset SHALL contain zero or one dedicated OpenSpec store member, identified by `.openspec-store/store.yaml`. Ordinary project members MAY contain local `openspec/` roots without counting as dedicated stores. Import and sync SHALL reject a workspace containing more than one dedicated store; doctor SHALL report legacy violations; and governance resolution for an invalid containing workset SHALL fail closed.

#### Scenario: One store plus self-governed projects
- **WHEN** a workspace contains one member with `.openspec-store/store.yaml` and multiple project members with local `openspec/` directories
- **THEN** import accepts the workspace and identifies only the marked store as the dedicated governance member

#### Scenario: Import contains two stores
- **WHEN** a workspace contains two members with `.openspec-store/store.yaml`
- **THEN** import refuses without creating or replacing OpenSpec workset state and names both store members

#### Scenario: Existing sidecar contains two stores
- **WHEN** doctor inspects a previously imported workset containing two dedicated store members
- **THEN** doctor reports the workset as invalid with repair guidance

### Requirement: Workset open provisions an isolated session view
`zpp workset open` SHALL be the automatic mutation boundary for branch isolation. Given a current or explicit project checkout, it SHALL resolve the logical member, create or reuse the effective governance worktree, and open a zpp-owned session view that substitutes the effective project and governance checkout paths without modifying the user-owned `.code-workspace`.

#### Scenario: Alternate clone opens through the same logical workset
- **WHEN** the owner runs workset open from an alternate clone uniquely matching member `project-a`
- **THEN** zpp opens a session view containing that clone and its isolated governance worktree while the imported workspace and base sidecar paths remain unchanged

#### Scenario: Provisioning preflight fails
- **WHEN** branch creation cannot safely proceed because the base ref is missing or the target worktree conflicts
- **THEN** workset open stops before changing OpenSpec or Git state and reports the applicable override
