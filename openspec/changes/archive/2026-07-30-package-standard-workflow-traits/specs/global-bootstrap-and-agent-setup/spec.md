## MODIFIED Requirements

### Requirement: Product identity and command surface
ZPP SHALL identify itself as version 0.9.0 and expose initialization, profile, persistent global activation, saved-profile, local-layer, resolution, standard-workflow lifecycle, help, and version behavior through the confirmed command hierarchy. Native lifecycle-hook configuration SHALL remain part of initialization, while standard-workflow distribution SHALL use the independent `workflow` command group. The generic `skill` command group SHALL NOT remain available.

#### Scenario: Inspect the installed product
- **WHEN** a user requests the version and help output
- **THEN** ZPP reports version 0.9.0, exposes profile and global lifecycle behavior plus the independent standard-workflow lifecycle group, and does not expose a generic skill-management group

### Requirement: Neutral user-state initialization
Initialization SHALL create an unconditional neutral global trait layer, a permanent user-owned `default` profile containing the bundled standard traits, and the saved-override and independent-cache namespaces under the user's ZPP state. It SHALL NOT create project-local state or derived trait caches.

Initialization SHALL create the bundled `default` profile only when it is absent. It SHALL validate all existing required managed user sources before creating missing state, preserve valid existing authored bytes including a user-edited `default` profile, create only missing required entries, and be idempotent. Invalid managed state SHALL reject initialization without partial user-state writes.

#### Scenario: Initialize missing user state
- **WHEN** initialization runs against absent or valid partial user state
- **THEN** neutral global state and the permanent default profile exist, valid existing authored bytes are unchanged, and no project or derived-cache state is created

#### Scenario: Preserve an existing default
- **WHEN** initialization encounters a valid user-edited `default` profile
- **THEN** the complete profile remains byte-for-byte unchanged and bundled content is not reapplied

#### Scenario: Reject invalid managed user state
- **WHEN** initialization encounters an invalid managed source while other required entries are missing
- **THEN** initialization fails, identifies the invalid source, and leaves the complete user state unchanged

