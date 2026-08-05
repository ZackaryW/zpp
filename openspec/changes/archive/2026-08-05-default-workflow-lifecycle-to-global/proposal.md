## Why

The workflow lifecycle currently defaults to repository-local projection and requires `--global` for the complete user-level installation. That default makes the normal invocation easy to misread and can leave an agent without its global workflow skills and lifecycle hooks.

## What Changes

- **BREAKING** Make user-global scope the default for `workflow install`, `workflow update`, and `workflow remove`.
- **BREAKING** Replace the workflow lifecycle's `--global` scope selector with an explicit `--local` selector for repository-local operations.
- Require `--local` for every repository-local lifecycle invocation. With no target it uses the current repository; with a target it uses that exact repository directory. A positional target without `--local` is invalid.
- Preserve the established global outcome: installation creates missing native global skill directories, installs the managed ZPP workflow bundle, reconciles native hooks, and bootstraps version-matched OpenSpec operation skills.
- Preserve local-only controls in local scope: compatible-global deduplication and `--force`, plus explicit `--with-openspec` bootstrap.
- Reject contradictory scope and target combinations before mutation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-skill-distribution`: Invert workflow lifecycle scope selection so global is the default and repository-local scope requires `--local`.

## Impact

- Changes the public CLI and help for `zpp workflow install`, `update`, and `remove`.
- Changes lifecycle scope parsing, validation, tests, executable examples, and README usage.
- Existing scripts using `--global` must migrate; unqualified lifecycle invocations change from local to global.
- Native skill destinations, managed ownership, atomicity, and OpenSpec generation mechanisms remain unchanged.
- `zpp init` remains the established global user-state and native-hook setup command; this change applies to the `workflow` lifecycle only.

## Unresolved — Do Not Assume

None.
