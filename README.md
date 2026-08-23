# ZPP 2.0

ZPP resolves small, repository-oriented behavior traits for coding agents. It
ships a packaged workflow family with outcome entries, one lifecycle kernel,
bounded stages and OpenSpec adapters, and a separate repository verifier.
Workflow invariants and authority are owned by those skills, not by traits.

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
zpp init [--agent AGENT ...] [--json]
zpp open
zpp reset --yes [--json]
zpp resolve [TARGET] [--trait FAMILY ...] [--stage STAGE] [--facet NAME=VALUE ...] [--agent AGENT] [--explain]
zpp behave init
zpp behave COMMAND [--all | --target TARGET ... | --gate GATE | --base REV --head REV]
zpp trait init context|FAMILY [TARGET]
zpp lease acquire --root ROOT --change CHANGE [--root ROOT --change CHANGE ...]
zpp lease acquire --owner OWNER --member UUID:CHANGE [--member UUID:CHANGE ...]
zpp lease status
zpp lease audit --bundle UUID --path PATH [--path PATH ...]
zpp lease archive --bundle UUID --member UUID:CHANGE [--owner OWNER]
zpp lease complete|abandon --bundle UUID [--owner OWNER]
zpp bypass --reason TEXT --acknowledge -- COMMAND [ARG ...]
zpp workflow install|update|remove [--agent AGENT ...] [--target PATH | --global]
```

The root `--path` option selects ZPP's home. It defaults to `~/.zpp`, and every
Bundler lease command uses only that home's `bundler` child as managed
state. Merely selecting a home does not create it. `zpp open` creates the
selected home when absent and opens that exact directory in the native file
manager without initializing Bundler state or interpreting the other contents.

`zpp reset --yes` preflights every supported agent's ZPP-owned user-scope
workflow family, every packaged companion skill, and the `zpp-traits` hook
through Agent Router. If that preflight succeeds, reset removes those intact
packaged assets normally. It also inspects seven obsolete workflow identities
as removal-only tombstones: an Agent Router-owned obsolete projection is
removed through Agent Router, while an unmanaged or ownership-unsafe collision
is preserved and reported. Reset performs no OpenSpec detection, process
invocation, initialization, generation, or repair. Only after lifecycle
removals succeed does it replace the selected home's `bundler` child. It
preserves the home itself, repository `.zpp` documents,
`zpp.behave.yaml`, project-scope projections, plugins, worktrees, and unrelated
files. A removal failure leaves prior Bundler state unchanged and a retry
accepts assets already removed. Reset has no global-trait overwrite mode.
Successful reset prints one concise summary line by default; `--json` emits the
complete inspection, removal, and state report.

Resolution is read-only and creates no lease state. If the target is inside a
registered OpenSpec store, ZPP composes only that store's root-to-target parent
chain. Sibling stores never contribute.

Ordinary governed workflows pass repository roots and change names to `zpp lease
acquire`. ZPP then owns OpenSpec registration, `openspec/bundler.toml` preparation,
the durable owner stored in the selected ZPP home, and atomic Bundler acquisition.
Users and skills do not need to provide those internal identifiers. The explicit
`--owner` plus `--member UUID:CHANGE` form remains available for diagnosis and
recovery.

`ZPP_WORKFLOW_COORDINATION` may override automatic selection with strict version-1
JSON containing an optional `owner_id` and an optional `stores` map from absolute
repository roots to registered OpenSpec store IDs. Unknown or invalid fields fail
before bootstrap, and this variable can never disable leasing. For an exceptional
owner-authorized unleased operation, `zpp bypass` requires a reason and explicit
acknowledgement, prints a warning and exact child command to standard error, and
scopes bypass to that one child process. Bypass grants no mutation, archive,
checkpoint, verification, or lifecycle authority.

`--stage` accepts only `clarify`, `shape`, `plan-utilities`,
`mature-utilities`, `wire`, `form-specs`, or `finalize`. Stage is protected
invocation state: repository context, stored context, and evidence cannot author
it, and it is never serialized into descriptive `ZPP_CONTEXT`.

Agent values come directly from Agent Router. Repeated explicit values retain
first-seen order and are deduplicated. Required interactive selection offers
Codex, Claude Code, Pi, and Kimi in that order; cancellation occurs before any
projection. `resolve` accepts at most one agent because it reads that invoking
agent's effective plugin artifacts.

`zpp init` validates the complete packaged workflow family before projection,
then Agent Router installs that family together with `zpp-traits` and every
packaged companion skill in user scope. Initialization is independent of the
local OpenSpec executable and never generates or installs upstream OpenSpec
skills. Re-running `init` reports an already initialized agent and directs the
caller to `zpp sync`, which reconciles the same shared inventory. Successful
initialization prints one concise summary line by default; `--json` emits every
ordered Agent Router lifecycle result. The grouped `workflow` commands manage
the complete workflow family and native hook at project or user scope; they
expose no authoring-skill or OpenSpec option.

Packaged skills live under `zpp/artifacts/skills/{role}/{skill}`. The `workflow`
role must match the canonical family inventory and loads in entry, kernel,
stage, adapter, and repository-verifier order. Every skill in the `companion`
role is discovered by directory scan in deterministic name order. All are
projected and removed through the shared lifecycle inventory. A directory is a
skill only when it contains `SKILL.md`; a missing, invalid, or unexpected
workflow member fails family loading rather than yielding a partial inventory.

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

Native BDD execution does not require `zpp.behave.yaml`.
`zpps-verify-repository` may run an established repository Behave, Cucumber, or
other BDD surface directly from repository configuration or an explicit owner
choice.
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

The workflow kernel acquires one bundle before governed OpenSpec mutation. A
requested parent holds its descendant closure; independent roots requested
together form one atomic crew. Finalization audits changed OpenSpec paths,
records every archive, and completes the bundle only after all members archive.
Agent Router owns plugin discovery and every workflow skill and native hook
destination mutation.
The installed native context hook invokes `resolve` automatically: Codex and
Claude Code use JSON SessionStart hooks, Kimi uses a TOML SessionStart hook, and
Pi uses a TypeScript `before_agent_start` extension. There is no invocation
command, resolver skill, or UserPromptSubmit resolution hook. The workflow
family contains invariant workflow policy and does not bootstrap trait
resolution.

Packaged defaults are source assets under `zpp/artifacts/traits`; this is not a
required runtime collection layout. The standard families are `bdd`,
`bdd-structure`, `bdd-execution`, `tdd`, and `tooling`. They carry only
repository-selected language, framework, structure, mode, and tool
specialization. Ponytail dependency selection, build completeness,
zero-assumption reconciliation, BDD binding, and RED/GREEN invariants belong to
their owning workflow skills. Lease progression remains kernel behavior rather
than globally injected trait policy. ZPP 1.x Markdown traits and stage skills
are not migration inputs.
