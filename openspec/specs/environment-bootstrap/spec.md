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
