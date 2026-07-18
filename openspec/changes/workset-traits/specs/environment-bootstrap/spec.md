# environment-bootstrap

## ADDED Requirements

### Requirement: Managed tool mode
For tools that ship release binaries, a toolchain entry MAY declare a managed mode: zpp fetches the pinned release binary into `~/.zpp/bin/` and invokes it from there, instead of requiring the tool on PATH. The mode SHALL be configurable per tool (`system` = PATH-provided, never installed by zpp; `managed` = zpp-fetched under `~/.zpp/bin/`). `zpp doctor` SHALL report, for such tools, the active mode and which binary would be used. saucepan is the first managed-mode tool, defaulting to `managed`.

#### Scenario: Doctor reports mode and provenance
- **WHEN** saucepan runs in managed mode with a fetched binary present
- **THEN** `zpp doctor` reports saucepan as present, mode `managed`, with the `~/.zpp/bin/` path

#### Scenario: System mode respects the user's toolchain
- **WHEN** a tool is configured `system` and is present on PATH
- **THEN** zpp uses the PATH binary and never writes to `~/.zpp/bin/` for that tool
