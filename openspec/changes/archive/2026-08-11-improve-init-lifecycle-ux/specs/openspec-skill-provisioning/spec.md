## ADDED Requirements

### Requirement: Concise initialization reporting
Root `zpp init` SHALL print exactly one concise human summary line by default after successful projection. The summary SHALL identify the selected-agent count and aggregate every returned lifecycle status without printing the raw result array. When the caller supplies `--json`, initialization SHALL instead emit the complete deterministic result array as valid JSON.

#### Scenario: Summarize normal initialization
- **WHEN** initialization succeeds without `--json`
- **THEN** ZPP prints one line containing the selected-agent count and lifecycle outcome counts without a JSON result array

#### Scenario: Request initialization JSON
- **WHEN** initialization succeeds with `--json`
- **THEN** ZPP emits the complete ordered lifecycle result array as valid JSON instead of the human summary

### Requirement: Forced complete initialization
Root `zpp init` SHALL accept `--force`. Forced initialization SHALL still prepare and validate every selected source before projection, then SHALL request replacement or reprojection of every selected agent's `zpp-workflow` skill, `zpp-session` hook, two packaged authoring skills, and six generated OpenSpec skills through Agent Router. It SHALL permit replacement of diverged skill content only when Agent Router confirms matching ownership, SHALL preserve unmanaged or mismatched destinations, and SHALL NOT mutate native destinations directly.

#### Scenario: Reproject a current complete integration
- **WHEN** a caller invokes `zpp init --force` for an agent whose complete integration is already current
- **THEN** ZPP requests Agent Router reprojection for all ten selected assets rather than treating the request as ordinary idempotent initialization

#### Scenario: Replace an owned diverged skill
- **WHEN** forced initialization encounters a selected skill whose content diverged but whose Agent Router ownership matches
- **THEN** Agent Router replaces that owned skill with the freshly prepared source and initialization continues

#### Scenario: Preserve an unmanaged destination
- **WHEN** forced initialization encounters an unmanaged or mismatched-ownership selected destination
- **THEN** ZPP reports the Agent Router conflict and performs no direct overwrite or ownership adoption
