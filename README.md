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

`first-win` retains the first match in repository → selected store chain → global
order. `all` retains every match. `extend` removes a generic match when a
matching flavor has a strict superset of its facets, while retaining independent
specializations. A repository document can set
`mode = "repository-overwrite"` to replace store and global contributions for
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
`which`. Before final family selection, one bounded evidence pass derives
eligible facet values and typed facts. This lets detected TypeScript context,
for example, activate another family's TypeScript flavor during the same
resolution without starting a recursive pass. Existing repository lists and
evidence-owned values extend in deterministic first-seen order; explicit
invocation values and repository scalars remain authoritative. `which = "uv"`
also publishes a typed `has_uv` runtime fact.

`resolve --explain` returns the recomputed `ZPP_CONTEXT` as compact version-2
JSON with member-level source and evidence provenance; normal `resolve` output
contains only selected bodies. ZPP still accepts version 1 from the environment
and upgrades it on the next successful resolution. When an evidence fingerprint
changes, only members owned by that evidence are removed. Context is
target-bound. Persisting selected values in `.zpp/zpp.toml` remains an explicit
repository-authoring operation rather than a resolution side effect.

## Commands

```text
zpp [--path ZPP_HOME] COMMAND
zpp init [--agent AGENT ...] [--force] [--json]
zpp open
zpp reset --yes [--json]
zpp resolve [TARGET] [--trait FAMILY ...] [--stage STAGE] [--facet NAME=VALUE ...] [--agent AGENT] [--explain]
zpp behave init
zpp behave COMMAND [--all | --target TARGET ... | --gate GATE | --base REV --head REV]
zpp trait init context|FAMILY [TARGET]
zpp lease acquire --owner OWNER --member UUID:CHANGE [--member UUID:CHANGE ...]
zpp lease status
zpp lease audit --bundle UUID --path PATH [--path PATH ...]
zpp lease archive --bundle UUID --owner OWNER --member UUID:CHANGE
zpp lease complete|abandon --bundle UUID --owner OWNER
zpp workflow install|update|remove [--agent AGENT ...] [--target PATH | --global]
```

The root `--path` option selects ZPP's home. It defaults to `~/.zpp`, and every
Bundler lease command uses only that home's `bundler` child as managed
state. Merely selecting a home does not create it. `zpp open` creates the
selected home when absent and opens that exact directory in the native file
manager without initializing Bundler state or interpreting the other contents.

`zpp reset --yes` preflights every supported agent's ZPP-owned user-scope
`zpp-workflow` skill, every packaged companion skill, and `zpp-traits` hook
through Agent Router. If that preflight succeeds, reset
removes those intact packaged assets normally and force-deletes the six
canonical Agent Router-owned OpenSpec skills for each agent by stable name. A
modified packaged companion skill remains a conflict. A modified generated
skill is removed with its ownership state and no retained history; an unmanaged
same-named skill is preserved as a conflict. Reset never regenerates OpenSpec.
Only after all removals succeed does it replace the selected home's `bundler`
child. It preserves the home itself, repository `.zpp` documents,
`zpp.behave.yaml`, project-scope projections, plugins, worktrees, and unrelated
files. A removal failure leaves prior Bundler state unchanged and a retry
accepts assets already removed. Reset has no global-trait overwrite mode.
Successful reset prints one concise summary line by default; `--json` emits the
complete inspection, removal, and state report.

Resolution is read-only and creates no lease state. If the target is inside a
registered OpenSpec store, ZPP composes only that store's root-to-target parent
chain. Sibling stores never contribute.

`--stage` accepts only `clarify`, `shape`, `plan-utilities`,
`mature-utilities`, `wire`, `form-specs`, or `finalize`. Stage is protected
invocation state: repository context, stored context, and evidence cannot author
it, and it is never serialized into descriptive `ZPP_CONTEXT`.

Agent values come directly from Agent Router. Repeated explicit values retain
first-seen order and are deduplicated. Required interactive selection offers
Codex, Claude Code, Pi, and Kimi in that order; cancellation occurs before any
projection. `resolve` accepts at most one agent because it reads that invoking
agent's effective plugin artifacts.

