# trait-system

## ADDED Requirements

### Requirement: Trait content sources with fixed precedence
zpp SHALL resolve trait content from three sources — `~/.zpp/user/` (user-registered markdown files), builtin trait files shipped inside the zpp package, and `~/.zpp/saucepan/` (remote packs fetched by saucepan) — with name-collision precedence `user > builtin > saucepan`. A trait's name SHALL be its filename stem. Remote sources SHALL NOT be able to shadow a user or builtin trait name.

#### Scenario: User trait shadows builtin
- **WHEN** `~/.zpp/user/ponytail.md` exists and a builtin `ponytail` also exists
- **THEN** `zpp trait show ponytail` returns the user file's content and reports source `user`

#### Scenario: Remote pack cannot shadow a builtin
- **WHEN** a saucepan-fetched pack contains `structure.md` and a builtin `structure` exists
- **THEN** resolution returns the builtin content, and `zpp trait list` shows the remote copy as shadowed

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
The active trait set SHALL be computed from the existing config layering — store defaults, then the workset sidecar overlay, then repo `zpp.toml` — as a `[traits] apply` list per tier, unioned in tier order. When the `ZPP_TRAITS` environment variable is set (comma-separated names), it SHALL replace the workset sidecar tier only, for that invocation; store and repo tiers SHALL always survive an env override.

#### Scenario: Env replaces only the personal tier
- **WHEN** the workset overlay applies `["coverage"]`, the repo applies `["structure"]`, and `ZPP_TRAITS=ponytail` is set
- **THEN** the effective set is the store tier plus `ponytail` plus `structure` — `coverage` is absent and `structure` cannot be removed by the env

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
