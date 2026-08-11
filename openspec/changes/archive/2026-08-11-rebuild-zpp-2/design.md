## Context

ZPP 2.0 starts from a placeholder Python package and intentionally rejects the ZPP 1.x implementation as product authority. The separate ZPP checkout remains evidence for the established package architecture, public CLI grammar, and standard workflow behavior that must be deliberately reauthored rather than accidentally discarded. Workflow control remains in one distributed skill while compact environment policy moves into repository-oriented, one-family TOML trait documents. OpenLease supplies repository-scoped configuration without requiring the user to manage a space, and Agent Router supplies agent/plugin discovery and projection.

The central usability constraint is that a human must be able to open one named trait file, read its flavors in source order, and predict which complete instruction bodies an agent will receive. The design therefore favors repeated self-contained flavors and an explicit family-level selection policy over inheritance, provider graphs, recursive derivation, or hidden stage transitions.

## Goals / Non-Goals

**Goals:**

- Represent each trait family as one named TOML document containing ordered, complete flavors with retained bodies.
- Make each family's selection policy explicit and select its result set predictably from known facets or workspace evidence.
- Let evidence-selected flavors report missing facet values without creating recursive activation.
- Replace seven workflow-stage skills with one workflow skill that consumes contextual traits.
- Preserve the established `core`, `cli`, `artifacts`, and `utils` source architecture and the recognizable root-command plus workflow-command-group CLI.
- Reauthor the complete applicable reference standard-trait collection into the new TOML family model.
- Bootstrap and resolve repository traits without creating an OpenLease space.
- Keep OpenLease and Agent Router as the real owners of their respective public responsibilities.

**Non-Goals:**

- Read, migrate, or emulate ZPP 1.x state, skills, profiles, or trait documents.
- Build a capability-provider graph, trait inheritance system, template language, or recursive rules engine.
- Let a trait select or advance a workflow stage, authorize mutation, or claim verification/completion.
- Mirror OpenLease space coordination or Agent Router discovery/projection in ZPP.
- Put repository environment policy into product OpenSpec capability specifications.

## Decisions

### Keep workflow orchestration in one skill

The complete ZPP workflow remains a shipped skill. The seven former `zpp-flow-*` stage skills are consolidated into that one entry point rather than translated into a workflow trait. The skill owns dispatch, stage context, required operation handoffs, mutation authority, and truthful completion. Resolved trait bodies specialize the current stage for the repository's language, framework, test framework, build tool, and other environment facets.

This preserves one inspectable operational authority while allowing repository policy to vary independently. There is no packaged `workflow.toml` or other workflow trait family. A trait cannot grant the skill new authority or mark a stage complete. A non-workflow trait flavor may constrain itself by the explicit `stage` facet when its environment guidance is relevant only during that stage, but stage semantics and stage transitions remain entirely in the skill.

### Preserve the established package boundaries

The shipped Python package retains four primary boundaries from the established ZPP architecture:

- `zpp.core` owns immutable domain models, validation, composition, evidence results, context precedence, resolution, and application-level orchestration.
- `zpp.cli` owns the Typer application and focused command modules; it does not contain trait semantics or component reimplementations.
- `zpp.artifacts` owns access to the consolidated skill and the standard workflow TOML source assets.
- `zpp.utils` owns bounded filesystem/process helpers and thin OpenLease and Agent Router adapters used by core application services.

Root-level runtime modules that bypass these boundaries were rejected because they make the public application surface and component ownership difficult to predict. The separate reference checkout is architectural evidence, not code to copy wholesale or a compatibility dependency.

### Preserve the CLI grammar and typed agent selection while changing the engine

The Typer application remains exported as `zpp.cli:app`, keeps `--version`, and retains root `init` and `resolve` plus the `workflow install|update|remove` group. Exact repository document creation is `trait init`, not the flat `init-trait` command and not an overload of root `init`. `resolve` accepts the target directory, an explicit workflow stage when invoked for workflow guidance, optional selected-space context, and an explanation flag on the same operation. It does not add a separate `explain` command. Workflow lifecycle commands retain target/global scope and agent selection while delegating destination behavior to Agent Router. ZPP does not expose `install-workflow` and does not mirror OpenLease's space lifecycle.

CLI agent parameters use Agent Router's `Agent` enum directly. Explicit multi-agent input is repeatable, preserves the caller's first-seen order, and deduplicates repeated values. When a command requires one or more agents and none are supplied, an interactive terminal presents Codex, Claude Code, Pi, and Kimi in that order; cancellation aborts before mutation, while noninteractive omission is an error. `resolve --agent` is optional and accepts at most one agent because it selects one invoking agent's active artifact context. ZPP does not silently broaden one-agent selection to every installed agent or create stringly typed agent aliases that bypass Agent Router validation.

