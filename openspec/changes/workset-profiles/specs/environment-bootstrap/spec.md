# environment-bootstrap

## MODIFIED Requirements

### Requirement: Config-driven toolchain filtering
The doctor/bootstrap toolchain SHALL be configurable through a `[doctor]` section resolved through the standard config tiers (the store's published `default` profile → workset profile → repo `zpp.toml`, lists unioned), with `zpp doctor [PATH]` and `zpp bootstrap [PATH]` resolving the section for their context. `doctor.exclude` SHALL remove the named builtin tools from the effective table consumed by **both** doctor and bootstrap — an excluded tool is neither checked nor installed. When config resolution fails, both commands SHALL degrade to the builtin table with a warning rather than fail.

#### Scenario: Excluded tool is neither checked nor installed
- **WHEN** the resolved config sets `doctor.exclude = ["codegraph"]`
- **THEN** `zpp doctor` reports no codegraph line and `zpp bootstrap` does not attempt to install codegraph

#### Scenario: Store tier publishes fleet expectations
- **WHEN** a governing store's `zpp.toml` declares `[doctor]` entries inside `[profiles.default]` and a governed repo adds its own
- **THEN** the effective table for that repo's path reflects the union of both tiers

#### Scenario: Degraded resolution keeps doctor alive
- **WHEN** config resolution fails for the given path
- **THEN** doctor runs against the builtin table and reports the degradation as a warning
