## Context

See `proposal.md` for motivation and the delta specs for mature behavior. ZPP already separates Typer CLI entry points, core orchestration, small reusable utilities, and packaged resources. The accepted workflow skills are maintained in the development skill area but must ship as product-owned resources usable by Pi, Codex, and Claude Code.

## Goals / Non-Goals

**Goals:**

- Ship one authoritative seven-skill bundle and project it safely into supported native skill roots.
- Keep selection, scope, compatibility, ownership, preflight, and rollback behavior consistent across install, update, and removal.
- Preserve platform-neutral skill bodies and keep automatic workflow progression advisory.

**Non-Goals:**

- Do not execute `skill_lookup` or implement a runtime workflow state machine.
- Do not merge workflow-skill installation into `zpp init` or authored `.zpp` layers.
- Do not define native agents' precedence when global and local copies coexist.

## Decisions

### Package resources are the only installation source

The product bundle lives beneath `zpp.artifacts.skills`; development copies are not read during installation. Python package-resource traversal preserves wheel compatibility and exact resource bytes. A wheel-content verification guards the distribution boundary.

### Ownership is explicit and content-backed

Each projection receives one ZPP metadata sidecar describing bundle version, fingerprint, and every owned relative file. A projection is compatible only when the metadata and exact bytes agree. Internally consistent older metadata is outdated; missing metadata with same-name skill content, malformed metadata, tampering, or unsafe ownership claims are conflicts. This avoids destructive folder-name inference.

### Projection selection precedes mutation

Thin native-path adapters map Codex and Pi to their shared `.agents/skills` root and Claude Code to `.claude/skills`. Core orchestration resolves an accepted scope and agents, deduplicates shared destinations, inspects all selected state, produces one complete lifecycle plan, and applies it only after successful preflight.

### Existing rollback primitives compose the transaction

Managed replacements and removals are staged through adjacent tombstones. One creation plan writes every selected projection; a later failure rolls back new files and restores staged state. Successful completion deletes only metadata-owned paths and never removes the surrounding native skill root.

### Reporting avoids precedence claims

Core orchestration compares corresponding managed global and local projections after lifecycle work. CLI output reports coexistence and differing versions while deliberately omitting a preferred scope. The agents' own resolution behavior remains authoritative.

## Risks / Trade-offs

- [Risk] User edits can invalidate a managed projection. → Classify it as a conflict and require explicit user resolution rather than repairing or deleting it.
- [Risk] Codex and Pi selections can name the same destination twice. → Coalesce their canonical native root before inspection and mutation.
- [Risk] A process crash may leave an adjacent tombstone. → Preserve detectable owned state and never overwrite unrelated content; automated crash recovery is deferred.
- [Risk] Installed agents can resolve coexisting scopes differently. → Report both scopes and versions without asserting precedence.

## Migration Plan

No prior managed workflow-skill installation exists. Release ZPP 0.9.0 with the packaged artifacts and lifecycle commands. Users may install globally or locally through the new commands. Rollback uses confirmed `zpp skill remove` for managed projections and does not affect lifecycle hooks or authored trait layers.
