## Context

ZPP already depends on Bundler 0.1.0 and has verified the integration against local revision `63cb9851931b9d242abf8abf75565c34cc2b3779`. That revision is now the GitHub `main` head. See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**

- Make fresh ZPP environments resolve Bundler without an adjacent checkout.
- Preserve reproducibility by pinning the exact proven remote commit.
- Ensure built distribution metadata carries the Git dependency rather than relying on uv-only source configuration.

**Non-Goals:**

- Changing Bundler APIs, ZPP behavior, or the established lease and attachment contracts.
- Publishing Bundler to a package index or tracking a mutable branch implicitly.

## Decisions

Declare Bundler as a PEP 508 direct Git dependency in `project.dependencies`, using the full GitHub URL and immutable commit. This matches ZPP's existing Agent Router dependency convention and ensures the source survives package builds. A `[tool.uv.sources]` Git override was rejected because it is uv-specific and does not become wheel metadata; an unpinned branch was rejected because lock regeneration could silently select later code.

Regenerate `uv.lock` from the declaration and require its Bundler package source and ZPP requirement metadata to identify the same remote commit.

## Risks / Trade-offs

- [GitHub must be reachable on an uncached install] → Pin an immutable commit so caches remain reusable and resolution is deterministic.
- [The Git history must retain the pinned object] → Pin a commit already present on the public repository's main branch.
- [Future Bundler updates require an explicit ZPP change] → Treat that as intentional dependency review rather than automatic drift.

## Migration Plan

1. Replace the bare dependency and local uv source override with the pinned direct Git requirement.
2. Regenerate and inspect `uv.lock`.
3. Sync in locked mode, verify the installed source revision, then run complete tests, BDD, validation, and build gates.
4. Roll back by restoring the previous declaration and lockfile if remote resolution or verification fails.
