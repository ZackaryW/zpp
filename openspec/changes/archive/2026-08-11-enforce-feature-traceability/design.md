## Context

The workflow already shapes confirmed changes into features and utility tests, but its source boundary does not explicitly exclude non-behavior documents and artifacts.

## Goals / Non-Goals

**Goals:** Restrict Gherkin to behavior delta specs, require concise bidirectional coverage when those deltas exist, and restrict TDD to executable behavior rather than artifact wording.

**Non-Goals:** Add a persisted ledger, identifier syntax, runtime code, or one-to-one requirement/scenario mapping.

## Decisions

Add concise normative lines beside the stage definitions. Treat only accepted externally observable obligations in active capability delta specs as Gherkin sources. Explicitly exclude proposals, designs, tasks, docs, artifacts, configuration-only work, and implementation details. If no behavior delta remains, `shape` is not applicable; otherwise incomplete or untraced coverage blocks completion.

Treat executable behavior as the TDD subject. Artifact loading, unloading, parsing, validation, and conversion into runtime classes or models remain eligible; assertions that merely pin prose or arbitrary artifact wording do not. If no executable utility behavior remains, `mature-utilities` is not applicable.

A new artifact format was rejected because the completion check needs semantic coverage, not another user-maintained file.

## Risks / Trade-offs

- **Traceability becomes superficial** → Require both scenario-to-change and obligation-to-coverage checks.
- **Non-behavior work leaks into Gherkin** → Exclude it as a source and make artifact-only shaping not applicable.
- **Artifact prose becomes a brittle unit-test contract** → Test artifact-processing behavior while excluding assertions that merely pin prose or arbitrary wording.

## Open Questions

None.
