## MODIFIED Requirements

### Requirement: Permanent workflow bundle ownership
ZPP SHALL package the seven permanent `zpp-*` workflow skills as one versioned owned bundle. Installed copies SHALL be projections of the packaged bundle, preserve every required skill resource, and SHALL NOT embed agent, application-platform, framework, test-runner, or optional-trait policy in skill bodies.

Permanent skills SHALL retain stage-specific operations, hard gates, verification authority, OpenSpec operation ownership, and zmem materiality in their owning skill. Cross-cutting advisory governance SHALL remain in independently configurable standard traits rather than being repeated across skill bodies.

Each completed skill stage SHALL hand its result to the next owning workflow. When automatic progression or explicit end-to-end delegation applies, a satisfied checkpoint or ordinary stage transition SHALL continue without an approval-only pause.

ZPP SHALL establish managed ownership and compatibility through bundle metadata plus exact owned content rather than directory names. Passive trait `skill_lookup` metadata SHALL NOT execute a skill or grant authority.

#### Scenario: Use the permanent workflow bundle
- **WHEN** a user installs the workflow skills and resolves the standard advisory traits
- **THEN** stage-specific enforcement remains skill-owned while shared guidance and automatic handoffs remain advisory

## ADDED Requirements

### Requirement: Workflow lifecycle isolation from authored profiles
Workflow installation, update, and removal SHALL operate only on selected managed agent projections. These operations SHALL NOT create, modify, rename, or remove any user profile or authored trait content, including the persistent `default` profile.

#### Scenario: Maintain skills without changing profiles
- **WHEN** a user installs, updates, declines removal, or confirms removal of selected workflow projections
- **THEN** only eligible managed agent projection state changes and every authored profile remains unchanged

