## Context

See `proposal.md`. Typer registers the public command group in the CLI adapter, while the existing core and utility layers model workflow-skill bundle operations without depending on the group name.

## Goals / Non-Goals

**Goals:**

- Rename the public group at the CLI boundary.
- Keep lifecycle behavior and the established domain utility graph unchanged.
- Keep the old name unavailable rather than maintaining two public paths.

**Non-Goals:**

- Renaming internal concepts that accurately refer to packaged skills, skill projections, or `skill_lookup`.
- Packaging standard traits with the workflow bundle; that is a separate product change.
- Introducing migration aliases or deprecation handling.

## Decisions

- Register one Typer group named `workflow` and retain the existing `install`, `update`, and `remove` operations beneath it.
- Rename CLI-local helpers and diagnostics where they describe the public lifecycle, while leaving core skill-bundle types and utilities unchanged.
- Bind the complete existing workflow-distribution Gherkin set to the new command path and explicitly verify that root help no longer exposes `skill`.

The rejected alternative was a compatibility alias. It would preserve the generic interface that the owner explicitly replaced and make the command surface ambiguous.

## Risks / Trade-offs

- [Existing callers of `zpp skill` break immediately] → Treat the rename as an explicit breaking change and expose the replacement consistently in help and canonical contracts.
- [Mechanical renaming could alter actual skill-domain terminology] → Restrict the rename to the public CLI path, corresponding diagnostics, and executable bindings.

## Migration Plan

Existing callers replace `zpp skill` with `zpp workflow`; subcommands, arguments, and options remain unchanged.
