## Context

See `proposal.md` for motivation. The four supported clients expose different
context-bearing compaction paths. Codex and Claude Code run `SessionStart` after
compaction and inject its output; Kimi exposes `PostCompact` and adds successful
stdout to context; Pi rebuilds the system prompt through `before_agent_start` before
every model run. Codex also exposes `PostCompact`, but ignores plain stdout there.

## Goals / Non-Goals

**Goals:**

- Preserve fresh advisory trait context across successful compaction for all four
  supported clients.
- Keep one resolver command and the existing failure-isolation semantics.
- Express the compatibility matrix in executable packaging evidence.

**Non-Goals:**

- Force a uniform native event name across clients.
- Add a trait-output cache or persistent context entry.
- Change lifecycle ownership, resolver behavior, or Agent Router compatibility.

## Decisions

### Extend only the Kimi hook asset

The Kimi TOML asset will carry both `SessionStart` and `PostCompact` entries using
the same `zpp resolve --agent kimi .` command. The other packaged assets remain
unchanged because their existing context-bearing path already covers the next model
request after compaction.

Alternative: add `PostCompact` to every client. Rejected because Codex ignores plain
stdout from that event, Agent Router does not currently accept it for Claude, and Pi
cannot alter the system prompt from `session_compact`.

### Verify an outcome-oriented client matrix

One public packaging scenario will assert the native reinjection strategy for each
supported client. Focused artifact tests will prove Kimi has both events and that
Codex, Claude, and Pi retain their non-duplicating paths.

Alternative: test only the new Kimi line. Rejected because the accepted capability is
cross-client behavior and a future uniform-event rewrite could silently regress it.

## Risks / Trade-offs

- Client hook contracts change → Keep the matrix explicit and validate updates
  against current primary client documentation.
- Kimi invokes resolution more often → Limit the additional invocation to successful
  compaction and retain existing resolver failure visibility.
- Existing Kimi ownership becomes outdated → Let normal `zpp sync` or grouped
  workflow update replace the owned asset through Agent Router.

## Migration Plan

Ship the updated asset with its behavior and artifact tests. Existing owned Kimi
hooks update through the established lifecycle; other clients retain identical hook
fingerprints. Rollback removes only the Kimi `PostCompact` entry.
