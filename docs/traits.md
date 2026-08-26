# Traits and resolution

Traits are small instruction families selected from explicit context and repository
evidence. They describe language, framework, structure, execution mode, and tooling
specialization; they do not carry workflow authority or lifecycle rules.

## Repository context

`.zpp/zpp.toml` supplies known repository facets:

```toml
[facet]
language = ["python", "flutter"]
build_tool = "uv"
```

Explicit invocation values and repository scalar values remain authoritative.
Evidence-derived and existing repository lists extend in deterministic first-seen
order.

Initialize this document with:

```powershell
zpp trait init context .
```

## Trait families

One `.zpp/traits/{family}.toml` file defines one family. Every flavor contains a
complete body so a person can understand it without following inheritance,
templates, or a provider graph.

```toml
[meta]
selection = "extend"
activation = "automatic"

[[trait]]
[trait.facet]
language = "python"
[trait.content]
body = "Use the repository's established Python test runner."

[[trait]]
[trait.facet]
language = "python"
build_tool = "uv"
[[trait.when]]
workspace_contains = "/pyproject.toml"
[[trait.when]]
which = "uv"
[trait.content]
body = "Use uv and the repository's established Python test runner."
```

Initialize an exact family document with `zpp trait init FAMILY [TARGET]`.

## Selection

Each family chooses one selection policy:

- `first-win` retains the first match in repository, selected store-chain, then
  global order.
- `all` retains every match.
- `extend` removes a generic match when a matching flavor has a strict superset of
  its facets, while retaining independent specializations.

A repository family can set `mode = "repository-overwrite"` to explicitly replace
store and global contributions for that family.

## Activation

Activation defaults to `automatic`, using normal facets and evidence.

- `manual` excludes the family from common resolution. Request it explicitly with
  repeatable `--trait FAMILY`.
- `always-run` bypasses facet and evidence activation but still applies the family's
  declared selection policy.

Evidence branches support `workspace_contains`, literal `file_contains`, and
`which`. One bounded evidence pass derives eligible facet values and typed facts
before final family selection. For example, `which = "uv"` publishes the typed
`has_uv` runtime fact.

This pass is not recursive. Newly detected context can activate another family's
matching flavor during the same resolution, but does not start another evidence
cycle.

## Sources and topology

ZPP composes repository traits with the selected OpenSpec store's root-to-target
parent chain and packaged defaults. Sibling stores never contribute. Packaged
defaults are source assets under `zpp/artifacts/traits`; that path is not a required
runtime collection layout.

The standard packaged families are:

- `bdd`
- `bdd-structure`
- `bdd-execution`
- `tdd`
- `tooling`

## Context and explanation

```powershell
zpp resolve . --facet language=python --facet build_tool=uv --explain
zpp resolve . --trait tooling --agent codex --explain
```

`--explain` returns recomputed `ZPP_CONTEXT` as compact version-2 JSON with
member-level source and evidence provenance. ZPP accepts version 1 from the
environment and upgrades it after a successful resolution. When an evidence
fingerprint changes, only values owned by that evidence are removed. Context is
target-bound, and resolution never persists inferred values into `.zpp/zpp.toml`.

`--stage` is protected invocation state. Accepted values are `clarify`, `shape`,
`plan-utilities`, `mature-utilities`, `wire`, `form-specs`, and `finalize`.
Repository context, stored context, and evidence cannot author it, and it is not
serialized into descriptive `ZPP_CONTEXT`.

For authoring guidance, invoke the packaged `zpp-author-trait` companion skill.
