## MODIFIED Requirements

### Requirement: Managed update and removal
Update SHALL operate only on the explicitly selected managed scope, make compatible projections no-ops, replace outdated managed projections with the packaged bundle, and leave every unselected global or local scope unchanged.

A structurally valid historical manifest SHALL remain ownership evidence when its declared bundle version or complete owned file set differs from the current packaged bundle. ZPP SHALL validate the historical projection against exactly the paths and digests declared by that manifest, classify the intact projection as outdated, remove only those declared owned paths during replacement, and install the complete current bundle and manifest atomically.

Removal SHALL require confirmation unless `--yes` or `-y` is supplied and SHALL remove only metadata-owned ZPP paths from the selected managed projection. Update and removal SHALL reject absent projections, malformed manifests, unsafe manifest paths, content that differs from its manifest, conflicting paths, or user-owned selected state without partial mutation. Diagnostics SHALL distinguish absent selected state from malformed, conflicting, or user-owned state.

#### Scenario: Maintain one selected managed scope
- **WHEN** a user updates or confirms removal for selected managed projections
- **THEN** only their owned state changes and unrelated or unselected state remains unchanged

#### Scenario: Update an intact historical managed bundle
- **WHEN** a selected projection exactly matches a structurally valid manifest for an earlier workflow bundle
- **THEN** ZPP replaces only its declared owned paths with the current complete bundle and preserves unrelated content

#### Scenario: Reject an absent selected projection clearly
- **WHEN** a user requests update or removal in a scope with no managed projection
- **THEN** ZPP rejects the request as not installed in that scope without describing it as unmanaged content
