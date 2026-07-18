# environment-bootstrap

## ADDED Requirements

### Requirement: Config-driven toolchain filtering
The doctor/bootstrap toolchain SHALL be configurable through a `[doctor]` section resolved through the standard config tiers (store defaults → workset overlay → repo `zpp.toml`, lists unioned), with `zpp doctor [PATH]` and `zpp bootstrap [PATH]` resolving the section for their context. `doctor.exclude` SHALL remove the named builtin tools from the effective table consumed by **both** doctor and bootstrap — an excluded tool is neither checked nor installed. When config resolution fails, both commands SHALL degrade to the builtin table with a warning rather than fail.

#### Scenario: Excluded tool is neither checked nor installed
- **WHEN** the resolved config sets `doctor.exclude = ["codegraph"]`
- **THEN** `zpp doctor` reports no codegraph line and `zpp bootstrap` does not attempt to install codegraph

#### Scenario: Store tier publishes fleet expectations
- **WHEN** a governing store's `zpp.default.toml` declares `[doctor]` entries and a governed repo adds its own
- **THEN** the effective table for that repo's path reflects the union of both tiers

#### Scenario: Degraded resolution keeps doctor alive
- **WHEN** config resolution fails for the given path
- **THEN** doctor runs against the builtin table and reports the degradation as a warning

### Requirement: Additional detect-only tools
Repeatable `[[doctor.more]]` entries SHALL add tools to the doctor report in the form `which = "<cmd>"`, `successnote = "<note>"`. `more` tools are detect-only: doctor SHALL check presence via PATH lookup, and bootstrap SHALL never install them nor count them as manual steps. When a `more` tool is present, doctor SHALL display its `successnote` as usage guidance; when missing, doctor SHALL report it plainly with no hint and a failing exit status.

#### Scenario: Present more-tool shows its usage note
- **WHEN** `[[doctor.more]]` declares `which = "gh"` with a successnote and gh is on PATH
- **THEN** the doctor line for gh shows the successnote

#### Scenario: Missing more-tool reports plainly
- **WHEN** the declared tool is not on PATH
- **THEN** doctor marks it missing with no hint text and exits nonzero

#### Scenario: Bootstrap ignores more-tools
- **WHEN** a declared `more` tool is missing and `zpp bootstrap` runs
- **THEN** bootstrap neither installs it nor lists it as a remaining manual step
