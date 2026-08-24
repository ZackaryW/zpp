## Why

Context compaction can discard previously injected trait bodies. Kimi exposes a
dedicated post-compaction hook whose output returns to model context, while the other
supported clients already re-resolve traits through their native post-compaction or
per-run context-injection path.

## What Changes

- Guarantee fresh trait resolution after successful compaction for every supported
  client without requiring one uniform native event name.
- Add `PostCompact` resolution to the packaged Kimi hook alongside `SessionStart`.
- Retain Codex and Claude compact-source `SessionStart` injection and Pi's per-run
  `before_agent_start` injection instead of adding duplicate, ignored, or cached work.
- Keep failure isolation and the no-session/no-coordination boundary unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `automatic-trait-hooks`: Require client-native post-compaction reinjection across
  Codex, Claude Code, Kimi, and Pi.

## Impact

Affected areas are the packaged Kimi hook, cross-client hook-shape behavior, focused
artifact tests, the automatic-trait-hooks Behave capability, and its canonical
specification. No public command, dependency, or compatibility alias is added.