### Reauthor the complete standard behavior collection

Packaged global traits live directly under `zpp/artifacts/traits/` as one TOML document per logical family. This source layout is only a distribution boundary; OpenLease and Agent Router may present an effective collection without reproducing an `artifacts/traits` path at runtime. The reference Markdown collection is inventoried and translated behavior-by-behavior. Related documents become self-contained flavors where the new family model adds value:

- Python, Flutter, and TypeScript BDD structure become flavors of `bdd-structure.toml`.
- Python, Flutter, and TypeScript BDD operating guidance become flavors of `bdd.toml`.
- Python, Django-specialized Python, Flutter, and TypeScript TDD become `tdd.toml` flavors selected with `extend` semantics.
- BDD verification modes become complete ordered flavors in `bdd-workflow.toml`.
- Python package build remains a build family flavor; tool preferences may combine under an `all` tooling family.
- Dependency proportionality, lease completeness, lease conflict handling, reconciliation, and zero-assumption policy remain focused families unless a complete-behavior review proves a safe grouping.

Automatic progression and workflow authority move into the consolidated skill rather than becoming `workflow` trait flavors. Every applicable reference behavior must be accounted for by a new family/flavor or an explicit documented exclusion; generic replacement paragraphs are insufficient.

### Model one trait family per TOML document

The basename of `{name}.toml` identifies one trait family. Its `[meta]` table declares `selection`, and repeated `[[trait]]` entries define the family's ordered flavors. Each flavor retains a required `[trait.content]` table with a complete `body`. A flavor may declare `[trait.facet]` values and one or more `[[trait.when]]` evidence branches.

Flavors deliberately repeat complete prose when ecosystems need slightly different wording. ZPP does not inherit, splice, or template one flavor body from another. The TOML parser supplies structural decoding; ZPP validates the product schema and reports the trait document and flavor location for invalid input.

For example:

```toml
[meta]
selection = "extend"
# Optional. The default is layered composition.
mode = "repository-overwrite"

[[trait]]
[trait.facet]
language = "python"
[trait.content]
body = """Complete Python guidance."""

[[trait]]
[trait.facet]
language = "python"
build_tool = "uv"
[trait.content]
body = """Complete Python and uv guidance."""
```

### Resolve with an explicit family selection policy

For each effective trait family, resolution finds flavors whose complete declared facet set matches the input context. A scalar flavor constraint matches the equal scalar context value or a member of a multi-value context facet. The file's `[meta].selection` policy determines the retained result: `first-win` retains the first matching flavor, `all` retains every matching flavor, and `extend` removes a matching flavor when another match contains all of its facet constraints plus at least one additional constraint. Thus Python-and-uv supersedes generic Python while an independently matching Flutter flavor remains selected.

For `first-win`, a direct facet match still takes precedence over evidence fallback. For `all` and `extend`, directly matching flavors and compatible flavors whose `when` evidence succeeds form one candidate set before the selection policy is applied. A flavor is compatible only when none of its declared facets conflicts with known context.

Each selected evidence-backed flavor contributes its missing facet values to the resolution result. Equal contributed values are deduplicated; distinct values for the same missing categorical facet become an ordered list following retained flavor order. Evidence cannot overwrite or expand an explicit conflicting value, and the resolver does not restart selection after backfill. Flavor constraints remain scalar strings; repository and invocation context facets may be scalar strings or non-empty lists of distinct strings. The `which` predicate additionally records executable availability as a boolean `has_<tool>` runtime facet. This gives agents useful runtime context without introducing an order-sensitive recursive fact engine.

### Compose sources in repository, space, global order

For a trait family contributed by several OpenLease sources, files with the same basename contribute to the same effective family. ZPP orders contributions by repository, then space, then global, while preserving the established order within each category and authored flavor order within each document. The highest-precedence contributing document's `[meta].selection` becomes the effective family policy. Under `first-win`, matching therefore scans repository flavors before space flavors and space flavors before global flavors.

The optional repository declaration `[meta] mode = "repository-overwrite"` changes composition for that family: ZPP uses only the repository document and excludes every space and global contribution before matching. This is an explicit ZPP 2.0 declaration replacing legacy implicit overwrite behavior. Omitting `mode` uses layered composition. `repository-overwrite` is invalid outside a repository contribution.

The effective explanation must display the effective policy and its source, composition mode, source boundaries, excluded contributions, and flavor order because source position affects `first-win` and equal-facet ties. `extend` uses declared facet-set dominance rather than a numeric specificity score.

