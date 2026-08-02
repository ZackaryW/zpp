## ADDED Requirements

### Requirement: Standard profile trait resolution
The permanent `default` profile SHALL participate through the established profile layer when `ZPP_PROFILE` selects it. Persistent profile activation SHALL instead copy its authored content into global without changing temporary profile selection.

When the standard profile participates, only traits named by composed `trait.json` rules SHALL activate. Later participating `traitsConfig` values SHALL override standard frontmatter configuration without activating or deactivating a trait, and later trigger rules MAY independently activate optional standard trait definitions.

#### Scenario: Resolve the selected standard profile
- **WHEN** `ZPP_PROFILE` selects the default profile
- **THEN** the platform-neutral base resolves in effective order with its default configuration and no inactive optional trait

#### Scenario: Overlay and extend standard traits
- **WHEN** a later participating layer overrides automatic-workflow configuration and activates one optional standard trait
- **THEN** the base remains active with the effective override and only the selected optional trait is added
