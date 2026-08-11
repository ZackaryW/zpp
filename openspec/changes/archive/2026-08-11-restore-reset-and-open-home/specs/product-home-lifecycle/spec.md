## ADDED Requirements

### Requirement: Selected ZPP home layout
ZPP SHALL treat root `--path` as the selected ZPP home and SHALL default it to `~/.zpp`. Every OpenLease-backed ZPP operation SHALL use the exact `openlease` child of that selected home as its state root. Selecting or resolving a home SHALL NOT by itself create the home or state.

#### Scenario: Use the default ZPP home
- **WHEN** a caller omits root `--path`
- **THEN** ZPP selects `~/.zpp` as its home and supplies `~/.zpp/openlease` to OpenLease-backed operations

#### Scenario: Use an alternate ZPP home
- **WHEN** a caller supplies root `--path` with an eligible custom directory
- **THEN** ZPP treats that exact directory as the ZPP home and supplies only its `openlease` child as managed state

#### Scenario: Avoid eager home mutation
- **WHEN** a caller only requests help, version, or another operation that does not require filesystem state
- **THEN** selecting the ZPP home creates no directory or OpenLease state

### Requirement: Explicit native home opening
Root `zpp open` SHALL create the selected ZPP home when absent and open that exact directory through the host platform's native folder-opening facility without a command shell. It SHALL report the resolved home path. It SHALL NOT open only the OpenLease child, inspect or rewrite home contents, initialize OpenLease state, install agent assets, or execute repository behavior.

#### Scenario: Open an existing default home
- **WHEN** a caller invokes `zpp open` with an existing eligible default home
- **THEN** ZPP launches the native folder opener for `~/.zpp` and reports that path without changing its contents

#### Scenario: Create and open an alternate home
- **WHEN** a caller supplies an eligible absent `--path` and invokes `zpp open`
- **THEN** ZPP creates exactly that home directory, opens it natively, and does not create its `openlease` child

#### Scenario: Report an unavailable native opener
- **WHEN** the selected home is valid but the platform folder opener cannot launch
- **THEN** ZPP reports the launch failure without deleting the explicitly created home or falling back to a shell command

### Requirement: Confirmed complete product reset
Root `zpp reset` SHALL require `--yes` before inspecting or mutating external state. A confirmed reset SHALL target every supported agent's ZPP-owned `zpp-workflow` skill and `zpp-session` hook in user scope, prepare fresh OpenLease state, remove every present preflighted projection through Agent Router, and replace only the selected home's `openlease` child after projection cleanup succeeds. It SHALL NOT expose or accept the former `--overwrite-global-traits` option.

#### Scenario: Reject unconfirmed reset
- **WHEN** a caller invokes `zpp reset` without `--yes`
- **THEN** ZPP rejects the command before inspecting agent projections, preparing state, or changing the filesystem

#### Scenario: Reset complete user integration and state
- **WHEN** a caller confirms reset and every selected projection and state boundary passes preflight
- **THEN** ZPP removes all present ZPP-owned user workflow skills and hooks through Agent Router and replaces the exact OpenLease state child with fresh state

#### Scenario: Omit obsolete global-trait replacement
- **WHEN** a caller inspects reset help or supplies the former overwrite option
- **THEN** ZPP exposes no global-trait overwrite mode and rejects the unsupported option

### Requirement: Complete reset preflight and retry safety
Before any reset mutation, ZPP SHALL inspect the complete supported-agent user-scope skill and hook catalog through Agent Router, validate the selected home and exact state child, and prepare replacement OpenLease state. An absent projection SHALL be eligible and require no removal. Any modified, unmanaged, ambiguous, conflicting, unknown, or failed inspection SHALL abort the complete reset without removing any projection or replacing state.

After successful preflight, ZPP SHALL attempt every preflighted removal in deterministic supported-agent order and SHALL aggregate runtime failures. Any removal failure SHALL leave the prior OpenLease state unchanged. A retry SHALL treat already absent projections as eligible and SHALL converge without adopting or directly deleting native assets.

#### Scenario: Abort on one projection conflict
- **WHEN** any selected user-scope skill or hook is not absent or ownership-safe removable during preflight
- **THEN** reset identifies the agent and asset and changes no selected projection or OpenLease state

#### Scenario: Preserve state after runtime removal failure
- **WHEN** complete preflight succeeds but one Agent Router removal fails
- **THEN** reset attempts the remaining preflighted removals, reports all outcomes, leaves prior OpenLease state unchanged, and does not claim completion

#### Scenario: Retry after partial cleanup
- **WHEN** reset is retried after an earlier runtime failure removed some selected projections
- **THEN** absent projections pass preflight, remaining intact projections are removed through Agent Router, and state replacement occurs only after cleanup succeeds

### Requirement: Reset ownership and destructive-path boundary
Reset SHALL preserve the selected ZPP home itself and every path outside its exact `openlease` child. Repository `.zpp` documents, repository `zpp.behave.yaml`, project-scope projections, plugins, external worktrees, and unrelated user agent assets SHALL remain outside reset authority. Reset SHALL reject a selected home or state child that is broad, symlinked, non-directory where a directory is required, or otherwise cannot be proven safe, and SHALL NOT follow a symlink during preparation or replacement.

#### Scenario: Preserve repository and project assets
- **WHEN** confirmed reset runs while repositories contain traits, behavior mappings, project projections, plugins, or external worktrees
- **THEN** reset changes none of those assets and operates only on the selected user projections and OpenLease state child

#### Scenario: Preserve other ZPP-home contents
- **WHEN** the selected ZPP home contains user-authored files outside `openlease`
- **THEN** reset preserves those files byte-for-byte and never recursively deletes the complete home

#### Scenario: Reject an unsafe reset boundary
- **WHEN** the selected home or `openlease` child is a broad destructive target, unsafe symlink, or incompatible filesystem object
- **THEN** reset fails before projection or state mutation and does not follow or delete the unsafe path
