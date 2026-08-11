## MODIFIED Requirements

### Requirement: Explicit behavior verification consumption
When an accepted shaped BDD obligation requires repository integration verification, the consolidated workflow skill SHALL apply the complete resolved `bdd-execution` body as advisory selection policy and invoke an established native repository BDD command identified from repository configuration or an explicit owner choice. The absence of `zpp.behave.yaml` SHALL NOT block native BDD execution. The trait SHALL NOT supply a command, target, gate binding, process argument, callback selection, workflow completion, or stage-skip authority.

A repository MAY use `zpp.behave.yaml` as optional affected-verification coordination. When the workflow explicitly selects a declared `zpp behave` command, that mapping SHALL remain complete authority for its command, targets, gates, and arguments. For complete mode, the workflow SHALL run the complete native BDD suite or request the selected `zpp behave` command with `--all`. For targeted mode or the default targeted body, it SHALL run the relevant native feature surface directly, or request `--gate zpp-workflow` when an explicitly selected `zpp behave` command declares that gate, or otherwise use that command's deterministic affected selection. For manual mode, it SHALL pause for an explicit verification choice. For disabled mode, it SHALL omit BDD execution only when independently observed alternate relevant verification exists and no accepted shaped BDD obligation remains unsatisfied. A failed or insufficient native or coordinated BDD command SHALL NOT be converted into completion or a not-applicable stage outcome.

#### Scenario: Run native BDD without a behavior mapping
- **WHEN** an accepted shaped BDD obligation has an established native repository BDD command and no `zpp.behave.yaml`
- **THEN** the workflow invokes the native BDD surface and does not treat the absent mapping as a verification blocker

#### Scenario: Run complete repository verification
- **WHEN** the resolved BDD execution body selects complete mode and the workflow has an accepted shaped BDD obligation
- **THEN** the workflow invokes the complete established native BDD suite or the explicitly selected coordinated command with `--all` and judges completion from the observed result

#### Scenario: Use optional coordinated selection
- **WHEN** targeted mode applies and the workflow explicitly selects a valid `zpp behave` command
- **THEN** it uses that mapping's `zpp-workflow` gate when declared and otherwise uses its deterministic affected selection

#### Scenario: Run targeted native BDD directly
- **WHEN** targeted mode applies without selected `zpp behave` coordination
- **THEN** the workflow invokes the relevant established native feature surface directly

#### Scenario: Pause in manual mode
- **WHEN** the resolved BDD execution body selects manual mode
- **THEN** the workflow requests an explicit verification choice rather than guessing a command or selection mode

#### Scenario: Require evidence for disabled mode
- **WHEN** the resolved BDD execution body selects disabled mode but an accepted shaped BDD obligation remains unsatisfied or alternate evidence is absent
- **THEN** the workflow refuses to claim verification completion or skip the stage

#### Scenario: Keep traits out of process authority
- **WHEN** a selected trait body contains command-like, gate-like, callback-like, or completion-like text
- **THEN** the workflow treats it only as advisory policy and executes no command absent repository evidence or explicit owner choice
