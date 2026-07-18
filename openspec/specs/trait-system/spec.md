# trait-system

## Purpose

Serve agent instruction fragments ("traits") in realtime from layered content sources, replacing compiled agent files. Content comes from four sources with fixed precedence; which traits *apply* comes from the governance config tiers. No composer, no build step.

## Requirements

### Requirement: Trait content sources with fixed precedence
zpp SHALL resolve trait content from four sources — `~/.zpp/user/` (user-registered markdown files), builtin trait files shipped inside the zpp package, agent-surface plugins (gathered live per `--tool`, see the gathering requirement), and `~/.zpp/saucepan/` (remote packs fetched by saucepan) — with name-collision precedence `user > builtin > plugin > saucepan`. A trait's name SHALL be its filename stem. Neither remote packs nor plugins SHALL be able to shadow a user or builtin trait name.

#### Scenario: User trait shadows builtin
- **WHEN** `~/.zpp/user/ponytail.md` exists and a builtin `ponytail` also exists
- **THEN** `zpp trait show ponytail` returns the user file's content and reports source `user`

#### Scenario: Remote pack cannot shadow a builtin
- **WHEN** a saucepan-fetched pack contains `structure.md` and a builtin `structure` exists
- **THEN** resolution returns the builtin content, and `zpp trait list` shows the remote copy as shadowed

#### Scenario: Plugin cannot shadow a builtin
- **WHEN** a gathered plugin ships `traits/ponytail.md` and a builtin `ponytail` exists
- **THEN** resolution returns the builtin content, and `zpp trait list --tool <surface>` shows the plugin copy as shadowed

#### Scenario: Plugin outranks a remote pack
- **WHEN** a gathered plugin and a saucepan pack both provide `acme-style` and neither name matches a user or builtin trait
- **THEN** resolution returns the plugin copy and marks the saucepan copy shadowed

#### Scenario: Builtin discipline set is present
- **WHEN** zpp is installed with no user or saucepan traits
- **THEN** `zpp trait list` includes at least `ponytail`, `structure`, `coverage`, and `commit-stage` with source `builtin`

### Requirement: Realtime trait query surface
zpp SHALL serve trait content in realtime through `zpp trait list` (every available trait with its source, shadowing, and version when known), `zpp trait show <name>` (one trait's content), and `zpp trait effective [path]` (the applied set for a context, concatenated in application order). All three SHALL support `--json`; `effective --json` SHALL carry per-trait provenance (source and which config tier applied it). No compiled agent artifact SHALL be produced or required.

#### Scenario: Effective set for a governed context
- **WHEN** the store tier applies `["ponytail"]` and the repo `zpp.toml` applies `["structure"]`
- **THEN** `zpp trait effective` outputs ponytail then structure content concatenated, and `--json` attributes each to its tier

#### Scenario: Unknown trait fails loudly
- **WHEN** an applied trait name resolves to no source
- **THEN** `zpp trait effective` reports the unknown name as a warning and continues with the remaining traits

### Requirement: Trait application tiers with session env override
The active trait set SHALL be computed from the existing config layering — store defaults, then the member's resolved workset profile, then repo `zpp.toml` — as a `[traits] apply` list per tier, unioned in tier order. When the `ZPP_TRAITS` environment variable is set (comma-separated names), it SHALL replace the workset-profile tier only, for that invocation; store and repo tiers SHALL always survive an env override.

#### Scenario: Env replaces only the personal tier
- **WHEN** the member's profile applies `["coverage"]`, the repo applies `["structure"]`, and `ZPP_TRAITS=ponytail` is set
- **THEN** the effective set is the store tier plus `ponytail` plus `structure` — `coverage` is absent and `structure` cannot be removed by the env

#### Scenario: Profile-applied traits reach every member
- **WHEN** a workset's `default` profile applies `["ponytail"]` and a member repo applies nothing itself
- **THEN** that member's `zpp trait effective` includes ponytail attributed to the workset tier

#### Scenario: Provenance names the env tier
- **WHEN** `ZPP_TRAITS` is active
- **THEN** `zpp trait effective --json` attributes env-applied traits to `env`, not `workset`


### Requirement: saucepan-backed remote sources in managed mode
zpp SHALL fetch remote trait packs via the saucepan CLI, invoked through an adapter. In the default `managed` mode, zpp SHALL fetch the saucepan release binary for the current platform into `~/.zpp/bin/` on first use and invoke it from there; with `[traits] saucepan = "system"`, zpp SHALL require saucepan on PATH and never install it. Remote refs SHALL be bare names; sources are declared centrally in saucepan's configuration, never inside trait refs.

#### Scenario: Managed fetch on first use
- **WHEN** no saucepan binary exists under `~/.zpp/bin/` and a remote trait operation runs in managed mode
- **THEN** zpp fetches the release binary, reports the fetch explicitly, and completes the operation with it

#### Scenario: System mode never installs
- **WHEN** `[traits] saucepan = "system"` and saucepan is not on PATH
- **THEN** the operation fails with guidance to install saucepan; nothing is written to `~/.zpp/bin/`

### Requirement: Per-tool live plugin gathering
The `zpp trait list`, `zpp trait show`, and `zpp trait effective` commands SHALL accept a `--tool <surface>` option naming exactly one agent surface (e.g. `claude`, `codex`). When present, zpp SHALL gather that surface's plugin traits live for that invocation — resolving the surface's installed plugins and reading each plugin's `traits/*.md` — and fold them into the result as the `plugin` source. When `--tool` is absent, no plugin gathering SHALL occur and the result SHALL be identical to a run without any plugin source. zpp SHALL NOT write a plugin-trait cache to disk and SHALL NOT provide a separate populate command.

#### Scenario: Tool flag folds in that surface's plugin traits
- **WHEN** a Claude plugin ships `traits/acme-style.md` and the user runs `zpp trait list --tool claude`
- **THEN** `acme-style` appears with source `plugin` and provenance naming the tool and plugin

#### Scenario: No tool flag means no plugin gathering
- **WHEN** the same Claude plugin is installed and the user runs `zpp trait list` without `--tool`
- **THEN** `acme-style` does not appear and the listing equals the no-plugin result

#### Scenario: A plugin without a traits folder contributes nothing
- **WHEN** an installed plugin ships skills but no `traits/` folder and the user runs `zpp trait list --tool claude`
- **THEN** that plugin contributes no traits

#### Scenario: Same-name collision within the plugin tier is visible
- **WHEN** two gathered plugins both ship `traits/acme-style.md`
- **THEN** the later-gathered copy wins and `zpp trait list --tool claude` shows each copy's `tool/plugin` provenance

### Requirement: Cross-platform plugin resolution with per-surface override
Plugin resolution SHALL be performed by a per-surface resolver that determines the surface's base directory according to the operating system. A `[traits] plugins` config table MAY override the base directory per surface (`plugins.claude`, `plugins.codex`); when an override is set it SHALL take precedence over the resolver's auto-detected path. Only trait content (`traits/*.md`) SHALL be extracted from a resolved plugin; skills, scripts, and manifests SHALL be ignored.

#### Scenario: Override wins over auto-detection
- **WHEN** `[traits] plugins.claude` points at a directory and `zpp trait list --tool claude` runs
- **THEN** plugins are resolved from the override path, not the OS default

#### Scenario: Only traits are extracted
- **WHEN** a resolved plugin contains `skills/`, `scripts/`, `plugin.json`, and `traits/x.md`
- **THEN** only `x` is gathered as a trait
