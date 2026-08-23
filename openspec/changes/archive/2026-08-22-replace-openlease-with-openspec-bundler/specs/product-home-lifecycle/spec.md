## MODIFIED Requirements

### Requirement: Selected ZPP home layout
ZPP SHALL treat root `--path` as the selected ZPP home and default it to `~/.zpp`. Bundler-backed lease operations SHALL use exactly the selected home's `bundler` child as their `LeaseStateRepository` root. Selecting or resolving a home and performing read-only attachment resolution SHALL NOT create the home or state. ZPP SHALL ignore and never migrate, delete, or inspect a sibling `openlease` child.

#### Scenario: Select the default home without creation
- **WHEN** no explicit path is supplied for a read-only operation
- **THEN** ZPP selects `~/.zpp`, derives its `bundler` child, and creates neither path

#### Scenario: Create state on first lease acquisition
- **WHEN** automatic workflow coordination acquires its first Bundler bundle
- **THEN** ZPP creates state only beneath the selected home's exact `bundler` child

### Requirement: Explicit native home opening
Root `zpp open` SHALL create and open the selected ZPP home through the host platform's native folder-opening facility without a command shell. It SHALL NOT initialize Bundler state, inspect legacy state, install agent assets, or execute repository behavior.

#### Scenario: Open a missing home natively
- **WHEN** a caller selects a missing ZPP home and invokes `zpp open`
- **THEN** ZPP creates and opens exactly that home without creating its `bundler` child

### Requirement: Confirmed complete product reset
Root `zpp reset` SHALL require `--yes`, remove every ownership-safe selected ZPP projection through Agent Router, and replace only the selected home's exact `bundler` child with fresh empty lease state after projection cleanup succeeds. It SHALL target the `zpp-traits` hook and remaining packaged companions, exclude the removed workspace skill, and never inspect or change legacy `openlease` state.

#### Scenario: Reset complete user integration and state
- **WHEN** confirmed reset preflight succeeds and every selected removal succeeds or is absent
- **THEN** ZPP removes the current owned integration and replaces only the `bundler` state child

### Requirement: Complete reset preflight and retry safety
Before reset mutation, ZPP SHALL inspect every selected current projection, validate the exact `bundler` child, and prepare replacement Bundler lease state. Any unmanaged or unsafe projection or state target SHALL abort before mutation. Any removal failure SHALL leave prior Bundler state unchanged, and retry SHALL treat already absent projections as eligible.

#### Scenario: Preserve state after runtime removal failure
- **WHEN** a planned Agent Router removal fails after preflight
- **THEN** ZPP reports the failure and leaves prior Bundler state unchanged

### Requirement: Reset ownership and destructive-path boundary
Reset SHALL preserve the selected ZPP home and every path outside its exact `bundler` child, including legacy `openlease` state, repository documents, project projections, plugins, and worktrees. It SHALL reject broad, symlinked, or incompatible state targets and SHALL NOT follow a symlink.

#### Scenario: Preserve legacy and user-authored content
- **WHEN** the selected home contains an `openlease` child or other user-authored paths outside `bundler`
- **THEN** reset changes none of them

### Requirement: Concise reset reporting
Confirmed reset SHALL print one concise summary by default identifying projection outcomes and the Bundler state result; `--json` SHALL emit the complete deterministic report.

#### Scenario: Report successful reset concisely
- **WHEN** confirmed reset completes without `--json`
- **THEN** ZPP prints one line summarizing integration cleanup and Bundler state replacement

### Requirement: Shared lifecycle projection inventory
Root initialization, synchronization, and reset SHALL derive one shared per-agent inventory containing `zpp-traits`, `zpp-workflow`, every remaining packaged companion skill, and the canonical generated OpenSpec operation skills. It SHALL contain neither `zpp-session` nor `zpp-workspace-management`.

#### Scenario: Share one current projection inventory
- **WHEN** lifecycle operations enumerate current ZPP integration assets
- **THEN** all use the same deterministic hard-cut inventory
