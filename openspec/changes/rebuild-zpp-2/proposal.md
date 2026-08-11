## Why

ZPP 1.x hard-coded a large seven-skill workflow and coupled repository policy to product-owned orchestration, limiting how humans and agents could adapt the workflow without creating new skills or duplicating component responsibilities. ZPP 2.0 will replace that system with one consolidated workflow skill and small repository-authored TOML traits selected through explicit facets and workspace evidence.

## What Changes

- **BREAKING** Rebuild ZPP from the new repository without reading, migrating, or preserving ZPP 1.x profiles, trait documents, workflow skills, state, or compatibility behavior.
- Define one TOML document per trait family at `{name}.toml`; its `[meta]` table declares the family selection policy and its ordered `[[trait]]` flavors each retain a complete `content.body`, declare selectable facets, and may declare workspace-evidence branches.
- Compose same-basename trait documents in repository → space → global order, including the established ordering within each category. The highest-precedence contributing document supplies the effective selection policy. An explicit repository `mode = "repository-overwrite"` discards space and global contributions for that family instead of relying on legacy overwrite behavior.
- Resolve matching flavors according to the trait file's explicit selection policy: `first-win` retains the first match, `all` retains every match, and `extend` retains the non-dominated most-specific matches. For multi-winner policies, compatible evidence-backed flavors join direct matches before selection; selected evidence flavors backfill missing values, combining distinct categorical values into ordered lists without recursively rerunning resolution.
- Read repository-known scalar or multi-value string facets from `.zpp/zpp.toml`, carry backfilled runtime context through a complete JSON `ZPP_CONTEXT` session environment value with target/evidence provenance, and let `which` evidence publish a boolean `has_<tool>` facet.
- Replace the seven packaged `zpp-flow-*` skills with one consolidated workflow skill. The skill is the only packaged workflow definition and owns stage behavior, dispatch, user/session mutation authority, and truthful completion. ZPP SHALL NOT package a `workflow` trait family; selected traits remain advisory environment, language, framework, test, build, tool, and coordination policy.
- Translate the complete applicable standard-trait behavior from the separate reference repository into `artifacts/traits/{family}.toml`, grouping related reference traits as self-contained flavors without silently omitting or replacing their behavior with generic prose. This is source-guided reauthoring for ZPP 2, not a ZPP 1.x compatibility reader; the packaged source path is not a required runtime collection layout.
- An explicit workflow invocation against a repository authorizes read-only opening of existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents through invocation-scoped OpenLease contexts without creating or selecting a space or requiring durable repository registration. Creation and modification require a separate explicit command, and OpenLease remains the owner of bounded configuration access.
- Use Agent Router for agent/plugin discovery and projection. ZPP owns trait schema, matching, resolution, and rendering but does not recreate OpenLease coordination or Agent Router discovery behind a compatibility layer.
- Preserve the established public CLI grammar and exact Agent Router agent-selection behavior: root `init` and `resolve`, grouped `trait init`, plus `workflow install`, `workflow update`, and `workflow remove`. Add stage and explanation controls to `resolve` instead of inventing `install-workflow` or a standalone explanation command.
- Keep OpenSpec planning and specifications limited to shipped product behavior; repository-authored trait content remains repository environment policy outside product capability deltas.

## Capabilities

### New Capabilities

- `toml-trait-catalog`: Defines one-family TOML trait documents, explicit selection metadata, ordered flavors, facets, `when` evidence, complete content bodies, validation, and source layering.
- `trait-resolution`: Defines deterministic policy-driven selection, facet backfill, non-recursive resolution, output, and explanation behavior.
- `consolidated-workflow-skill`: Defines the single distributed workflow skill, its responsibility boundary, explicit stage dispatch, and consumption of resolved traits.
- `repository-trait-bootstrap`: Defines repository-local trait initialization and OpenLease/Agent Router integration without requiring an OpenLease space.

### Modified Capabilities

None. This repository has no canonical ZPP 2.0 specifications.

## Impact

- Replaces the current ZPP 2.0 placeholder while retaining the established `core/`, `cli/`, `artifacts/`, and `utils/` package boundaries and command-group organization as architectural constraints.
- Introduces TOML parsing and validation for repository and distributed one-family trait documents.
- Adds direct dependencies on the current public OpenLease and Agent Router contracts while keeping their ownership boundaries intact.
- Removes the ZPP 1.x multi-skill distribution model rather than migrating it.

## Unresolved — Do Not Assume

None.
