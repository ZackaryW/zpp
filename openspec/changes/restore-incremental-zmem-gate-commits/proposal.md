## Why

The consolidated workflow calls several outcomes “checkpoints” but never defines them as Git commits, and its automatic-progression clause explicitly withholds commit authority. As a result, a complete workflow can accumulate every responsibility into one final commit even though ZPP installs `zmem-author-commits` and the intended history is dependency-ordered, independently coherent gate commits.

## What Changes

- Require every material workflow stage gate to use the installed `zmem-author-commits` skill before it can complete.
- Define a material gate as a completed stage that owns a non-empty coherent diff; skipped stages and gates with no diff create no empty commit.
- Require stage-appropriate verification before committing, stage only the explicit paths or hunks owned by that gate, validate the proposed message with zmem, and inspect every created commit with `zmem show`.
- Require dependency-ordered incremental commits when a gate contains distinct responsibilities, without creating an intermediate commit known to break the repository.
- Treat explicit end-to-end workflow delegation as checkpoint commit authority for the resulting gate series. Without checkpoint commit authority, a material gate remains incomplete and pauses before committing.
- Preserve unrelated working-tree changes and withhold amend, merge, rebase, push, and unrelated reconciliation authority.
- Change finalization from collapsing work into one logical commit to verifying the checkpoint series and committing only remaining archival/finalization work.
- Keep annotations selective: `zmem-author-commits` decides whether a commit contains durable memory rather than requiring a meaningless annotation on every commit.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `consolidated-workflow-skill`: Define material stage checkpoints as verified incremental zmem-aware commits and carry their authority through explicitly delegated end-to-end progression.

## Impact

- `src/zpp/artifacts/skills/workflow/zpp-workflow/SKILL.md`
- `src/zpp/artifacts/skills/workflow/zpp-workflow/references/stage-assessment.md`
- `openspec/specs/consolidated-workflow-skill/spec.md` during specification formation
- Uses the already packaged `zmem-author-commits` companion skill; no runtime, CLI, dependency, Gherkin, or TDD changes

## Unresolved — Do Not Assume

None.
