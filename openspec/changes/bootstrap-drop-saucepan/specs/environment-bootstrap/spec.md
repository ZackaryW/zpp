# Delta: environment-bootstrap

## MODIFIED Requirements

### Requirement: Managed tool mode
For tools that ship release binaries, a toolchain entry MAY declare a managed
mode: zpp fetches the pinned release binary into `~/.zpp/bin/` and invokes it
from there, instead of requiring the tool on PATH. The mode SHALL be
configurable per tool (`system` = PATH-provided, never installed by zpp;
`managed` = zpp-fetched under `~/.zpp/bin/`). `zpp doctor` SHALL report, for
such tools, the active mode and which binary would be used. saucepan is the
first managed-mode tool, defaulting to `managed`.

A managed tool MAY additionally be marked **optional**: `zpp bootstrap` SHALL
NOT fetch it, count it as a manual step, or fail because of it — it is
provisioned lazily at its point of use (saucepan: on first
`zpp trait fetch`). `zpp doctor` SHALL still report an optional tool's
presence, mode, and provenance, but its absence SHALL NOT contribute to
doctor's failure exit. saucepan is optional.

#### Scenario: Managed binary reported
- **WHEN** saucepan runs in managed mode with a fetched binary present
- **THEN** `zpp doctor` reports saucepan as present, mode `managed`, with the
  `~/.zpp/bin/` path

#### Scenario: Bootstrap ignores optional tools
- **WHEN** `zpp bootstrap` runs with saucepan absent and its release
  unreachable
- **THEN** the run neither fetches saucepan nor fails because of it, and no
  saucepan manual step is emitted

#### Scenario: Doctor does not fail on optional absence
- **WHEN** `zpp doctor` runs with every core tool present and saucepan absent
- **THEN** the report shows saucepan as absent-optional and the command exits
  0
