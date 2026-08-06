## Context

See `proposal.md`. The workflow currently enters OpenSpec before it explicitly classifies whether a request changes shipped behavior. Feature shaping also speaks about a complete feature set without defining how that set maps onto established monorepo members. Separately, repository release metadata is maintained by uv while the runtime version constant is duplicated in source.

## Goals / Non-Goals

**Goals:**

- Put request-nature classification before all product bootstrap activity.
- Preserve native feature ownership for every justifiably affected monorepo subproject.
- Keep release automation outside the shipped package while safely synchronizing duplicated release sources.

**Non-Goals:**

- Make environmental tooling a product capability or BDD feature.
- Require every monorepo member to use Gherkin, one test framework, or one runner.
- Infer semantic release level or rewrite arbitrary version mentions.

## Decisions

### Classify observable ownership before product bootstrap

`zpp-clarify-change` will perform an explicit preflight before listing, selecting, or creating product OpenSpec changes. Environmental-only work exits to its native workflow; mixed work is split and only the shipped portion continues through product clarification.

Alternative considered: classify from directory names. Rejected because packaging, generated sources, and shipped artifacts can cross conventional directory boundaries.

### Shape per established affected subproject

`zpp-shape-feature` will discover subproject boundaries from existing repository evidence such as workspace manifests, package descriptors, build files, and native feature roots. Completeness means all accepted behavior across affected members, not a single root-level feature or every member in the repository.

Alternative considered: one umbrella feature set at repository root. Rejected because it erases subproject ownership and can impose an inapplicable framework on other members.

### Use a standalone uv script for release maintenance

`scripts/bump_version.py` will carry PEP 723 metadata with no dependencies and run as `uv run scripts/bump_version.py <X.Y.Z>`. It will preflight the project and runtime declarations, snapshot both plus `uv.lock`, write the two authored sources, run `uv lock`, and restore original presence and bytes on failure.

Alternative considered: `[project.scripts]`. Rejected because official uv semantics make that an installed package CLI, which would incorrectly move repository maintenance into the shipped application surface.

## Risks / Trade-offs

- [Mixed requests are split incorrectly] -> Classify by observable outcome and pause before bootstrap only when ownership remains genuinely ambiguous.
- [Monorepo boundaries overlap] -> Use established native project and feature roots; require a cross-project scenario only for cross-project public behavior.
- [uv lock fails after source writes] -> Restore all three owned files from byte snapshots and surface the failure.

## Migration Plan

Install the revised workflow bundle after release. Run the standalone script once for `0.9.6`, verify the existing product identity scenario, and retain no application CLI entrypoint for release maintenance.
