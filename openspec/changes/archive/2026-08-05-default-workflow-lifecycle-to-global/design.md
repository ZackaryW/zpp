## Context

See `proposal.md` for motivation and `specs/workflow-skill-distribution/spec.md` for the accepted behavior. The current Typer commands expose a `--global` Boolean and translate its absence to local scope. Core lifecycle orchestration already accepts an explicit `"global" | "local"` scope, so the behavioral inversion belongs at the CLI boundary rather than in projection, ownership, or mutation utilities.

Executable examples and README commands currently encode the old default extensively. Global installation additionally owns the complete hook and OpenSpec bootstrap outcome, while local installation retains compatible-global deduplication, `--force`, and opt-in `--with-openspec` behavior.

## Goals / Non-Goals

**Goals:**

- Make the default workflow lifecycle invocation select global scope consistently across install, update, and remove.
- Make `--local` the sole explicit workflow scope selector and preserve the current-directory default for local operations.
- Reject positional targets outside explicit local scope before core mutation begins.
- Preserve core lifecycle, projection, ownership, atomicity, and report behavior.

**Non-Goals:**

- Do not change `zpp init`, agent selection, native destinations, managed manifests, or workflow content.
- Do not add a deprecated `--global` alias or infer local scope from a positional target.
- Do not change when global or local OpenSpec skills are generated.

## Decisions

### Invert scope only at the CLI boundary

Replace the three command-level `--global` parameters with `--local` parameters and derive `scope="local" if local else "global"` in the shared execution path. Keeping core orchestration explicitly scoped preserves its existing invariants and minimizes the changed surface. Inverting core defaults was rejected because internal callers already pass scope explicitly and should remain unambiguous.

### Require explicit local intent for every repository target

Accept an optional positional target only alongside `--local`; when `--local` has no target, use the current directory as today. Rejecting a bare target prevents command shape from silently overriding the new global default. Retaining a bare-target compatibility form was rejected because it would leave two implicit scope-selection rules.

### Remove `--global` without an alias

Let Typer reject the removed option as unknown. A deprecated no-op alias was rejected because it would obscure the new command contract and prolong ambiguous scripts. This is an intentional breaking change documented in the proposal and README migration examples.

### Keep local-only options visible but validate their scope

`--force` and `--with-openspec` remain install options, but they are valid only with `--local`. Reject them for the new default global scope before mutation so local policy cannot be silently ignored. Existing local and global lifecycle behavior after scope resolution remains unchanged.

## Risks / Trade-offs

- **Existing unqualified commands change destination** → Treat this as a documented breaking change and update every executable example and help assertion.
- **Existing scripts using `--global` fail** → Remove the option deliberately and provide direct `--local` migration examples where local behavior was intended.
- **A bare target may previously have selected local scope** → Reject it with a scope-oriented usage error so the user must make local intent explicit.
- **Shared CLI helpers may accidentally leave one command on old semantics** → Drive install, update, and remove through one local-selector execution boundary and cover all three in BDD.

## Migration Plan

1. Replace `--global` with `--local` across the workflow CLI and invert shared scope derivation.
2. Add pre-mutation validation for positional targets and local-only install options.
3. Update executable features, unit tests, and README examples to the new syntax and defaults.
4. Verify global default outcomes, explicit-local outcomes, invalid combinations, and idempotent lifecycle behavior across all supported agents.

Rollback restores the old CLI selector and examples; managed projections remain valid because their on-disk formats and destinations do not change.
