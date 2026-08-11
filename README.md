# ZPP 2.0

ZPP resolves small, repository-oriented behavior traits for coding agents. It
ships one consolidated workflow skill; workflow stages and authority are not
traits.

## Trait documents

One `.zpp/traits/{family}.toml` file defines one family. Every flavor keeps a
complete body so a human can understand it without inheritance, templates, or a
provider graph.

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

`first-win` retains the first match in repository → selected space → global
order. `all` retains every match. `extend` removes a generic match when a
matching flavor has a strict superset of its facets, while retaining independent
specializations. A repository document can set
`mode = "repository-overwrite"` to replace space and global contributions for
that family explicitly.

Activation defaults to `automatic`, which uses normal facet and evidence
matching. `manual` families are excluded from common resolution and can be
requested explicitly with repeatable `--trait FAMILY`. `always-run` families
bypass facet and evidence activation but still apply their declared selection
policy.

Repository context lives in `.zpp/zpp.toml`:

```toml
[facet]
language = ["python", "flutter"]
build_tool = "uv"
```

Evidence branches support `workspace_contains`, literal `file_contains`, and
`which`. A successful evidence fallback may backfill missing facets once; it
does not recursively restart selection. `which = "uv"` also publishes a typed
`has_uv` runtime fact.

## Commands

```text
zpp init [--agent AGENT ...]
zpp resolve [TARGET] [--trait FAMILY ...] [--stage STAGE] [--facet NAME=VALUE ...] [--agent AGENT] [--explain]
zpp trait init context|FAMILY [TARGET]
zpp workflow install|update|remove [--agent AGENT ...] [--target PATH | --global]
```

Agent values come directly from Agent Router. Repeated explicit values retain
first-seen order and are deduplicated. Required interactive selection offers
Codex, Claude Code, Pi, and Kimi in that order; cancellation occurs before any
projection. `resolve` accepts at most one agent because it reads that invoking
agent's effective plugin artifacts.

Default `resolve` output is the selected complete trait bodies, ready for prompt
injection. `--explain` emits the structured bodies, context, and deterministic
selection decisions instead.

OpenLease owns direct TOML binding, provenance, selected-space configuration,
and bounded writes. Existing repository documents can be read from an
unregistered repository without creating or selecting a space. Agent Router owns
plugin discovery and every workflow skill and native hook destination mutation.
The installed hook invokes `resolve` automatically for Codex, Claude Code, Pi,
or Kimi; the consolidated skill contains workflow policy and does not bootstrap
trait resolution.

Packaged defaults are source assets under `zpp/artifacts/traits`; this is not a
required runtime collection layout. ZPP 1.x Markdown traits and its seven stage
skills are not migration inputs.
