# Resolver evidence

## Start from one target

Run the pair below against the same concrete file or directory:

```text
zpp resolve <target> --json
zpp config resolve <target> --sources --json
```

Use a file path when a task edits a file. Config resolution evaluates a file through its parent directory, while preserving the resolved governance boundary.

## Interpret the outputs

`zpp resolve` answers authority and isolation questions:

- `mode` and `rule`: which governance rule matched
- `root` or `store`: the governing identity
- `isolation`: the effective branch/root or a structured remediation state
- `reference_stores`: available references, never governing authority

The four governance outcomes are ordered: a local OpenSpec root, a committed repository binding, a workset profile binding, then ungoverned. Confirm current names and fields from live output and the governance-resolution spec.

`zpp config resolve --sources` answers policy questions:

- `effective`: the configuration the target receives
- `origins`: the winning source for each leaf
- `layers`: store defaults, workset overlay, repository-root config, and any ordered target scopes exposed by the current contract

Merge direction is from broad authority toward the concrete target. Nearer scalars replace inherited values, lists union without duplicates, and tables merge recursively. Confirm exact behavior from the active governance-resolution spec and tests before relying on it.

## Avoid common traps

- Do not resolve `.` when the decision concerns `sdk/python`, a sibling tree, or a specific file.
- Do not infer a stack from installed executables, task wording, repository majority, or another repository's `zpp.toml`.
- Do not confuse a governing store with a reference store.
- Do not confuse the registered base store with a branch-isolated effective governance root.
- Do not assume a nested `zpp.toml` creates a governance root. Check the root-only authority contract and the scoped layer evidence.
- Do not claim that inspection provisions a missing worktree. Read-only resolution must report remediation without mutating state.
- Do not infer either Git submodule capabilities or limits from path appearance. Verify the repository tree and current Git documentation or live command behavior.
- For a submodule claim, report four fields separately: cloneable repository URL, downstream mount path, pinned gitlink commit, and optional branch-following configuration. Do not reinterpret a downstream `path` or tracked `branch` as an upstream tree-prefix selector.

## Escalate contradictions

If resolver output, OpenSpec, and implementation disagree, capture all three in the evidence note. Treat that as a contract or implementation issue; do not hide it with a copied config, session-only override, or guessed fallback.