### Load known facets from repository and session context

Repository-known facets are authored beneath `[facet]` in `.zpp/zpp.toml` as strings or non-empty lists of distinct strings. The workflow supplies its explicitly requested stage separately, and `ZPP_CONTEXT` carries stored session context as one compact JSON object between invocations. The object contains facet values, value provenance, selected target identity, and relevant evidence fingerprints. Resolution combines these sources without allowing stored or backfilled values to replace explicit repository or invocation values, then returns a complete replacement value for publication by the supported session integration.

A child process does not mutate its parent's environment. The host/session integration therefore publishes the returned complete `ZPP_CONTEXT` value at its supported boundary. A target-identity mismatch invalidates the stored context, and changed evidence invalidates the affected evidence-derived values rather than silently retaining them.

### Keep evidence predicates small and observable

The initial evidence surface contains `workspace_contains`, literal `file_contains`, and the retained `which` executable check. A leading `/` in a workspace pattern anchors it to the selected target root. `file_contains` names its file explicitly and performs literal matching. Evaluating `which = "uv"` records `has_uv` as a boolean and uses executable availability as that predicate's truth value.

### Require explicit workflow stages

The consolidated skill requires the requested stage as an explicit action rather than inferring it from OpenSpec status, files, or prior trait output. It supplies that stage to trait resolution as invocation context. Automatic end-to-end continuation, when separately authorized, remains a visible sequence of explicit stage actions rather than a hidden stage transition.

### Preserve bodies as first-class content

Every selected flavor returns its complete `content.body`; structured metadata does not replace the authored instruction. ZPP preserves each body as authored rather than generating it from facet values or configuration. Future structured content fields may coexist with `body`, but the body remains the stable human-readable policy surface.

### Delegate repository context and agent integration

Explicitly invoking the workflow against a selected repository authorizes read-only opening of its existing `.zpp/zpp.toml` and `.zpp/traits/{name}.toml` documents through OpenLease's invocation-scoped direct document contract with repository-path provenance. Mere file presence outside an invocation performs no operation. Missing repository documents are not created implicitly; resolution continues with available space and global contributions. Creating or modifying a repository document requires a separate explicit command scoped to that exact document.

These operations do not require durable repository registration and neither create nor select an OpenLease space, topology record, lease, or persistent configuration source. Explicit space coordination, when separately requested, remains an OpenLease concern rather than a prerequisite for ordinary repository traits.

Agent Router discovers supported agent/plugin artifacts and owns projections into agent destinations. ZPP registers its trait artifact semantics, validates and resolves current inputs, and supplies the consolidated workflow asset without rediscovering or directly projecting agent state.

## Risks / Trade-offs

- [A broad early flavor shadows a later specific flavor under `first-win`] → Preserve visible source order, explain every rejected/selected flavor, and detect obviously unreachable flavors during validation.
- [A higher-precedence flavor unexpectedly shadows an inherited flavor] → Prepend by explicit OpenLease source order and show every source boundary and flavor decision in explanations.
- [A repository unintentionally loses packaged or space flavors] → Layer by default and exclude inherited contributions only through the repository's explicit `repository-overwrite` declaration.
- [Several `extend` winners contain overlapping or contradictory complete bodies] → Keep dominance mechanical and explanations complete; authors remain responsible for making incomparable flavors safe to combine.
- [Stored session facets become stale across repository changes] → Carry target identity and evidence fingerprints in `ZPP_CONTEXT`, ignore mismatched targets, and invalidate evidence-derived values whose evidence changed.
- [Literal file-content filters produce false positives] → Keep the predicate explicit and expose its matched file and literal evidence in resolution explanations.
- [One consolidated workflow skill becomes another monolith] → Keep repository/platform policy in traits and retain in the skill only dispatch, hard authority, operation boundaries, and completion rules.
- [Repository-authored instructions are loaded unexpectedly] → Load them only during an explicit workflow invocation against that repository, keep the operation read-only, and expose document provenance in resolution explanations.
- [Higher configuration flexibility becomes difficult to explain] → Require deterministic policy-driven output with source, flavor, facet, dominance, and evidence provenance.

## Migration Plan

1. Establish ZPP 2.0 trait-document, resolution, bootstrap, and workflow contracts without importing ZPP 1.x files or state.
2. Implement and distribute only the new consolidated workflow asset and TOML trait format.
3. Document ZPP 1.x as unsupported input requiring independent removal rather than automatic conversion.
4. Roll back by removing the new ZPP 2.0 installation and repository binding; no legacy state is restored.

## Open Questions

None.
