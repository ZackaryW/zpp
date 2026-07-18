# Design: workset-traits

## Context

bootstrap-zpp-core (feat `80e468b`) established the tier resolution (store → workset sidecar → repo, scalars override / lists union) and the sidecar `[overlay]` section — the application half of a trait system. The governance store's agent-compose holds the content half today: shards bundled by presets, compiled by compose.py into agent files. zmem records the store's own intent: sectioned config was designed so "a later domain is a new section with no resolver change" — `[traits]` is that section.

Owner decisions from the pv-clarify interview: drop the composer (realtime queries are cheap); trait content is machine-level (`~/.zpp/user`, `~/.zpp/saucepan`) plus builtins shipped in the package; precedence `user > builtin > saucepan`; saucepan managed-mode default; generic discipline shards (`ponytail`, `structure`, `coverage`, `commit-stage`) become zpp builtins so zpp self-manages; this change is built under fail-first BDD (behave) + TDD (pytest).

## Goals / Non-Goals

**Goals:**

- Realtime trait queries replace compiled agents: `zpp trait list | show | effective`.
- Three content sources with deterministic precedence and per-trait provenance.
- Session-scoped trait override (`ZPP_TRAITS`) that can never shed committed discipline.
- saucepan integration behind an adapter, managed binary by default.
- zpp self-managed: its own sessions consume its builtin traits (dogfood).
- Fail-first BDD/TDD, declared in `zpp.toml`, scenarios in `features/`.

**Non-Goals:**

- No composer, no compiled agent files, no preset compilation — dropped, not deferred.
- No changes to governance-of-agents-1 (its shards/presets stay until it adopts zpp traits).
- No trait content authoring format beyond markdown files.
- No store-level source allowlist this round — precedence (builtins unshadowable by remote) is the guard; an allowlist can layer on later if remote sources multiply.
- No workset-membership-based ambient application for rule-2 repos — `ZPP_TRAITS` or repo config covers those sessions explicitly.

## Decisions

### D1: Realtime queries, composer dropped

Agents run `zpp trait effective [path]` at session start (or `show <name>` on demand) and receive content directly; nothing is compiled or cached as an artifact. Rationale: queries are cheap (local file reads after fetch), and compiled agents drift from their sources — the entire build-agents.sh/provenance-stripping machinery in the governance store exists to fight a problem that disappears when there is no build. Consequence: presets die with the composer; a "bundle" is just a trait list in a config tier.

### D2: Three content sources, precedence `user > builtin > saucepan`

```
~/.zpp/user/*.md          user-registered, highest
<package>/traits/*.md     builtin, shipped in the wheel
~/.zpp/saucepan/**/*.md   remote packs, lowest
```

User wins so local experimentation always sticks. Builtin beats remote so a remote pack can never silently shadow shipped discipline — this precedence IS the supply-chain guard, replacing an allowlist for now. Name-based refs stay bare (`ponytail`); sources are declared centrally (saucepan config), never inside refs.

### D3: Builtin traits = the generic discipline set

`ponytail`, `structure`, `coverage`, `commit-stage` move into the zpp package as data files. They are stack-agnostic; Pathverse-specific shards (pz-requirements, webapp0-governance, clarify-bdd, implement-tdd, flow-overview, preferred-tooling) stay in the governance store. This makes the dogfood rule real: a zpp agent session's discipline comes from zpp itself.

### D4: Application tiers unchanged; `ZPP_TRAITS` replaces the workset tier only

Active-trait resolution reuses the existing config layering with a `[traits] apply = [...]` list per tier: store defaults → (workset sidecar overlay | `ZPP_TRAITS` env, whichever — env wins for the session) → repo `zpp.toml`, lists union. The env var replaces only the personal tier, mirroring `PVA_ALLOW_NO_STORE`'s ephemeral-bypass doctrine: committed tiers always survive, so discipline traits placed in store/repo config cannot be shed by a session. Provenance attribution reports `env` when active.

### D5: saucepan behind an adapter, managed mode default

`core/sauce.py` mirrors the openspec adapter pattern (subprocess + `--json` + typed errors — saucepan is explicitly middleware-shaped: stable exit codes, JSON reads). Managed mode (default): zpp fetches the saucepan release binary for the current platform into `~/.zpp/bin/` on first use and invokes it from there; `[traits] saucepan = "system"` requires it on PATH instead and never installs. Doctor reports the active mode and binary provenance. Only the adapter knows saucepan's CLI; a source-format change touches one file.

### D6: BDD/TDD discipline, declared in-protocol

`zpp.toml` at the repo root declares `[tdd] stack = "python"` and `[bdd] stack = "python"` — the repo states its own discipline per protocol rule, and zpp's config resolution can serve it. behave (dev dependency, via uv) runs `features/*.feature`; scenarios are written to fail first, then implemented; pytest remains the unit layer under the same fail-first rule. Side benefit: zmem parses `features/*.feature` diffs into scenario nodes, so the BDD layer writes memory.

### D7: Trait file model

A trait is one markdown file, name = filename stem (kebab-case). Remote packs may carry `sauce.json` (name/version) — version surfaces in `trait list` provenance. No front-matter schema this round; content is opaque to zpp.

## Risks / Trade-offs

- [Realtime queries make agents depend on zpp being installed] → acceptable and intended (dogfood); `trait effective` degrades loudly, not silently, when a source dir is missing.
- [No allowlist: any saucepan-declared source can supply new trait names] → precedence caps the blast radius (cannot shadow user/builtin); revisit an allowlist when sources go beyond owner-controlled repos.
- [Managed binary fetch is a network dependency at first use] → fetch is explicit in output, pinned to a release version recorded in config; `system` mode opts out entirely.
- [ZPP_TRAITS typos silently change a session's trait set] → `trait effective` prints unknown-name warnings; doctor validates env refs when set.
- [Builtin shards fork from the governance store's copies] → intentional: builtins become the canonical home; the store's copies are legacy until it adopts zpp traits (out of scope here).
- [behave adds a second test runner] → bounded: scenarios drive the trait capability only; pytest keeps everything else.

## Open Questions

- saucepan release pinning: exact version knob location (`[traits] saucepan_version`?) — decide at implementation with a sane default of "latest at first fetch, then pinned".
- Whether `trait effective` should cache per-session (env-keyed) — only if measured cost warrants it; default is no cache.
