## Why

ZPP must become a standalone, breaking redesign that bootstraps and resolves profiles, traits, configuration, instructions, and skills without the removed `governance-of-agents-1v2` plugin. The existing application remnants describe a rejected product, so version `0.9.0` needs one owner-grounded contract before implementation resumes.

## What Changes

- **BREAKING**: Replace the old ZPP formats, commands, plugin gates, `2.0.0` version, and "ZPP v2" product identity without migration or compatibility behavior.
- Keep Typer and the established `src/zpp/artifacts`, `src/zpp/cli`, `src/zpp/core`, and `src/zpp/utils` package boundaries.
- Initialize an unconditional neutral `~/.zpp/global` layer, empty `profiles`, top-level `saved`, and independent `cached` root. Initialization is preflighted, all-or-nothing, byte-preserving for valid existing state, idempotent, and never creates project-local state or derived caches.
- Select an optional named user profile exclusively through `ZPP_PROFILE`. Unset means global only; a known value layers that profile after global; an unknown value fails. Do not persist, prompt for, bind through saved state, or accept a CLI override for the active profile.
- Resolve layers in this order: global, optional active profile, the closest matching saved override, repository-root `.zpp`, then nested `.zpp` layers from the Git root toward the target.
- Store reusable saved override layers under top-level `~/.zpp/saved/{name}` with a canonical-target index and independent caches. One valid saved name may bind multiple existing directories; repeated bindings are idempotent; an existing target cannot be silently rebound; the longest matching ancestor wins.
- Define each trait as one concise Markdown advisory document with YAML frontmatter. Require `name` and `description`; allow optional non-negative integer `order`, JSON-compatible mapping `config`, and ordered advisory `skill_lookup`. The filename stem equals `name`, unknown keys are invalid, and `skill_lookup` remains passive metadata.
- Keep `trait.json` as the exclusive activation owner. Initial rules contain `trait` plus zero or one fixed condition: `which` or recursive `workspace_contain`. A conditionless `{ "trait": "..." }` rule activates whenever its layer participates. Reject compound/additional keys, exclude `.git`, cache directories, and directory-symlink traversal, and deduplicate by first activation.
- Keep `config.json` limited to `trait_overwrites` and `traitsConfig`. `trait_overwrites` extends or replaces the accumulated trigger list only. Same-name authored documents are replaced completely by the later layer. `traitsConfig` never activates a trait and applies a shallow top-level overlay after the winning document is selected; configured names unavailable from every layer are invalid.
- Apply authored `order` after activation and document replacement. Explicitly ordered traits come first ascending; ties retain first-activation order; unordered traits follow in first-activation order. `traitsConfig` cannot override `order`, and no `before`/`after` graph exists initially.
- Compile each participating layer's authored Markdown collection lazily into one independent JSON cache plus freshness sidecar. Authored Markdown remains authoritative and byte-unchanged. Compilation is collection-wide and reports all source errors; stale data is never returned after a failed rebuild. Cache schema, validation matrices, timestamp edge cases, and atomic-write behavior belong to disposable utility planning and focused TDD rather than canonical specifications.
- Make `zpp resolve [TARGET]` resolve an existing directory, defaulting to the current directory, and emit complete effective trait documents in their native Markdown/frontmatter envelope. Empty activation succeeds with empty stdout. Do not expose public JSON, provenance, layer/source diagnostics, or cache introspection.
- Make `zpp init` bootstrap user state and then offer an interactive Pi/Codex/Claude Code multiselector. Repeatable `--agent pi|codex|claude` bypasses the selector; no option in a noninteractive session skips agent setup successfully. Submitting the interactive selector with no checked agents also succeeds without agent setup; aborting it through Ctrl+C/Escape cancels without agent changes. An existing valid user root skips only its filesystem bootstrap.
- Configure selected agents exclusively through global, user-home native lifecycle-hook mechanisms; never install agent integration into a repository-local `.codex`, `.claude`, or `.pi` directory and never install an instruction paragraph or skill. Codex receives one `SessionStart` command hook in `~/.codex/hooks.json` for `startup|resume|clear|compact`. Claude Code receives one `SessionStart` command hook in `~/.claude/settings.json` for `startup|resume|clear|compact|fork`. Both run `zpp resolve` in the session working directory and let the agent's native hook contract inject successful stdout as context. Pi receives one auto-discovered extension at `~/.pi/agent/extensions/zpp/index.ts`; its `before_agent_start` callback resolves the current working directory and appends successful output to that run's system prompt.
- Keep native hook execution source-authoritative: complete successful resolution output is injected exactly once for that lifecycle invocation, empty output injects nothing, and a resolution failure surfaces through the target agent without injecting stale or partial trait context. Native trust and enablement remain owned by the target agent. Installation never invokes trait resolution, creates a trait cache, or copies effective traits into the installed hook artifact.
- Make every selected-agent installation independently idempotent, preflight all selected targets before changing any agent, preserve unrelated native configuration semantically, reject invalid configuration or conflicting unmanaged ownership without overwrite, and leave unselected agents untouched.
- Support the public commands below. Creation is preflighted and idempotent. Removal requires confirmation and accepts `--yes`/`-y`; removing the profile named by `ZPP_PROFILE` does not alter the environment. Profile lists are lexical names; saved lists are canonical-target-ordered `NAME<TAB>TARGET`; empty lists succeed silently.

```text
zpp init [--agent pi|codex|claude]...
zpp profile create NAME
zpp profile list
zpp profile remove NAME [--yes|-y]
zpp profile saved create NAME TARGET
zpp profile saved list
zpp profile saved remove NAME [--yes|-y]
zpp local init [TARGET]
zpp resolve [TARGET]
zpp --version
zpp --help
```

