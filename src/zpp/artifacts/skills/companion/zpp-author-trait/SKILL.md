---
name: zpp-author-trait
description: Author or revise one repository ZPP TOML trait family with explicit activation, selection, facets, observable evidence, complete flavor bodies, layering, and resolution validation. Use when a user asks to create, configure, review, or repair a .zpp/traits/{family}.toml document.
---

# Author a ZPP trait

Operate only for an explicit trait-authoring request. Author repository behavior
policy, not workflow stages, executable commands, callbacks, or completion
claims. A Clarify result that identifies a repository-context gap is evidence, not
an authoring request, and does not independently admit this mutation.

## Establish the family contract

1. Resolve the containing Git worktree and the requested family name. One file
   `.zpp/traits/{family}.toml` defines the basename-derived family.
2. Inspect that document, `.zpp/zpp.toml`, and relevant effective repository
   evidence before editing. Preserve other families.
3. Set `[meta].selection` deliberately:
   - `first-win`: retain the first eligible flavor in repository, selected
     space, global, then authored order.
   - `all`: retain every eligible flavor in effective order.
   - `extend`: retain incomparable eligible flavors and remove a generic match
     dominated by a matching strict facet superset.
4. Set `[meta].activation` deliberately:
   - `automatic`: participate in common resolution through normal matching.
   - `manual`: participate only when the family is named explicitly.
   - `always-run`: bypass activation matching while still applying selection.
5. Use `[meta].mode = "repository-overwrite"` only when the owner explicitly
   wants this repository document to replace space and global contributions.
   Otherwise keep layered composition.

## Author complete flavors

- Write each `[[trait]]` as an independently understandable flavor with its own
  complete `[trait.content].body`. Do not use inheritance, fragments, templates,
  providers, or content assembled from another flavor.
- Put descriptive constraints already known in the resolution context under
  `[trait.facet]`. Facet values in a flavor are non-empty strings.
- Put observable repository predicates under `[[trait.when]]`:
  `workspace_contains`, literal `file_contains = { path = ..., text = ... }`,
  and `which`. Predicates within one branch are AND; repeated branches are OR.
- Use root-anchored `/path` evidence when only a worktree-root entry is valid.
- Let successful evidence backfill the flavor's missing facet values for the
  bounded resolution pass. `which = "tool"` also publishes `has_tool` as a
  boolean fact. Do not persist derived values to `.zpp/zpp.toml` implicitly.
- Order `first-win` flavors from specific to general and avoid an earlier
  unconditional flavor that makes later flavors unreachable.
- Keep trait bodies advisory. They cannot authorize mutation, run a process,
  select or skip a workflow stage, or establish verification success.

Use this as a structural example:

```toml
[meta]
selection = "extend"
activation = "automatic"

[[trait]]
[trait.facet]
language = "python"
[trait.content]
body = "Complete guidance for an established Python repository."

[[trait]]
[trait.facet]
language = "python"
build_tool = "uv"
[[trait.when]]
workspace_contains = "/pyproject.toml"
which = "uv"
[trait.content]
body = "Complete Python and uv guidance without relying on another flavor."
```

## Initialize and validate

1. If the family is absent, run `zpp trait init FAMILY TARGET` to create only
   that repository document, then replace the scaffold body completely.
2. Resolve the family directly with `zpp resolve TARGET --trait FAMILY
   --explain`. Supply representative `--facet NAME=VALUE` inputs when testing
   known context; use real worktree evidence for `when` branches.
3. Inspect selected and rejected flavors, effective order, dominance, derived
   context, provenance, and unmatched behavior. Test more than one context when
   the document has multiple meaningful flavors.
4. For a `manual` family, verify common resolution excludes it and direct named
   resolution still applies normal matching. An unmatched manual family returns
   no forced body.
5. For an `always-run` family, verify activation bypass and the declared
   selection result independently.
6. Report the exact file, family policy, tested contexts or evidence, selected
   bodies, and any unresolved owner choice.
