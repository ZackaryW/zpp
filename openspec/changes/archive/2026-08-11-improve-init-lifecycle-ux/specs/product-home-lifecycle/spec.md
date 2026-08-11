## ADDED Requirements

### Requirement: Concise reset reporting
Confirmed root `zpp reset --yes` SHALL print exactly one concise human summary line by default after successful cleanup and state replacement. The summary SHALL aggregate removed and already-absent integration outcomes and identify the OpenLease state result without printing inspection or removal arrays. When the caller supplies `--json`, reset SHALL instead emit its complete deterministic inspection, removal, and state report as valid JSON.

#### Scenario: Summarize confirmed reset
- **WHEN** confirmed reset succeeds without `--json`
- **THEN** ZPP prints one line summarizing removed and already-absent integrations and the replaced OpenLease state

#### Scenario: Request reset JSON
- **WHEN** confirmed reset succeeds with `--json`
- **THEN** ZPP emits the complete deterministic reset report as valid JSON instead of the human summary
