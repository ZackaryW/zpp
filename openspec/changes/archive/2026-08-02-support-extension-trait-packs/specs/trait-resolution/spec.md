## MODIFIED Requirements

### Requirement: Participating layer precedence
When an invoking agent is identified, resolution SHALL compose that agent's validated active plugin trait sources before user-owned layers. User-owned layers SHALL then compose in this order: global, the optional profile named exclusively by `ZPP_PROFILE`, the closest matching saved override, and repository `.zpp` layers from the Git worktree root toward the target.

Unset `ZPP_PROFILE` SHALL mean global-only profile selection after any eligible invoking-agent plugin sources. An unknown named profile SHALL fail resolution. Saved overrides SHALL remain eligible outside Git worktrees, only the longest matching canonical ancestor SHALL participate, and a binding whose saved layer is missing SHALL fail resolution. Repository and subfolder layers SHALL not be required outside Git.

Without an invoking agent identity, resolution SHALL preserve the existing global, optional-profile, saved, and repository order and SHALL include no external plugin source.

#### Scenario: Resolve every participating layer class
- **WHEN** an invoking agent has active plugin trait sources and the target has global, active-profile, multiple matching saved, repository-root, and nested layer context
- **THEN** plugin sources participate first, global and the active profile follow, only the closest saved override participates, and repository layers participate root-to-target

#### Scenario: Preserve user override authority over plugin sources
- **WHEN** a user-owned layer replaces a plugin-authored trait document, applies configuration to it, or replaces inherited triggers
- **THEN** the ordinary later-layer replacement, overlay, and trigger-list semantics govern the effective result

#### Scenario: Preserve direct resolution behavior
- **WHEN** resolution has no invoking agent identity
- **THEN** global is the first participating layer and no editor plugin source participates

#### Scenario: Resolve saved state outside Git
- **WHEN** a target outside every Git worktree descends from a valid saved binding
- **THEN** eligible invoking-agent plugin sources, global, and that closest saved layer resolve without any repository layer

#### Scenario: Reject an invalid selected layer
- **WHEN** `ZPP_PROFILE` names an unknown profile or a selected saved binding has no authored layer
- **THEN** resolution fails with the missing selection identified and emits no fallback output
