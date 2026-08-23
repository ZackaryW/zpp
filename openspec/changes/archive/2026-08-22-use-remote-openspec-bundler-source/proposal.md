## Why

ZPP currently resolves `openspec-bundler` from an adjacent checkout, which makes installation depend on machine-local repository layout. The proven Bundler revision is now available from its GitHub remote and can be consumed reproducibly.

## What Changes

- Replace the adjacent-path uv source with the GitHub repository pinned to the proven immutable commit `63cb9851931b9d242abf8abf75565c34cc2b3779`.
- Regenerate the lockfile so every ZPP environment resolves the remote Git source rather than `../openspec-bundler`.
- Verify dependency resolution, all tests, all capability-owned BDD roots, and package builds against the remote source.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The canonical Bundler integration behavior is unchanged; this change replaces only its dependency distribution source and therefore opts out of delta specifications.

## Impact

Affected files are `pyproject.toml` and `uv.lock`. Network access to GitHub is required when populating a fresh dependency cache, while runtime APIs and ZPP behavior remain unchanged.
