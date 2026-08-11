## Why

ZPP 2.0 currently resolves repository behavior policy but omits the previous `zpp behave` verification engine, so existing `zpp.behave.yaml` declarations and the configuration skill have no executable public command. Restoring that capability is required before ZPP 2.0 can replace the active workflow without losing affected integration-test orchestration.

## What Changes

- Reintroduce `zpp behave init` and `zpp behave COMMAND` with the version-1 dedicated YAML contract, deterministic affected-target selection, named target and gate selection, revision-range selection, and the `argv`, `nx`, and `go-task` providers.
- Register behavior verification as the independent `zpp.behave` OpenLease extension. Direct CLI use binds the selected repository's exact `zpp.behave.yaml` for the invocation and requires no registered repository or space.
- Keep ordinary OpenLease integration invocation-scoped: repository traits and `zpp.behave.yaml` are opened directly from the discovered worktree without repository registration, space selection, or agent-visible OpenLease coordination. Preserve explicitly selected reconciliation cross-checks only when OpenLease already supplies real repository or cohort context.
- Reimplement the adopted behavior contract within ZPP 2.0's established `core`, `cli`, `artifacts`, and `utils` boundaries; do not add a legacy compatibility loader or restore the old package architecture.
- Make the consolidated workflow consume the resolved `bdd-execution` policy when choosing behavior verification and use `zpp-workflow` as the stable gate identity for complete workflow verification. No legacy gate-name migration is added.
- **BREAKING** relative to the incomplete ZPP 2.0 preview: the stable public command hierarchy now includes the `behave` group and behavior verification again becomes part of workflow completion when its resolved policy requires it.

## Capabilities

### New Capabilities

- `behavior-verification`: Defines repository-owned verification declarations, deterministic selection and provider execution, direct OpenLease operation, and opt-in reconciliation cross-checks.

### Modified Capabilities

- `repository-trait-bootstrap`: Adds the restored `behave` command group and recognizes OpenLease ownership of the independent `zpp.behave` document extension alongside `zpp.traits`.
- `consolidated-workflow-skill`: Requires the workflow to interpret `bdd-execution` policy through the restored behavior command and establishes `zpp-workflow` as its gate identity.

## Impact

- Public CLI: `zpp behave init` and `zpp behave COMMAND` return.
- Configuration: repositories may own a dedicated root `zpp.behave.yaml` version-1 document.
- Runtime: OpenLease registers both `zpp.traits` and `zpp.behave`; repository hooks and direct behavior commands remain no-space operations, while explicitly selected reconciliation callbacks retain OpenLease cross-check capability.
- Packaging and workflow assets: behavior configuration/execution support and `bdd-execution` guidance are reconciled with the single consolidated workflow skill.
- Tests: behavior mapping, selection, providers, CLI, direct binding, hook isolation, opt-in reconciliation callbacks, and workflow integration require fail-first coverage.

## Unresolved — Do Not Assume

None.
