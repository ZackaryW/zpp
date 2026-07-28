## Context

`resolve_config(path)` currently resolves governance first, derives one `repo_root`, and reads only `<repo_root>/zpp.toml` as the highest-precedence tier. That is coherent for one-language repositories but makes the CLI's path argument misleading in a monorepo: the path selects governance context, not ordinary configuration scope. Downstream skills compensate by resolving from the Git root and inferring a language from task wording or available tools.

The same `zpp.toml` syntax carries two different kinds of information. `[governance]` and `[profiles.*]` establish or publish authority at the root; sections such as `[tdd]`, `[bdd]`, `[doctor]`, `[traits]`, and `[test-economy]` are ordinary operational configuration. Path scoping must not let a child directory redefine the governing store or published profiles.

The change also introduces zpp's own `learn-zpp` skill. It exists because consumers repeatedly reconstruct zpp semantics from memory, examples, or adjacent plugin behavior. Its value is an evidence workflow and routing map, not a duplicate implementation manual.

## Goals / Non-Goals

**Goals:**

- Make `zpp config resolve <PATH>` reflect ordinary configuration between the resolved governance root and the concrete target.
- Preserve one governance answer and the existing store/workset/repo precedence model.
- Preserve scalar replacement, list union, recursive table merge, and per-leaf provenance.
- Reject authority-bearing sections below the governance root.
- Publish a concise, validated, evidence-first `learn-zpp` skill from zpp as the authoritative source.
- Expose that skill at the root of an automatically maintained distribution branch suitable for a pinned submodule.

**Non-Goals:**

- Creating nested OpenSpec stores or changing `zpp resolve` rule precedence.
- Adding central `[scopes.*]` syntax or glob-based scope matching.
- Adding list reset/removal syntax.
- Moving BDD/TDD behavior into zpp; consumers remain responsible for applying resolved policy.
- Implementing the governance plugin integration in this repository.
- Addressing Saucepan's Rust search projection behavior.

## Decisions

### Separate authority resolution from ordinary config overlays

Governance continues to resolve exactly once using the existing four-mode rules. After the effective repository/governance root is known, config resolution canonicalizes the requested target (using its parent for a file), verifies it lies within that root, and gathers `zpp.toml` files from the root's children toward the target. The root file remains the existing `repo` tier; each descendant file becomes a `scope` tier in shallow-to-deep order.

For a target outside the resolved root, zpp does not borrow overlays across the boundary. This keeps store/workset/isolation authority and lease identity unchanged.

The alternative of treating every nested file as a new governance root was rejected because one monorepo would acquire overlapping authorities. A central `[scopes."path"]` table was rejected because it duplicates filesystem structure and makes independently vendorable subprojects harder to carry.

### Keep merge semantics uniform

Each scoped overlay uses the existing `_merge` behavior: a nearer scalar wins, lists union without duplicates, and nested tables merge recursively. Provenance names the exact scoped file or root-relative directory for every winning leaf. `--sources --json` exposes scoped layers as an ordered collection rather than inventing an unbounded set of fixed top-level tier names.

No reset operator is added. A subtree that needs a different single stack declares a scalar in its nearest file; deliberately cumulative lists remain cumulative.

### Reserve authority sections at the root

A descendant `zpp.toml` containing `[governance]` or `[profiles]` is invalid for scoped resolution. The error names the canonical file and every prohibited section. It is not ignored and is not partially merged. The root file retains its current semantics: top-level ordinary keys form the repo tier, `[profiles.default]` may publish the self-governed store tier, and `[governance]` may bind an external root where applicable.

Failing rather than ignoring was chosen so an owner cannot believe a nested authority declaration is active when it is not.

### Make learn-zpp an evidence and routing skill

`skills/learn-zpp/` is created with the standard skill scaffold, concise `SKILL.md`, matching `agents/openai.yaml`, and selectively loaded references. Its trigger covers explaining, diagnosing, configuring, integrating, or changing zpp and uncertainty about supporting tools when that uncertainty affects a zpp decision.

The workflow establishes this evidence order:

1. Resolve the concrete target with `zpp resolve <PATH> --json` and `zpp config resolve <PATH> --sources --json`.
2. Use live CLI help for command shape.
3. Read the governing OpenSpec capability and current implementation when behavior is being changed or diagnosed.
4. Use authoritative upstream documentation for external-tool facts instead of remembered constraints.
5. Route mutations to the existing bootstrap, OpenSpec, or implementation workflow; the skill itself remains read-only.

Detailed command and concept maps live in one-level references so the loaded skill stays small. It does not reproduce the README wholesale.

### Publish through a deterministic subtree branch

The main-branch directory `skills/learn-zpp/` is authoritative. CI validates it, runs `git subtree split --prefix=skills/learn-zpp`, and advances `dist/learn-zpp` after relevant changes reach `main`. The distribution branch has `SKILL.md`, `agents/`, and any references at its root, allowing another repository to mount it directly at `skills/learn-zpp` as a normal submodule.

The downstream repository still pins a gitlink deliberately; updating the distribution branch does not silently change installed governance policy.

## Risks / Trade-offs

- **[Canonical target traversal could cross a symlink or repository boundary]** → Resolve paths before ancestry checks and never gather a scope file outside the resolved governance root.
- **[Existing nested authority declarations begin failing]** → Emit a precise file-and-section error and document that authority belongs at the resolved root.
- **[List union cannot remove an inherited entry]** → Preserve current semantics deliberately; use scalar selectors for mutually exclusive stacks and defer reset syntax until a demonstrated need.
- **[More filesystem reads per config resolution]** → Read at most one candidate file per ancestor between root and target; typical depth is small and no recursive scan occurs.
- **[Distribution automation could drift or rewrite unexpectedly]** → Validate the skill before splitting, require a deterministic split result, use a dedicated branch, and verify its root layout in CI.
- **[The skill can itself become stale]** → Prefer live commands/specs, keep static explanation minimal, and forward-test it against representative zpp misunderstandings.

## Migration Plan

1. Add fail-first resolver scenarios and unit tests for root-only, nested, inherited, multi-level, prohibited-section, and out-of-root behavior.
2. Implement scoped layer discovery and provenance without changing `zpp resolve`.
3. Update CLI docs and verify existing root-only fixtures remain byte-for-byte compatible where no nested config exists.
4. Scaffold, author, validate, and forward-test `skills/learn-zpp`.
5. Add CI automation for `dist/learn-zpp`, publish its initial split tip, and verify the branch-root skill layout.
6. Land this change before the dependent governance-plugin change advances its submodule.

Rollback removes scoped discovery and the distribution workflow; root configuration behavior remains the compatibility baseline. A published distribution commit stays addressable for any downstream gitlink already pinned to it.

## Open Questions

None. The owner confirmed nested authoring, all-ordinary-section scope, existing merge rules, root-only authority, automatic subtree publication, and coordinated downstream integration.
