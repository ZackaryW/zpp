## Context

See `proposal.md` for motivation. ZPP is a Python/Typer CLI with Pydantic and PyYAML already in its runtime dependency set, a process utility that executes typed argv without a shell, a packaged standard profile, and an atomically managed workflow-skill bundle. Its Behave suite currently has eight top-level feature files and two globally loaded step modules, including one roughly 5,000-line module. Nx is an optional repository-owned executable; it is not a Python dependency or a ZPP trait.

## Goals / Non-Goals

**Goals:**

- Give repositories one validated committed mapping for affected verification and complete audits.
- Keep selection, provider discovery, and execution deterministic and owned by ZPP core.
- Make the current Behave suite independently executable and cacheable by stable capability roots.
- Upgrade existing valid persistent defaults additively as part of global workflow maintenance.
- Teach agents how to author the mapping without allowing agent output to become executable runtime input.

**Non-Goals:**

- Installing, migrating, or configuring Nx, Nx Cloud, or Nx framework plugins.
- Replacing a repository's test runner or imposing Gherkin on TypeScript or Flutter.
- Inferring dependency graphs at runtime from agent output.
- Making Nx mandatory or coupling behavior orchestration to workflow lifecycle commands.

## Decisions

### Versioned declarative mapping

`zpp.behave.yaml` will use a strict versioned Pydantic model. A command owns a provider declaration and a keyed target map. Each target has one provider value and one or more repository-relative impact globs. Provider-neutral declarations contain a typed argv list with exactly one `{targets}` element. Nx declarations contain one workspace target name, optional committed extra argv, and target values that name Nx projects. Unknown fields, duplicate YAML keys, invalid paths, invalid globs, duplicate target values, undeclared targets, and invalid expansion positions fail before process creation.

An empty `commands` map is valid only as the scaffold produced by `zpp behave init`; selecting a command from it fails normally. This lets initialization avoid inventing a runner or command. A clean mapped change selects no targets and exits successfully without starting a process. Alternatives considered were a generated runner-specific default, which would guess repository policy, and an agent-generated executable command, which would make runtime behavior nondeterministic.

### Repository and change resolution

Behavior commands resolve the Git worktree root and read only its root `zpp.behave.yaml`. Local mode unions tracked changes relative to `HEAD` with staged, unstaged, and untracked non-ignored paths. Revision mode accepts `--base` and `--head` together and compares those exact revisions. Every path is normalized to repository-relative POSIX form. A changed path matching no impact glob selects all declared targets; otherwise selection is the stable mapping-order union of matching targets. `--all` bypasses impact filtering but not provider caches.

Alternatives considered were an automatically learned mapping, rejected because it cannot be reviewed or reproduced, and treating unmapped paths as unaffected, rejected because it creates false-green verification.

### Provider boundary

The provider interface receives only a validated command and ordered selected targets. The argv provider expands target values as distinct arguments and delegates to the existing shell-free process boundary. The Nx provider resolves `node_modules/.bin/nx` (including the Windows command wrapper) before PATH `nx`, never invokes a downloading package-runner fallback, uses `nx show projects --json` and `nx show project <project> --json` to validate the declared workspace surface, then executes `nx run-many --target <target> --projects <projects>` plus committed provider arguments. A separately named command can add provider-specific uncached arguments for audit behavior.

Framework plugins remain entirely repository-owned: if they expose the declared projects and target, ZPP can use them; otherwise the repository supplies the plugin, an Nx command target, or an argv command. Alternatives considered were a ZPP-maintained plugin matrix and an Nx trait; both add framework policy to the wrong layer.

### Capability-oriented Behave roots

The suite will move to three stable execution roots: `features/core`, `features/workflow`, and `features/codespaces`. Each root owns its feature files and only the step modules it loads. Shared context, CLI invocation, filesystem fixtures, and assertion helpers move to importable non-step support under `features/support`; decorated steps remain in small capability-named modules within each root's `steps` directory. A structural pytest check enforces root ownership, maximum step-module size, and the absence of decorated steps in shared support.

The repository mapping will expose these roots through an argv-backed `bdd` command and a separate full uncached `bdd-audit` command. Nx configuration may expose the same roots when present, but the committed ZPP mapping will remain usable without Nx. Alternatives considered were tags inside one global root, which retain global step loading and weak cache inputs, and one root per feature file, which creates excessive support duplication.

### Additive default-profile upgrade in the global transaction

The packaged default snapshot remains the source for missing standard entries. Global workflow install and update will preflight the existing persistent default before any selected-agent mutation. If absent, the current packaged default is planned. If valid, only missing packaged trait files and missing trigger keys are planned; existing files and values always win. The merged snapshot is validated before being included in the same rollback-capable mutation plan as agent projections. Local operations and removal do not plan profile writes.

This preserves user ownership while making new packaged traits discoverable. Replacing the whole default was rejected because initialization already promises byte preservation; never upgrading it was rejected because existing global users would not receive newly packaged optional guidance.

### Skill and trait ownership

The workflow bundle gains `zpp-configure-behavior`, bringing the permanent bundle to twelve skills. The skill inspects established repository structure, runs `zpp behave init`, proposes declarative target/impact relationships, writes only `zpp.behave.yaml`, validates through the CLI, and runs the configured `--all` audit. It does not provide executable command text at runtime or own provider behavior. `zpp-wire-feature` gains only a verification handoff: use a configured `zpp behave <command> --all` gate when present, otherwise retain the established BDD runner.

The standard profile gains inactive `bdd-structure-python`, `bdd-structure-ts`, and `bdd-structure-flutter` documents. They express ecosystem structure guidance but have no default triggers. Nx has neither a trait nor a trigger.

## Risks / Trade-offs

- **[Impact maps can become stale]** → Unknown paths select all targets, the explicit skill runs a complete audit after edits, and committed review keeps mappings visible.
- **[Nx CLI output can vary by version]** → Treat JSON discovery as an external compatibility boundary, validate it defensively, and fail clearly rather than silently switching providers.
- **[Capability roots can duplicate step phrases]** → Keep reusable mechanics in non-step support and enforce small root-owned binding modules.
- **[Global profile upgrade spans authored and managed state]** → Preflight and validate the complete plan before mutation and reuse the existing rollback-capable filesystem transaction boundary.
- **[Provider caches can hide invalid inputs]** → Keep audit behavior as a separate repository command whose provider arguments are explicit and reviewable.

## Migration Plan

1. Split the Behave suite into the three roots, modularize bindings and shared support, and enforce the structure before other product implementation.
2. Package the three inactive structure traits and the twelfth workflow skill without activating them.
3. Add behavior configuration, change selection, provider validation, and CLI execution behind the new command group, then add the repository mapping.
4. Add the compatible global default upgrade to workflow install/update and verify atomic failure and idempotence.
5. Install the completed user-global bundle for the selected supported agents and run the configuration skill against this repository.

Rollback removes the new command registration and packaged artifacts and restores the prior feature layout. Workflow removal intentionally does not roll back user-owned default-profile additions.
