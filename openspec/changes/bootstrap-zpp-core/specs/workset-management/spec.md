# workset-management

## ADDED Requirements

### Requirement: Import a .code-workspace as a workset
`zpp workset import <file.code-workspace>` SHALL parse the workspace file (tolerating JSONC), resolve each folder's relative path to an absolute path against the workspace file's own directory, create the corresponding openspec workset via the `openspec workset` CLI, and write a sidecar under `~/.zpp/worksets/<name>.toml` recording the source workspace file path and member metadata keyed by member name. The workset name SHALL satisfy openspec's kebab-case naming rules.

#### Scenario: Successful import
- **WHEN** the user runs `zpp workset import ./pathverse.code-workspace` and no workset of that name exists
- **THEN** an openspec workset is created whose members match the workspace file's folders with absolute paths, and a sidecar exists recording the workspace file's absolute path

#### Scenario: Member folder missing on this machine
- **WHEN** a folder listed in the workspace file does not exist on disk
- **THEN** the import reports the missing member and fails without creating a partial workset, unless the user passes an explicit flag to import the surviving members

#### Scenario: Name collision
- **WHEN** an openspec workset with the derived name already exists
- **THEN** zpp refuses and instructs the user to choose another name or remove the existing workset; it SHALL NOT overwrite openspec-owned state

### Requirement: One-way sync from the workspace file
`zpp workset sync [name]` SHALL re-read the sidecar-recorded `.code-workspace` file and reconcile the openspec workset and sidecar to match its folders. zpp SHALL NOT write to the `.code-workspace` file under any command. Member metadata SHALL follow members across renames when folder `name` labels are present; when a change is indistinguishable from remove+add, sync SHALL present its reconciliation plan before applying metadata-destructive changes.

#### Scenario: Folder added in VSCode
- **WHEN** the user adds a folder to the workspace file and runs `zpp workset sync`
- **THEN** the openspec workset gains the member and the sidecar gains an entry with no bindings

#### Scenario: Labeled folder renamed
- **WHEN** a folder entry with a stable `name` label changes its `path` and the user syncs
- **THEN** the member's sidecar metadata (bindings, role) is preserved under the same name with the updated path

#### Scenario: Unlabeled folder replaced
- **WHEN** an unlabeled folder disappears and a new one appears in the workspace file
- **THEN** sync shows a plan identifying the metadata that would be dropped and requires confirmation before applying

### Requirement: Delegation to openspec workset
Workset composition, opening, listing, and removal SHALL be delegated to the `openspec workset` CLI (using `--json` output where available). zpp SHALL NOT write to any file under openspec's data directory.

#### Scenario: Opening a workset
- **WHEN** the user runs `zpp workset open <name>`
- **THEN** zpp invokes `openspec workset open <name>` and surfaces its outcome unchanged

#### Scenario: Removing a workset through zpp
- **WHEN** the user runs `zpp workset remove <name>`
- **THEN** zpp delegates removal to openspec and deletes the sidecar and its snapshots

### Requirement: Store bindings on members
`zpp workset bind <member> <store-id>` SHALL record, in the sidecar, that the member is governed by the given store, after validating the store id against openspec's store registry. Binding SHALL fail with the list of registered stores when the id is unknown.

#### Scenario: Valid binding
- **WHEN** the user binds member `poc` to registered store `governance-of-agents`
- **THEN** the sidecar records the binding and `zpp workset status` reports it

#### Scenario: Unknown store
- **WHEN** the user binds a member to a store id absent from the registry
- **THEN** the command fails and lists the registered store ids

### Requirement: Workset status and doctor
`zpp workset status` SHALL report, for the current workset context: members, each member's governance mode and bound store, detected roles (a member containing `.openspec-store/store.yaml` is reported as a store), and the source workspace file. `zpp workset doctor` SHALL detect and report: sidecars whose openspec workset no longer exists, openspec worksets lacking sidecars, member paths that do not exist, source workspace files that have moved or disappeared, and bindings referencing unregistered stores.

#### Scenario: Orphaned sidecar
- **WHEN** the user removed a workset via `openspec workset remove` directly and runs `zpp workset doctor`
- **THEN** the orphaned sidecar is reported with a suggested cleanup command

#### Scenario: Store member detection
- **WHEN** a member contains `.openspec-store/store.yaml`
- **THEN** status reports that member's role as a store without requiring a declaration
