# trait-system

## MODIFIED Requirements

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

## ADDED Requirements

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
