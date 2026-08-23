---
name: zpps-explore
description: Discover or compare unresolved package, version, API, remote, repository, or integration evidence read-only; do not use for an already resolved mutation.
---

# Explore OpenSpec context without mutation

## Admit evidence discovery

Admit this component only when an active playbook configures this exact exploration
or the caller's immediate operation is read-only discovery, comparison, or validation
of unresolved external or repository evidence. It expressly owns unresolved package
availability, published versions, APIs, remote sources, repository changes, and
integration boundaries even when the eventual intent is to mutate dependencies,
planning, implementation, specifications, or archives. It does not admit an already
resolved mutation or grant mutation authority.

On any mismatch, return `component-mismatch` immediately with
`selected_component: zpps-explore`, the `observed_immediate_operation`,
`missing_readiness`, and the `separately_eligible_operation`. Stop before the normal
procedure and never invoke the separately eligible component.

Use this component for open-ended discovery, architecture investigation, requirement
clarification, and comparison of alternatives. It may be selected by a configured
playbook or invoked directly with a question and any known repository, store, or
change identity. Ask only for operation-specific input that cannot be inferred.

Exploration is a stance, not a fixed artifact workflow. Be curious, adaptive, and
grounded in the repository. Ask questions that expose decisions instead of forcing a
questionnaire; compare credible options, challenge assumptions, identify risks, and
use compact diagrams when relationships or state transitions are easier to see that
way.

## Resolve the evidence scope

1. If the caller identifies a registered OpenSpec store, or the work is known to live
   in one, run `openspec store list --json`, match the store, and retain its UUID.
   Append `--store <uuid>` to every applicable OpenSpec read command for the rest of
   this operation. Reject an unknown or ambiguous store rather than falling back to a
   different root.
2. Otherwise work from the caller's repository location. OpenSpec commands resolve
   the nearest repo-local `openspec/` root, including configured local pointers or a
   default store. Do not invent a root.
3. Run `openspec list --json` in the resolved scope. Note active change names, schemas,
   status, and recent activity. If a named change is absent, report that fact; do not
   create it.
4. Use the returned root and read `openspec/config.yaml` or `config.yml` when present.
   Treat project `context` as background and artifact-keyed `rules` only as constraints
   on a future artifact of that ID. Do not reproduce configuration blocks as findings.

If the installed executable cannot provide the required structured read interface,
stop with the failed command and observed error. Never run `openspec init`, install or
repair skills, generate workflow files, or attempt compatibility behavior.

## Investigate

- Inspect relevant source, tests, feature files, current specifications, traits, and
  repository memory when they bear on the question.
- If a change is relevant, run
  `openspec status --change <name> --json` in the sticky scope. Use `planningHome`,
  `changeRoot`, `artifactPaths`, and `actionContext` as authority. Read existing
  artifacts only from each `artifactPaths.<id>.existingOutputPaths`; do not assume
  familiar filenames or a spec-driven schema.
- Re-read files from disk when the conversation may contain stale content.
- Separate observations from inferences, unresolved owner decisions, risks, and
  recommendations. Follow useful tangents, but keep the accepted question visible.
- When decisions crystallize, identify the affected capability path or existing
  artifact precisely enough for a later planning operation. Preserve a capability's
  full path relative to the authoritative specs root.

## Mutation requests

Remain read-only even if the caller asks to capture the result. Do not scaffold a
change, create or revise an artifact, edit a specification, acquire a lease, or edit
product code. Instead return a requested planning operation:

- new scaffold only: `zpps-new-change`;
- one next artifact: `zpps-continue-change`;
- complete proposal: `zpps-propose-change`;
- complete already-understood planning set: `zpps-ff-change`;
- revisions to existing artifacts: `zpps-update-change`.

Include the accepted intent, resolved store UUID or repo-local root, change identity
when known, target artifacts or capability paths, and unresolved decisions. This is an
operation request, not authority to invoke it or continue a workflow.

## Result and stopping boundary

Return the resolved root, sticky store UUID if any, relevant change identities,
evidence inspected, findings, alternatives and tradeoffs, unresolved questions, and
any requested planning operation. Stop after discovery. Do not select or advance a
playbook step, invoke a mutating component, authorize a checkpoint or commit, or claim
verification or lifecycle completion.