`zpp init` requires the local `openspec` executable. For every selected agent it
freshly generates and validates the six core OpenSpec operation skills before
projecting anything, then Agent Router installs or safely reconciles those
skills together with `zpp-workflow`, `zpp-traits`, and every packaged companion
skill in user scope. Re-running `init` is the only OpenSpec
regeneration operation and also reconciles the packaged companion skills.
Successful initialization prints one concise summary line by default; `--json`
emits every ordered Agent Router lifecycle result. `--force` reprojects every
selected owned integration, including safely replacing diverged skills with
matching Agent Router ownership, while unmanaged destinations remain conflicts.
The grouped `workflow` commands continue to manage only the consolidated
workflow skill and native hook; they expose no authoring-skill or OpenSpec
option.

Packaged skills live under `zpp/artifacts/skills/{role}/{skill}`. The `workflow`
role holds exactly one skill; every skill in the `companion` role is discovered
by directory scan, in deterministic name order, and is projected and removed as
part of the installation. A directory is a skill only when it contains
`SKILL.md`. Adding a companion skill requires no code change; an unusable role
fails loading rather than yielding a partial inventory.

`zpp-configure-behave` is a manual authoring skill for repository-backed
verification providers, stable segmented targets, conservative path rules,
gates, and validation of `zpp.behave.yaml`. `zpp-author-trait` is a manual
authoring skill for one-family TOML documents, activation, selection, facets,
evidence, complete bodies, and explained resolution. `zmem-author-commits` and
`zmem-query-memory` are vendored companion skills for authoring and querying
durable repository memory, kept current from upstream by the
`sync-vendored-skills` workflow. No companion skill runs from a
hook or workflow transition, and none introduces another CLI command.

Default `resolve` output is the selected complete trait bodies, ready for prompt
injection. `--explain` emits the structured bodies, context, and deterministic
selection decisions instead.

Repository verification is declared in a dedicated root `zpp.behave.yaml`
version-1 document. `zpp behave COMMAND` uses affected selection by default;
exact targets, a repository-owned gate, complete selection, and a paired revision
range are explicit mutually exclusive modes. Commands select one configured
`argv`, `nx`, or `go-task` provider, and ZPP executes only validated shell-free
arguments. `zpp behave init` and direct execution use an exact raw Bundler
repository attachment. ZPP owns YAML validation, target selection, and process
execution. Mapping presence never triggers execution, and direct behavior
commands create no lease state.

Native BDD execution does not require `zpp.behave.yaml`. The consolidated
workflow may run an established repository Behave, Cucumber, or other BDD
surface directly from repository configuration or an explicit owner choice.
`zpp.behave.yaml` participates only when the repository explicitly chooses
`zpp behave` for affected-target or gate coordination.

Bundler owns bounded raw repository attachments, exact `zpp-traits` store
namespaces, store topology, and durable atomic leases. ZPP owns TOML and YAML
decoding, repository-plus-store-chain composition, and behavior execution. A
store declares its UUID, optional parent, and ZPP namespace in its one
`openspec/bundler.toml` document:

```toml
version = 1
uuid = "8f85ef9f-d18a-4787-903e-1ecb920acb77"
parent = "52b7223b-3d15-4e8a-98f7-d8ddc90fbf1c"

[extensions.zpp-traits]
```

The workflow acquires one bundle before governed OpenSpec mutation. A requested
parent holds its descendant closure; independent roots requested together form
one atomic crew. Finalization audits changed OpenSpec paths, records every
archive, and completes the bundle only after all members archive. Agent Router owns
plugin discovery and every workflow skill and native hook destination mutation.
The installed native context hook invokes `resolve` automatically: Codex and
Claude Code use JSON SessionStart hooks, Kimi uses a TOML SessionStart hook, and
Pi uses a TypeScript `before_agent_start` extension. There is no invocation
command, resolver skill, or UserPromptSubmit resolution hook. The consolidated
skill contains workflow policy and does not bootstrap trait resolution.

Packaged defaults are source assets under `zpp/artifacts/traits`; this is not a
required runtime collection layout. The standard families are `bdd`,
`bdd-structure`, `bdd-execution`, `tdd`, `build`, `dependencies`, `tooling`, and
`zero-assumptions`. Lease progression remains workflow-skill behavior rather
than globally injected traits. ZPP 1.x Markdown traits and its seven stage
skills are not migration inputs.
