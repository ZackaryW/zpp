## Context

See `proposal.md` for motivation. Bundler intentionally accepts only paths beneath registered `openspec/` roots, while ZPP's kernel currently reports a component's complete changed-path inventory directly to that API. Separately, the decomposed workflow correctly moved scenario sequencing into `zpp-*` Markdown playbooks, but it did not preserve the former workflow's distinct stage-assessment contract. Complete playbooks now combine utility planning and maturation in one section and can treat one inferred skip as permission to reach wiring without separate stage results.

## Goals / Non-Goals

**Goals:**

- Keep Bundler's OpenSpec authority boundary strict while preventing repository-local product files from becoming false lease violations.
- Preserve complete changed-path reporting by components and centralize classification in ZPP's Python runtime.
- Keep `zpp-*` skills responsible for scenario-specific workflow execution and `zpps-*` skills responsible for reusable stage procedures.
- Require every stage to execute as a distinct visible action with a same-revision pre-action assessment and observed result.
- Add structural validation for each complete workflow's full stage-component sequence without restoring stage selection to the kernel.

**Non-Goals:**

- Broaden Bundler leases to application, feature, or test files.
- Ignore paths outside registered repositories or OpenSpec paths owned by unheld stores.
- Add persisted workflow state, a monolithic stage dispatcher, or compatibility for the superseded `route-workflow-playbooks` design.
- Infer stage applicability in `zpp-auto`, a complete workflow, or the kernel.

## Decisions

### Classify paths in the ZPP adapter before Bundler audit

`BundlerLeaseService` will own a ZPP result containing `audited`, `ignored`, and `violations`. It will resolve registered store roots most-specific-first, classify paths outside all roots as violations, classify paths inside a registered root but outside its `openspec/` subtree as ignored, and forward the remaining OpenSpec paths to `LeaseCoordinator.audit`. Bundler remains unchanged and authoritative for held-store validation.

Filtering in the kernel skill was rejected because every agent would have to reproduce filesystem and nested-store logic. Changing Bundler was rejected because its package contract is explicitly OpenSpec-only.

### Keep the CLI backward-readable while exposing ignored paths

`zpp lease audit` will retain `ok`, `accepted`, and `violations`, with `accepted` representing Bundler-audited OpenSpec paths, and add `ignored` for repository-local paths outside lease scope. Existing consumers that read the original fields continue to work, while workflow assessment gains explicit evidence that a path was classified rather than lost.

### Preserve scenario workflows and reusable stages

Each `zpp-*` playbook owns the complete sequence and branches for its scenario. Each `zpps-*` skill remains a reusable procedure for one stage or bounded operation and returns only its own observed result. `zpp-auto` will make same-invocation transfer explicit so a handoff acknowledgement cannot terminate triage successfully.

This preserves caller-owned sequence selection: the active `zpp-*` workflow chooses its next declared action, while the kernel validates only that selected action and never chooses or invokes a stage. Reintroducing the superseded kernel dispatcher was rejected because it would conflict with the current complete-playbook architecture.

### Restore distinct visible stage assessments

Before each selected stage, the workflow will supply the kernel with the current contract revision, selected stage and component, complete ordered predecessor outcomes, invalid or stale evidence, accepted effect classes, stage-owned output, and authority. After the stage, the kernel will assess its actual result, verification, changed paths, and checkpoint evidence. Each assessment applies only to that caller-selected stage.

`plan-utilities` and `mature-utilities` will be separate visible actions. A `zpps-planning-ponytail` skip is only the planning result; it does not manufacture a maturation result or directly authorize wiring. `zpps-mature-utilities` must independently return `completed` or an evidence-backed `skipped: not applicable` for the same revision before wiring is eligible.

### Validate the complete stage sequence, not arbitrary prose

The packaged workflow loader will derive normalized explicit stage-component uses from numbered playbook sections and validate that every complete workflow declares the ordered sequence `zpps-clarify`, `zpps-shape-bdd`, `zpps-planning-ponytail`, `zpps-mature-utilities`, `zpps-wire`, `zpps-form-specs`, and `zpps-finalize`. Missing, collapsed, or reversed stages will fail packaging. `zpp-auto` remains a triage-only exception but must name every complete handoff target. This validates workflow structure; kernel assessments validate execution evidence.

## Risks / Trade-offs

- [Registered roots may be nested] → Resolve the most-specific root before classifying the OpenSpec boundary, matching Bundler ownership semantics.
- [An ignored path could conceal an unauthorized repository] → Ignore only paths beneath a known registered root; unknown roots remain violations.
- [Prompt execution can still fail outside ZPP's runtime] → Require visible per-stage assessments and full same-revision predecessor evidence at the kernel boundary.
- [Markdown parsing can become brittle] → Parse only normalized explicit stage-component uses in numbered playbook sections and test missing, collapsed, and reversed stages independently of narrative text.

## Migration Plan

1. Shape a public audit regression in `features/openspec_bundler_integration/` and focused structural utility failures in unit tests.
2. Implement ZPP path classification and expose ignored-path evidence through the CLI.
3. Implement and validate full structural stage-component extraction and ordering.
4. Update `zpp-auto`, complete workflows, stage skills, and the kernel to require same-invocation handoff and distinct visible stage assessments.
5. Run focused BDD/unit targets, the complete repository gates, synchronize canonical specs, and archive only with explicit authority.
