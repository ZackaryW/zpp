## ADDED Requirements

### Requirement: Explicit behavior verification consumption
When an accepted shaped BDD obligation requires repository integration verification, the consolidated workflow skill SHALL apply the complete resolved `bdd-execution` body as advisory selection policy and invoke only a command declared by the repository's `zpp.behave.yaml`. The trait SHALL NOT supply a command, target, gate binding, process argument, callback selection, workflow completion, or stage-skip authority.

For `bdd_mode = "complete"`, the workflow SHALL request the selected command with `--all`. For `bdd_mode = "targeted"` or the default targeted body, it SHALL request `--gate zpp-workflow` when the selected command declares that gate and otherwise invoke default deterministic affected selection. For `bdd_mode = "manual"`, it SHALL pause for an explicit verification choice. For `bdd_mode = "disabled"`, it SHALL omit behavior execution only when independently observed alternate relevant verification exists and no accepted shaped BDD obligation remains unsatisfied. A failed or insufficient behavior command SHALL NOT be converted into completion or a not-applicable stage outcome.

#### Scenario: Run complete repository verification
- **WHEN** the resolved BDD execution body selects complete mode and the workflow has an accepted shaped BDD obligation
- **THEN** the workflow invokes the chosen repository-declared behavior command with `--all` and judges completion from the observed result

#### Scenario: Use the consolidated workflow gate
- **WHEN** targeted mode applies and the chosen command declares gate `zpp-workflow`
- **THEN** the workflow invokes that exact gate without consulting a legacy stage-skill identity

#### Scenario: Fall back to deterministic affected selection
- **WHEN** targeted mode applies and the chosen command does not declare gate `zpp-workflow`
- **THEN** the workflow invokes the command without a selection override and uses deterministic affected filtering

#### Scenario: Pause in manual mode
- **WHEN** the resolved BDD execution body selects manual mode
- **THEN** the workflow requests an explicit verification choice rather than guessing a command or selection mode

#### Scenario: Require evidence for disabled mode
- **WHEN** the resolved BDD execution body selects disabled mode but an accepted shaped BDD obligation remains unsatisfied or alternate evidence is absent
- **THEN** the workflow refuses to claim verification completion or skip the stage

#### Scenario: Keep traits out of process authority
- **WHEN** a selected trait body contains command-like, gate-like, callback-like, or completion-like text
- **THEN** the workflow treats it only as advisory policy and executes no undeclared process or lifecycle mutation

### Requirement: Stable consolidated workflow gate identity
The packaged consolidated workflow skill identity SHALL be `zpp-workflow`, and repository behavior mappings MAY use that exact identity as a command-local gate for workflow-owned verification. ZPP 2.0 SHALL NOT alias, translate, or infer a gate from any former `zpp-flow-*` skill identity.

#### Scenario: Select the current workflow gate
- **WHEN** a repository declares a valid `zpp-workflow` gate for the chosen behavior command
- **THEN** targeted workflow verification may select that gate as the current packaged skill's repository-owned target set

#### Scenario: Encounter only a legacy gate
- **WHEN** a repository declares a former `zpp-flow-*` gate but not `zpp-workflow`
- **THEN** ZPP applies the targeted affected-selection fallback and performs no legacy gate migration
