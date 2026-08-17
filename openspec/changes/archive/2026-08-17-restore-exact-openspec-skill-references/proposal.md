## Why

The packaged workflow delegates OpenSpec work to an unspecified “installed skill,” even though ZPP provisions a stable six-skill operation inventory. It also accepts an explicitly named stage without first making the stage's eligibility and predecessor gates visible. Those ambiguities make the workflow harder to follow and let stage selection be mistaken for gate satisfaction.

## What Changes

- Name all six component-owned OpenSpec skills in the packaged `zpp-workflow` instructions.
- Describe each skill by the operation it owns so an agent can select the exact integration without treating it as a ZPP workflow stage.
- Require an explicit, evidence-based eligibility assessment before every stage action; naming or guessing a stage does not satisfy it or its predecessors.
- Keep the assessment authority in `zpp-workflow` while moving its detailed schema and gate matrix into an internal `references/stage-assessment.md` document applied by the main skill.
- Decide conditional-stage applicability from accepted observable and executable effects rather than artifact labels, so prose-only skill or environment-guidance updates do not manufacture BDD, utility, TDD, or wiring work.
- Block an out-of-sequence stage when a predecessor checkpoint is absent or stale, while preserving explicit stage invocation and separately authorized end-to-end progression.
- Reconcile the canonical consolidated-workflow requirement with the shipped instructions.
- Keep the correction prose-only: no runtime behavior, Gherkin, utility, dependency, or compatibility changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Require exact OpenSpec operation delegates, effect-based conditional-stage applicability, and explicit predecessor-gate assessment before stage execution.

## Impact

- `src/zpp/artifacts/skills/workflow/zpp-workflow/SKILL.md`
- `src/zpp/artifacts/skills/workflow/zpp-workflow/references/stage-assessment.md`
- `openspec/specs/consolidated-workflow-skill/spec.md` during specification formation
- No public CLI, runtime, packaged inventory, dependency, or verification-provider changes

## Unresolved — Do Not Assume

None.
