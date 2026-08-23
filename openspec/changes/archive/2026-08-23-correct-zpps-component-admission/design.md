## Context

See [proposal.md](proposal.md) for motivation. ZPP currently packages twenty `zpps-*` components. Agent skill selection sees each frontmatter `description` before it reads the selected skill body, so admission policy that appears only inside a body cannot prevent the initial mismatch. Several mutating descriptions emphasize their eventual effect while allowing read-only discovery inside the procedure; that makes a request such as “adopt these packages after checking published versions and recent integration changes” look like apply work even though its immediate unresolved operation is exploration.

The canonical `consolidated-workflow-skill` capability owns component identities, bounded procedures, and routing authority. The older active `route-workflow-playbooks` planning set describes superseded identities and kernel dispatch behavior, so it is evidence of the earlier design but not the target contract for this correction.

## Goals / Non-Goals

**Goals:**

- Make initial discovery metadata sufficient to distinguish evidence discovery from a resolved mutation.
- Apply one admission precedence across every packaged `zpps-*` component and every playbook that selects one.
- Preserve each component's existing bounded procedure, authority requirements, and stopping boundary after correct admission.
- Make a detected mismatch a visible failed admission before any new operation begins.

**Non-Goals:**

- Add a runtime router, compatibility alias, or hidden stage dispatcher.
- Change AppBuilder, OpenSpec CLI, Bundler lease semantics, or component implementation procedures unrelated to admission.
- Treat an OpenSpec change or pending task as implicit mutation intent.
- Add Gherkin that asserts packaged Markdown wording or simulates agent judgment without a public-system observation.

## Decisions

### Put the admission capsule in both discovery metadata and the procedure entry

Every `zpps-*` frontmatter description will identify the exact immediate operation it accepts and distinguish read-only, conditionally mutating, mutating, or guard-only effect. The opening procedure will enforce the same boundary before its normal target discovery. This duplication is deliberate: metadata governs selection, while the body governs conduct after selection.

The alternative—keeping the rule only in `zpp-auto`, the kernel, or a shared reference—cannot prevent direct skill selection and is invisible until after the wrong skill has already been loaded. The component bodies remain substantive and do not delegate admission to the kernel.

### Use readiness-first precedence

Admission uses this order:

1. Identify the immediate bounded operation and the evidence it requires.
2. If required external or repository facts are unresolved, admit `zpps-explore` for that exact question and retain read-only effect.
3. If the operation is resolved, admit its exact read-only component, or admit its exact mutating component only with explicit mutation intent or exact active-playbook configuration.
4. If read versus write remains material and unresolved, use exploration when evidence can resolve it; otherwise ask one focused clarification.

An eventual mutation, imperative wording, active change, or pending task can provide context but cannot skip an earlier evidence operation. Exact playbook configuration is an admission source, not permission to ignore the configured component's prerequisites or authority checks.

### Apply the policy to the complete component inventory

The implementation audit covers all twenty packaged identities rather than patching only `zpps-apply-change` and `zpps-explore`:

- Read-only discovery and reconciliation: `zpps-explore`, `zpps-clarify`, `zpps-finalize`, `zpps-verify-change`, and `zpps-verify-repository`.
- Conditionally mutating work: `zpps-planning-ponytail` and `zpps-form-specs`, whose read-only modes remain admissible without mutation authority while writes require explicit intent/configuration and their existing guard.
- Mutating planning, behavior, implementation, synchronization, and archival work: `zpps-new-change`, `zpps-continue-change`, `zpps-ff-change`, `zpps-propose-change`, `zpps-update-change`, `zpps-apply-change`, `zpps-shape-bdd`, `zpps-mature-utilities`, `zpps-wire`, `zpps-sync-specs`, `zpps-archive-change`, and `zpps-bulk-archive-change`.
- Guard-only lifecycle assessment: `zpps-workflow-kernel`, which accepts only a caller-selected exact action and never chooses a component.

Playbooks will be audited at each explicit component-selection branch so their custom instructions use the same readiness-first precedence. No component may invoke the suggested replacement when it detects a mismatch.

### Return a mismatch before continuation

A misselected component will identify the admitted component, the observed immediate operation, and why they conflict, then stop with a failed admission. It may name the required separately selected operation, but it cannot invoke that operation or claim a stage result. A caller or active playbook may subsequently select the correct component under its existing authority.

This makes the failure visible before any procedural status, task ordering, or repository findings can obscure it. Silently switching components was rejected because it hides selection defects and lets a subordinate component choose workflow continuation.

### Keep acceptance authority in the specification

This correction changes packaged skill guidance, not an executable ZPP runtime selector. The supplied conversation is the relevant observed RED for the current metadata: a discovery request was admitted as apply work. Because the repository has no deterministic public agent-selection boundary, implementation will not add a wording assertion, recording-only binding, or capability-wide pseudo-check. Existing skill parsing/Agent Router validation and the independently runnable consolidated workflow feature remain regression gates for packaging; semantic satisfaction is assessed against this delta and the actual revised skill set.

If a deterministic public selector is introduced by a later accepted change, that capability can own executable scenario selection. This change does not invent one merely to make prose look executable.

## Risks / Trade-offs

- [Longer descriptions may reduce discovery clarity] → Keep each capsule concise and component-specific, then validate every skill through the existing packaged-skill loader and Agent Router validation.
- [Repeated admission language may drift] → Audit the complete twenty-component inventory and all playbook selection sites in one task, using the delta requirement as the single semantic authority.
- [Exploration precedence could delay an obvious mutation] → Apply it only when facts necessary to choose or execute the bounded operation are unresolved; resolved explicit mutations remain directly admissible.
- [A component may detect mismatch after harmless reads] → Require reporting and stopping as soon as the mismatch is detected, preserve any reads as evidence only, and do not represent them as component success.
- [The older routing change can appear contradictory] → Verify against the current canonical capability and flag the historical change for separate maintenance rather than editing or reviving it here.

## Migration Plan

1. Capture the representative package-integration request as the current failed-admission evidence and inventory every `zpps-*` discovery description and selection site.
2. Update the complete packaged component family and playbook selection guidance under the new precedence without changing component identities or runtime authority.
3. Validate packaging and semantic coherence, run the consolidated workflow capability root independently, and run the repository's complete declared gates.
4. Reconcile this delta into the canonical capability only through the later selected specification-formation/synchronization operations.

Rollback is the normal source revert of the packaged skill edits and this change's implementation commit; there is no data or compatibility migration.
