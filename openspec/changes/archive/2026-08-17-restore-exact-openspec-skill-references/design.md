## Context

ZPP installs six OpenSpec-generated skills with stable names, and the provisioning specification already treats that exact inventory as product authority. The consolidated workflow specification and packaged `SKILL.md`, however, delegate only to “the installed skill that owns the OpenSpec operation.” The authority boundary is correct but the usable identities and operation distinctions are missing.

The workflow also requires an explicit current stage and stage-specific completion evidence, but does not prescribe one visible eligibility assessment before executing the requested stage. That gap permits a named or agent-proposed later stage to be treated as though its predecessor gates were already satisfied.

This is a spec-governed artifact correction. It changes agent-facing workflow instructions and their canonical requirements, but it creates no executable public-system behavior.

## Goals / Non-Goals

**Goals:**

- Put the exact six skill identities at the workflow's component-delegation boundary.
- Distinguish the operation owned by each installed skill.
- Keep the generated skills subordinate component integrations rather than ZPP workflow stages.
- Keep shipped prose and canonical authority synchronized.
- Make stage eligibility an explicit evidence assessment rather than an implication of the requested stage name.
- Select conditional-stage work from accepted observable and executable effects rather than filenames or artifact categories.
- Prevent a later stage from executing while any predecessor outcome is missing, stale, failed, or based on a superseded contract.

**Non-Goals:**

- Change the six-skill inventory, generation, installation, or projection order.
- Rename or alias any skill.
- Assign one OpenSpec skill mechanically to each ZPP stage.
- Change runtime code, CLI behavior, Gherkin, utilities, dependencies, or verification providers.
- Let an assessment authorize mutation, verification success, or automatic stage invocation by itself.

## Decisions

**List the six identities inline at the existing delegation boundary.** The packaged workflow will identify `openspec-explore` for exploration, `openspec-propose` for creating a change and its planning artifacts, `openspec-update-change` for revising existing planning artifacts, `openspec-apply-change` for implementing change tasks, `openspec-sync-specs` for synchronizing delta specifications without archival, and `openspec-archive-change` for archiving a completed change. This makes selection actionable while matching the inventory already governed by `openspec-skill-provisioning`.

An alternative was to reference the provisioning specification or say “one of the six skills.” That preserves a single inventory declaration but does not help an acting agent select an exact installed skill, which is the defect being corrected.

**Describe operation ownership rather than stage aliases.** Several ZPP stages can revise planning artifacts or implement tasks, and clarification may use exploration, proposal creation, or update operations depending on current state. The workflow will therefore map names to OpenSpec operations, not assert a one-to-one ZPP-stage mapping.

An alternative was to annotate every stage with one skill. That would falsely turn component integrations into stage owners and would not represent operations that cross stage boundaries.

**Govern the wording canonically without adding behavior tests.** The complete `Explicit component delegation` requirement will be modified to carry the exact inventory. No Gherkin or unit test will pin literal artifact prose because there is no executable public-system observation and canonical specification already governs the obligation.

**Assess stage eligibility explicitly before every stage action.** The packaged workflow will require a visible assessment containing the current accepted contract revision, the explicitly requested stage, every predecessor checkpoint and its current evidence-backed outcome, the requested stage's eligibility or blocker, and the output that stage owns for the accepted effects. A requested stage is dispatch input only. It cannot establish its own eligibility, satisfy a predecessor, revive stale evidence, or convert a failure into a skip.

If any predecessor outcome is absent, stale, failed, or tied to a superseded contract, the requested stage remains blocked. The workflow may identify the earliest unsatisfied stage, but it does not execute that stage until the owner invokes it explicitly, except when separate end-to-end authority already permits automatic progression. A changed contract returns to clarification and invalidates downstream assessments derived from the older revision.

An alternative was to trust an agent to infer whether the requested stage is reasonable. That leaves the gate vulnerable to the same unsupported inference the explicit-stage rule was intended to remove.

**Split the assessment document, not the workflow authority.** `zpp-workflow/SKILL.md` will retain the non-bypass invariant, stage dispatch, transitions, authority boundaries, and the mandatory instruction to apply the complete assessment contract before every stage action. The detailed assessment schema, predecessor-gate matrix, effect classification, and per-stage applicability evidence will live at `zpp-workflow/references/stage-assessment.md` inside the same packaged skill directory.

The reference is normative content of `zpp-workflow`; it is not a separately installed skill, a companion operation, or an independent source of stage advancement, mutation, verification, or completion authority. Keeping the invariant in `SKILL.md` prevents an omitted reference read from appearing to make assessment optional, while moving the detailed matrix keeps the primary workflow legible.

An alternative was a second packaged skill such as a stage assessor. That would contradict the one-workflow-authority contract, add installation and invocation coupling, and create a bypass path in which an agent invokes the workflow without the assessor. Another alternative was to leave the full matrix inline, which preserves authority but makes the primary stage flow harder to inspect and maintain.

**Classify conditional work by effect before assessing its stage.** The accepted change is divided into externally observable public or integration behavior, pure executable utility behavior, executable artifact processing or update behavior, spec-governed prose, and ungoverned artifact text. That classification drives stage-owned outputs:

- Public or integration behavior may require `shape` and `wire`, with BDD selected only for an accepted shaped obligation observable through the public system.
- Pure executable utility behavior may require `plan-utilities` and `mature-utilities`, with case matrices kept in unit TDD.
- Executable artifact loading, parsing, validation, conversion, or update mechanics remain testable at their actual boundary even when their input is a skill or environment artifact.
- Spec-governed prose requires clarification, specification formation, and finalization, but by itself requires no Gherkin, BDD, utility plan, TDD, or wiring.
- Ungoverned artifact-only maintenance remains on the direct route and creates no workflow-stage outcomes.

This avoids a blanket “skill files are untestable” rule: the deciding fact is whether executable behavior changes, not the artifact name.

## Risks / Trade-offs

- **Generated OpenSpec names could change in a future OpenSpec release.** → ZPP already validates and provisions an exact canonical inventory; any inventory migration must reconcile both provisioning and workflow requirements together.
- **The inline list duplicates the provisioning inventory.** → The duplication is intentional at an operational boundary: provisioning governs what exists, while the workflow governs which component integration to follow. Strict OpenSpec validation and final diff review keep them aligned.
- **Readers may mistake skill identities for new workflow stages.** → The wording explicitly calls them operation owners and retains `zpp-workflow` as the only ZPP workflow authority.
- **Visible assessments add ceremony to small changes.** → Keep the assessment bounded to the requested stage and its predecessors, and allow evidence-backed not-applicable outcomes to remain concise.
- **An agent could restate unsupported evidence confidently.** → Require repository or accepted-contract evidence for each predecessor and block on missing or stale evidence; prose confidence is not a gate result.
- **An agent could overlook the internal reference.** → Keep the mandatory assessment and non-bypass rule in `SKILL.md`, explicitly require application of the complete reference, and treat the reference as content of the same installed workflow skill.
