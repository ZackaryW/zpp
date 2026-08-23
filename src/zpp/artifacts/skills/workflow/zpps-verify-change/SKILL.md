---
name: zpps-verify-change
description: Read-only verification of one OpenSpec change against its implementation, executable evidence, design, tasks, and single acceptance-authority bindings.
---

# Verify one OpenSpec change

Produce an evidence-backed completeness, correctness, and coherence assessment. This
component is read-only and may be invoked by a playbook or directly. It never repairs
the change or selects the enclosing workflow's next operation.

## Resolve the verification target

Accept an exact change when supplied. Otherwise infer it only from unambiguous
conversation context or the sole active change with implementation tasks. If several
remain possible, run `openspec list --json`, show changes with task artifacts, their
schemas, and incomplete-task state, and ask the owner to select. Announce the selected
change and how to choose another.

When a registered store is named or the work resolves inside one, run
`openspec store list --json`, use the returned UUID, and keep `--store <uuid>` sticky
on every store-aware command. Otherwise use the nearest repository-local `openspec/`
root. That repo-local root remains fully valid for this read-only audit and for
resolving an exact `repo:<git-root-relative-path-to-openspec-root>` trace locator.
Never guess a store identifier or require registration merely to verify.

Verify at invocation time that the installed executable supports public list,
structured status, and structured `instructions apply`. Never run `openspec init`,
load or repair generated `openspec-*` skills, or invoke ZPP lifecycle commands. This
read-only audit needs no mutation lease. It accepts repository-verification evidence
only when the caller explicitly supplies it; it does not invoke another component.

## Load the schema-driven contract

1. Run `openspec status --change "<name>" --json` with the selected-store flag when
   applicable. Preserve `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`,
   `artifacts`, and `actionContext`.

2. Run `openspec instructions apply --change "<name>" --json`. Preserve the returned
   state, progress, tasks, built-in instruction, and every concrete path under every
   `contextFiles` entry. Read all available files. Do not assume proposal, design,
   specs, or tasks exist, and do not infer artifact filenames from a familiar schema.

3. Record which verification dimensions can be assessed. Gracefully degrade:

   - tasks only: assess task completeness;
   - tasks plus requirements: add requirement and acceptance-authority correctness;
   - design present: add design adherence;
   - missing artifacts: explicitly list each skipped check and why.

## Assess completeness

- For every concrete task artifact, parse `- [ ]` and `- [x]`, count progress, and
  report each incomplete task as `CRITICAL` with an actionable recommendation.
- Extract every `### Requirement:` from each returned delta-spec path. Search the
  implementation for concrete evidence of each obligation. A requirement with no
  credible implementation evidence is `CRITICAL`; cite paths and lines when evidence
  exists and say when the search is inconclusive.
- Treat a checked box as a claim, not proof. If its implementation or required
  verification is absent, report the discrepancy.

## Assess correctness and single acceptance authority

For every requirement, determine whether its acceptance authority is executable BDD
or normative specification content.

For a BDD-backed public-system obligation:

- parse the compact JSON in the feature-side `# zpp-spec:` declaration immediately
  above the scenario and the OpenSpec trace-only conformance scenario;
- require exactly the same five values, in order: `root`, `capability`, `requirement`,
  `feature`, and `scenario`;
- resolve `store:<uuid>` only through `openspec store list --json`, or resolve
  `repo:<git-root-relative-path-to-openspec-root>` inside the current worktree;
- require the exact capability directory identity, exact requirement heading,
  normalized Git-root-relative feature path, and exactly one matching scenario title;
- require the feature declaration to be immediately adjacent to its scenario and the
  OpenSpec target to resolve back to the identical tuple;
- reject missing, malformed, guessed, stale, ambiguous, one-way, or orphaned bindings;
- reject a BDD-backed requirement without an executable feature scenario and reject a
  concrete OpenSpec GIVEN/WHEN/THEN duplicate of that feature scenario.

For a spec-only obligation, require that no feature claims its acceptance authority.
For a pure-functionality matrix, look for focused unit-test evidence rather than
fabricating public BDD. Retaining one public end-to-end BDD scenario is appropriate
only when it proves a public-system integration boundary.

Map each requirement to implementation evidence and compare behavior with the
requirement's intent. A demonstrated divergence is a `WARNING`; an absent required
implementation is `CRITICAL`. For each executable scenario, consume supplied native
repository evidence that identifies the exact scenario/target and command result.
Do not treat a trace-only conformance anchor as executable evidence.

If required executable evidence is absent, stale, failed, or does not cover the
resolved scenario, return `repository-evidence-required` and identify the exact
feature/scenario or native verification surface needed. Do not invoke
`zpps-verify-repository` implicitly and do not declare ready for archive.

## Assess coherence

- When a design artifact exists, extract its material decisions and compare the
  implementation with them. Report contradictions as `WARNING` with exact evidence
  and recommend either implementation correction or an explicit planning revision.
- Review changed code for significant naming, layout, dependency, and architectural
  inconsistencies with established repository patterns. Reserve `SUGGESTION` for
  non-blocking improvements; do not turn stylistic preferences into failures.
- Check proposal, design, specs, tasks, implementation, and both sides of every BDD
  binding for terminology or authority drift.

Prefer the least severe defensible classification when evidence is uncertain:
`SUGGESTION` before `WARNING`, and `WARNING` before `CRITICAL`. Every issue must state
the affected requirement/task/decision, evidence, location where applicable, and a
specific corrective action.

## Result

Return a Markdown report containing:

- resolved root, store UUID when applicable, change, and schema;
- a completeness/correctness/coherence scorecard;
- task and requirement coverage counts;
- repository evidence consumed and checks skipped;
- `CRITICAL`, `WARNING`, and `SUGGESTION` findings in priority order;
- binding failures, duplicate or orphaned acceptance authority, and missing evidence;
- one bounded conclusion: `ready`, `not-ready`, or `repository-evidence-required`.

Any critical issue or missing required executable evidence prevents `ready`. Warnings
may yield `ready` only when each is explicitly disclosed. Remain read-only: do not
edit artifacts, bindings, tests, or product code; choose or advance a stage; acquire,
expand, or complete a lease; authorize a checkpoint/commit; sync or archive; invoke
onboarding; or claim lifecycle completion.
