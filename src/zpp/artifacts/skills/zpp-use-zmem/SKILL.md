---
name: zpp-use-zmem
description: Investigate durable temporal decision history with zmem and verify it against current authority. Use when a change depends on earlier decisions, reversals, fallbacks, surprises, lessons, relationships, or commit context; this skill is read-only and does not create annotations or commits.
---

# Use zmem

Treat zmem as chronological evidence, not current truth. Canonical OpenSpec owns
long-standing accepted behavior; active OpenSpec artifacts own the current
change; current code shows implemented reality.

1. Run `zmem recall` for structured decision events. Narrow with repeatable
   `--event`, `--scope`, `--since`, or `--limit`; use `--events` for category
   counts.
2. Run `zmem search QUERY --in annotations|memory|commits|all` when the relevant
   commit is unknown. Use `--all` only when the decay window is insufficient,
   `--regex` only for an intentional expression, and `--include-deleted` only
   when tombstoned history matters.
3. Run `zmem show SHA` to inspect conventional-commit fields, annotations, and
   changed paths. Add `--diff-content` only when the historical diff is needed.
4. Run `zmem links --from ID` or `--to ID` to traverse directed relationships;
   narrow with `--min-score` and expand with `--all` only when justified.
5. Prefer default JSON for exact fields and automation. Use global `--human`
   for readable review, and global `--repo PATH` when the subject is not the
   current repository.
6. Compare the evidence with canonical specs, active change artifacts, and the
   relevant current code before relying on it. State conflicts and favor the
   current authority unless the owner changes it.

Do not treat an empty recall as a gate or write a placeholder memory. Delegate
material commit annotations to `zpp-commit-zmem` only when mutation authority
exists.
