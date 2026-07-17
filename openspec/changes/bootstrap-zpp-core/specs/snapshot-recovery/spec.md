# snapshot-recovery

## ADDED Requirements

### Requirement: Snapshots cover zpp-owned state only
A snapshot SHALL capture the workset's sidecar and the current text of the sidecar-recorded `.code-workspace` file, stored under `~/.zpp/worksets/<name>/snapshots/`. Snapshots SHALL NOT capture member repository contents, git state, or any file outside zpp's own state and the workspace-file copy. Snapshots are machine-local and SHALL never be a sharing or distribution mechanism.

#### Scenario: Snapshot contents
- **WHEN** `zpp snapshot take` runs for a workset
- **THEN** the snapshot contains the sidecar and a copy of the workspace file text, and nothing from member repositories

### Requirement: Auto-snapshot before mutations
Every zpp command that mutates zpp-owned state (`workset import`, `workset sync`, `workset bind`, `workset remove`, config edits) SHALL take a snapshot automatically before applying its changes.

#### Scenario: Bad sync is recoverable
- **WHEN** a sync applies an unwanted reconciliation
- **THEN** a snapshot taken immediately before the sync exists and `zpp snapshot restore` returns the sidecar to its pre-sync state

### Requirement: Restore is scoped and workspace-file-safe
`zpp snapshot restore <id>` SHALL rewrite only zpp-owned files by default. Restoring the workspace-file copy over the user-owned `.code-workspace` SHALL require an explicit flag, since that file is user-owned.

#### Scenario: Default restore
- **WHEN** the user restores a snapshot without flags
- **THEN** the sidecar is restored and the `.code-workspace` file on disk is untouched

#### Scenario: Explicit workspace-file restore
- **WHEN** the user passes the explicit workspace-restore flag
- **THEN** zpp writes the snapshot's workspace-file copy back to the recorded source path, reporting what it overwrote

### Requirement: Snapshot listing
`zpp snapshot list` SHALL list a workset's snapshots with their timestamps and the command that triggered each (manual take or the mutating command's name).

#### Scenario: Provenance visible
- **WHEN** snapshots exist from both manual takes and auto-takes
- **THEN** the listing distinguishes them and names the triggering command for auto-takes
