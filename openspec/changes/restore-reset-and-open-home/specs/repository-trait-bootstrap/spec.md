## MODIFIED Requirements

### Requirement: Stable public command hierarchy
ZPP SHALL export its Typer application as `zpp.cli:app`; expose root `init`, `open`, `reset`, `resolve`, and `behave COMMAND` with reserved `behave init`; provide exact repository initialization as grouped `trait init`; and retain the `workflow install`, `workflow update`, and `workflow remove` command group. `reset` SHALL require explicit confirmation according to the product-home lifecycle contract. `behave COMMAND` SHALL accept `--all`, repeatable `--target`, `--gate`, and paired `--base` and `--head` according to the behavior-verification selection contract. Trait explanations SHALL be requested as part of `resolve`, and workflow lifecycle SHALL NOT be exposed as a flat `install-workflow` command. The commands SHALL delegate configuration and projection operations to OpenLease and Agent Router rather than exposing a mirrored OpenLease space lifecycle.

Root `--path` SHALL identify the selected ZPP home. ZPP SHALL derive its OpenLease state root as the selected home's `openlease` child rather than accepting the product home and component state root as the same directory.

#### Scenario: Inspect command help
- **WHEN** a user opens ZPP command help
- **THEN** root `init`, `open`, `reset`, `resolve`, and `behave COMMAND`, grouped `trait init`, and grouped `workflow install|update|remove` are present, while flat `init-trait`, flat `install-workflow`, standalone `explain`, and mirrored `space` commands are absent

#### Scenario: Explain one resolution
- **WHEN** a user resolves a target with the explanation option
- **THEN** the same side-effect-free resolution operation emits its source, policy, flavor, facet, and evidence decisions without changing the selected bodies

#### Scenario: Inspect behavior selection help
- **WHEN** a user inspects `zpp behave --help`
- **THEN** the command documents its command-or-init argument and complete, exact-target, gate, and paired-revision selection options

#### Scenario: Route through one selected home
- **WHEN** a caller supplies root `--path` and invokes an OpenLease-backed command
- **THEN** ZPP passes the selected home's exact `openlease` child to OpenLease and does not reinterpret the command target as the state root
