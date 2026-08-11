## 1. Settle and Freeze the Runtime Contract

- [x] 1.1 Resolve every item in `Unresolved — Do Not Assume` and reconcile the proposal, design, and four capability deltas before implementation.
- [x] 1.2 Add contract examples and invalid fixtures for the accepted one-family TOML document, selection metadata, binding, facet, evidence, and source-composition shapes.

## 2. Implement TOML Trait Catalogs

- [x] 2.1 Replace the placeholder with the established `core`, `cli`, `artifacts`, and `utils` package boundaries, export `zpp.cli:app`, and add the versioned trait domain model under `core`.
- [x] 2.2 Implement strict TOML decoding for `{name}.toml`, required `[meta].selection`, ordered `[[trait]]` flavors, facet metadata, evidence branches, and required `content.body`.
- [x] 2.3 Implement atomic document validation, duplicate/conflict checks, selection and composition-mode checks, unreachable-flavor diagnostics, and source-oriented errors.
- [x] 2.4 Add focused unit tests covering valid multi-flavor families, complete body preservation, repeated prose, and invalid document rejection.

## 3. Implement Deterministic Resolution

- [x] 3.1 Implement complete facet matching plus accepted `first-win`, `all`, and `extend` selection semantics over effective authored flavor order.
- [x] 3.2 Implement direct-first `first-win` evidence fallback, combined direct/evidence candidates for `all` and `extend`, plus `workspace_contains`, literal `file_contains`, and boolean-producing `which` evaluators.
- [x] 3.3 Implement non-recursive ordered multi-value facet backfill, deduplication, explicit-context precedence, and complete JSON `ZPP_CONTEXT` publication with target/evidence invalidation.
- [x] 3.4 Implement repository-space-global flavor composition, highest-precedence policy selection, explicit `repository-overwrite`, policy-driven selected-body output, inactive results, and deterministic source-aware explanation records.
- [x] 3.5 Add focused unit tests for policy behavior, dominance, source-category ordering, within-category ordering, repository overwrite, scalar and multi-value context, partial facets, conflicts, evidence fallback, non-recursion, source provenance, and explanations.

## 4. Integrate Repository Configuration

- [x] 4.1 Register the `zpp.traits` extension and accepted configuration schema through the current public OpenLease API.
- [x] 4.2 Implement invocation-authorized read-only direct opening plus separately authorized explicit initialization and writes for `.zpp/zpp.toml` and exact `.zpp/traits/{name}.toml` documents in an unregistered repository, without space creation or durable topology mutation.
- [x] 4.3 Implement trait resolution from the exact OpenLease direct documents and repository-path context without ZPP-owned configuration state.
- [x] 4.4 Add integration tests for invocation-triggered read-only opening, no-operation before invocation, missing-document fallback, explicit bounded mutation, conflicts, no-space resolution, and component rejection propagation.

## 5. Consolidate the Workflow Skill

- [x] 5.1 Author one consolidated workflow skill covering the accepted ZPP stages and retaining only dispatch, authority, operation, completion, and handoff rules; package no workflow trait family.
- [x] 5.2 Implement the accepted stage-selection surface and pass stage plus known repository context into trait resolution.
- [x] 5.3 Inventory every reference standard trait and reauthor the applicable BDD structure, BDD operation, TDD, build, dependency, tool, lease, reconciliation, and zero-assumption behavior as complete one-family TOML flavors under `artifacts/traits`, recording any explicit exclusion without imposing that source path at runtime.
- [x] 5.4 Remove all ZPP 1.x stage-skill assumptions and verify that the consolidated skill never accepts trait-granted mutation or completion authority.

## 6. Integrate Agent Router and the Product Surface

- [x] 6.1 Register trait artifact discovery semantics and package the consolidated workflow asset for Agent Router-owned projection.
- [x] 6.2 Implement focused `cli` command modules preserving root `init` and `resolve`, grouped `trait init`, `resolve --explain`, and grouped `workflow install|update|remove`, without flat lifecycle commands or a mirrored OpenLease space lifecycle.
- [x] 6.3 Preserve Agent Router typed selection: ordered/deduplicated repeatable multi-agent input, Codex/Claude Code/Pi/Kimi interactive fallback and cancellation, noninteractive required-selection errors, and optional exactly-one `resolve --agent`.
- [x] 6.4 Add integration tests proving Agent Router-owned install/update/removal behavior and fail-closed projection conflicts.
- [x] 6.5 Document the ZPP 2.0 TOML format, ordered matching, component boundaries, no-space path, and explicit lack of ZPP 1.x migration.

## 7. Verify the Complete Rewrite

- [x] 7.1 Run focused unit and integration suites for trait documents, resolution, OpenLease integration, Agent Router integration, CLI behavior, and workflow assets.
- [x] 7.2 Exercise end-to-end repository bootstrap and workflow trait resolution for representative Python and Flutter flavors.
- [x] 7.3 Validate the complete OpenSpec change and build the ZPP distribution from a clean environment.