- Use `^[a-z0-9][a-z0-9_-]*$` for profile and saved names. `saved create`, `local init`, and `resolve` targets must be existing directories; `local init` defaults to the current directory and additionally requires a Git worktree.
- Use Typer exit code `2` for usage failures and `1` for domain or managed-state rejection. Emit normal results on stdout, diagnostics on stderr, and read/write text explicitly as UTF-8. ZPP-owned JSON uses `ensure_ascii=false`; normal errors identify relevant sources without stack traces.
- Keep ZPP core policy-blind: profiles, generic trait configuration, resolution, and native agent-hook mounting are mechanisms. Workflow modes, platform/framework tools, and skill-use decisions belong to independently authored traits or later contracts; the hook adapters transport resolved guidance but define none.

## Capabilities

### New Capabilities

- `global-bootstrap-and-agent-setup`: neutral user-state initialization and opt-in Pi, Codex, and Claude Code integration.
- `profile-and-saved-lifecycle`: named-profile and independent reusable saved-layer lifecycle.
- `local-layer-initialization`: neutral repository and subfolder layer creation inside Git worktrees.
- `trait-compilation-and-cache`: source-authoritative trait validation, lazy collection compilation, and cache gating.
- `trait-resolution`: ordered layer discovery, fixed activation, replacement/configuration composition, and effective Markdown output.

Canonical specs for these capabilities are formed only after integrated behavior is mature and green.

### Modified Capabilities

None. This is a breaking replacement rather than a revision to an accepted canonical specification.

## Impact

- Replaces contradictory `README.md`, `pyproject.toml`, and `src/zpp/__init__.py` remnants during later implementation.
- Adds user-owned `~/.zpp` state and optional repository/subfolder `.zpp` layers.
- Removes runtime dependence on the old governance plugin.
- Coordinates utility and dependency work through a disposable planning gate that is deleted after the mature-utility checkpoint.

## Contract Ownership

This proposal owns product intent, scope, constraints, invariants, capability boundaries, and deferrals. The complete public examples and paths belong only to these feature files:

- [`bootstrap_and_agents.feature`](../../../features/bootstrap_and_agents.feature)
- [`profiles_and_saved.feature`](../../../features/profiles_and_saved.feature)
- [`local_layers.feature`](../../../features/local_layers.feature)
- [`trait_compilation.feature`](../../../features/trait_compilation.feature)
- [`trait_resolution.feature`](../../../features/trait_resolution.feature)

Parser/control-document validation matrices, cache-record normalization, timestamp and failure edge cases, path matching primitives, and atomic filesystem behavior belong to focused TDD. Their disposable utility plan is not specification input and is deleted after utility maturity. At the feature-contract checkpoint, the feature files had no step definitions or runner evidence; bindings and root-owned BDD integration occurred only after the complete utility foundation was mature and checkpointed.

## Workflow Authority

- Workflow decisions: [`establish-workflow-skills/proposal.md`](../establish-workflow-skills/proposal.md)
- Invocation order: [this change's README](README.md)
- Temporary local definitions: `.codex/skills/zpp-clarify-change`, `zpp-shape-feature`, `zpp-plan-utilities`, `zpp-mature-utilities`, `zpp-wire-feature`, `zpp-form-specs`, and `zpp-commit-zmem`

The temporary skills govern development only and later distill into traits. They are not hard-coded runtime product behavior. Platform-specific BDD for this project uses `uv run behave`, but that runner belongs to an independent platform trait and is not invoked during feature formation.

## Governance State

- The product proposal and complete five-file Gherkin contract are reconciled: native lifecycle hooks replace the rejected instruction/skill bootstrap, conditionless activation is explicit, and selector cancellation is distinct from an empty submission.
- Thin step definitions and integration fixtures bind all five feature files to the real Typer command surface. Root-owned verification passes 5 features, 55 scenarios, and 434 steps through `uv run behave`; the complete unit suite passes 45 tests.
- Checkpoint `6c261fc` records the accepted feature contract. Checkpoint `3c13429` records the preceding green utility foundation, fallback checkpoint `109da49` records the missing read-only batch-agent preflight boundary, and replacement utility checkpoint `9e59ad3` closes that reopened gate. Green integration checkpoint `6021688` records the complete wired product; canonical specification formation may now begin.
- Five canonical capability deltas now preserve the mature public behavior without duplicating concrete Gherkin examples or internal utility algorithms. `openspec validate build-zpp-system --strict` passes for the complete formed set, and specification-formation checkpoint `f607541` records the gate.
- The verified utility plan was discarded after replacement mature-utility checkpoint `9e59ad3`; focused tests, implementation, and checkpoint history remain its evidence and none of its planning detail enters canonical specs.
- Checkpoint `c4e390f` records the preceding native-hook correction and checkpoint `78eff3f` the earlier instruction/skill contract; both remain historical.
- Commit `12b0232` remains historical evidence of the premature executable-BDD interpretation; its old step binding is removed from the current tree. Commit `fec0752` remains premature partial utility evidence. Preserve both commits in history and count neither as a valid workflow checkpoint.

## Explicit Deferrals

- JSON-to-Markdown import or two-way synchronization.
- Dynamic, compound, or extensible trigger grammar beyond `which` and `workspace_contain`.
- Agent-side trait refresh outside the installed native lifecycle hooks.
- Agent applications beyond Pi, Codex, and Claude Code.
- Background watchers, content hashes, or cache source inventories.
- Profile selection other than `ZPP_PROFILE`.
- Repository/subfolder discovery outside Git worktrees.
- Public JSON resolution, provenance, diagnostics/introspection, compile, cache, status, doctor, import, or trait-editor commands.
- Old-format migration, compatibility behavior, and plugin distribution beyond the three built-in agent adapters.
