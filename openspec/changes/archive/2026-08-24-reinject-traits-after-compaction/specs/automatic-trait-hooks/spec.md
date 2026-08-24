## ADDED Requirements

### Requirement: Post-compaction trait reinjection
After every successful context compaction, ZPP SHALL make a fresh successful trait
resolution available as advisory context before the supported client continues with
its next model request. ZPP SHALL use each client's context-bearing native path:
compact-source `SessionStart` for Codex and Claude Code, `PostCompact` for Kimi, and
per-run `before_agent_start` for Pi.

ZPP SHALL NOT add a duplicate post-compaction resolver where the existing native
context-injection event already covers compaction, SHALL NOT rely on a native event
whose command output is ignored, and SHALL NOT cache trait output between events.

#### Scenario: Conformance trace for post-compaction reinjection
- **WHEN** conformance is evaluated for `{"root":"repo:openspec","capability":"automatic-trait-hooks","requirement":"Post-compaction trait reinjection","feature":"features/automatic_trait_hooks/automatic_trait_hooks.feature","scenario":"Package post-compaction trait reinjection for every supported agent"}`
- **THEN** executable acceptance authority is `features/automatic_trait_hooks/automatic_trait_hooks.feature::Package post-compaction trait reinjection for every supported agent`
