# environment-bootstrap

## Purpose

Install and verify the governance toolchain cross-platform from one codebase, replacing the duplicated `.sh`/`.ps1` setup and doctor scripts. uv is the sole prerequisite; doctor and bootstrap share one tool table so they can never disagree.

## Requirements

### Requirement: Data-driven toolchain table
zpp SHALL maintain one table of governance tools — at minimum node, jq, ripgrep, zmem (via uv), codegraph, and the OpenSpec CLI — each entry pairing a detect predicate with per-OS install strategies. `zpp doctor` and `zpp bootstrap` SHALL both consume this table so verification and installation can never disagree about what the toolchain is.

#### Scenario: Doctor and bootstrap agree
- **WHEN** `zpp doctor` reports a tool missing
- **THEN** `zpp bootstrap` attempts to install exactly that tool, and after success doctor reports it present

### Requirement: Doctor verifies without mutating
`zpp doctor` SHALL run detect-only across the table and report one line per tool (present with version where cheap, or missing with install guidance). It SHALL work cross-platform from a single codebase and SHALL NOT install, modify, or delete anything.

#### Scenario: Read-only verification
- **WHEN** `zpp doctor` runs on a machine missing codegraph
- **THEN** the report marks codegraph missing with guidance, and no installation is attempted

### Requirement: Bootstrap installs idempotently
`zpp bootstrap` SHALL install missing tools using the OS-appropriate strategy (brew on darwin, the documented fallback elsewhere), skipping tools already present. Re-running bootstrap on a complete machine SHALL make no changes. uv is the sole prerequisite zpp may assume; when a tool cannot be installed non-interactively on the current OS, bootstrap SHALL print the manual instruction and continue rather than abort the run.

#### Scenario: Idempotent re-run
- **WHEN** `zpp bootstrap` runs twice on the same machine
- **THEN** the second run reports every tool as already present and installs nothing

#### Scenario: Partial installability
- **WHEN** one tool has no non-interactive install path on the current OS
- **THEN** bootstrap installs the remaining tools, prints the manual instruction for that one, and exits with a status distinguishing "complete" from "manual steps remain"

### Requirement: Managed tool mode
For tools that ship release binaries, a toolchain entry MAY declare a managed mode: zpp fetches the pinned release binary into `~/.zpp/bin/` and invokes it from there, instead of requiring the tool on PATH. The mode SHALL be configurable per tool (`system` = PATH-provided, never installed by zpp; `managed` = zpp-fetched under `~/.zpp/bin/`). `zpp doctor` SHALL report, for such tools, the active mode and which binary would be used. saucepan is the first managed-mode tool, defaulting to `managed`.

#### Scenario: Doctor reports mode and provenance
- **WHEN** saucepan runs in managed mode with a fetched binary present
- **THEN** `zpp doctor` reports saucepan as present, mode `managed`, with the `~/.zpp/bin/` path

#### Scenario: System mode respects the user's toolchain
- **WHEN** a tool is configured `system` and is present on PATH
- **THEN** zpp uses the PATH binary and never writes to `~/.zpp/bin/` for that tool

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
