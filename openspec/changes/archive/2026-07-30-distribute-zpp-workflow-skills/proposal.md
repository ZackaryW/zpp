## Why

The seven mature ZPP workflow skills contain procedural gates, tool boundaries, fallback handling, and verification authority that cannot be preserved in concise advisory traits. ZPP must distribute those skills as permanent owned artifacts without forcing every project to duplicate a compatible global installation.

## What Changes

- **BREAKING**: Replace the current product-wide prohibition on installing agent skills with an explicit, managed workflow-skill distribution capability. This change does not weaken the separate rule that native lifecycle hooks contain no copied workflow guidance or effective trait content.
- Retain all seven `zpp-*` workflow skills permanently. Traits remain smaller complementary advisory/configuration units and MAY reference stable skill names through passive `skill_lookup`; they do not replace or duplicate skill procedures.
- Support a conditionless automatic-workflow trait as the advisory coordinator for unattended progression. When active, it directs the agent to continue across satisfied workflow gates without routine approval pauses and uses passive `skill_lookup` to make the permanent workflow skills discoverable.
- Keep enforcement ownership in the permanent skills: each skill defines its prerequisite, artifact boundary, verification owner, checkpoint behavior, and failure stop. The automatic trait SHALL NOT make `skill_lookup` executable, bypass a failed gate, resolve an unsettled product decision, or independently authorize Git, destructive, or external mutations.
- Treat mechanical runtime enforcement through a ZPP state machine or native agent hook as outside this change. The trait coordinates agent behavior; the referenced skills provide the enforceable workflow contracts available to the agent.
- Store the authoritative packaged bundle under `src/zpp/artifacts/skills`, including each skill's `SKILL.md` and required resources or scripts. Installed global and project-local copies are projections, never additional sources of truth.
- Add a dedicated skill lifecycle independent from `zpp init` and `zpp local init`:

```text
zpp skill install [TARGET] [--global] [--agent pi|codex|claude]... [--force]
zpp skill update [TARGET] [--global] [--agent pi|codex|claude]...
zpp skill remove [TARGET] [--global] [--agent pi|codex|claude]... [--yes|-y]
```

- Support installation into either selected agents' user-global skill scope or an exact repository-local directory through agent-specific adapters. `--global` selects user scope and has no local target. Local scope defaults to the current directory, accepts an explicit existing directory inside a Git worktree, and does not create or modify an authored `.zpp` layer.
- Materialize Codex skills beneath `.agents/skills` or `~/.agents/skills`, Pi skills through the same shared `.agents/skills` projection, and Claude Code skills beneath `.claude/skills` or `~/.claude/skills`. Selecting Codex or Pi therefore targets their shared native projection rather than manufacturing duplicate agent-specific copies. Platform-specific paths and materialization rules SHALL remain outside the platform-neutral skill bodies.
- Treat the seven skills as one ZPP-owned bundle for installation and compatibility checks rather than seven unrelated folders.
- Reuse repeatable explicit agent selection and the established Pi/Codex/Claude interactive multiselector. Explicit agents bypass prompting. Interactive empty submission succeeds without changes and cancellation makes no changes. A noninteractive skill lifecycle invocation without explicit agents is a usage failure because it has no independent work to perform.
- Preflight the complete seven-skill bundle and every selected native destination before changing any selected destination. Any invalid or conflicting selected destination rejects the operation without partial writes.
- When project-local installation is requested and a compatible managed global bundle is present, skip the local projection by default. If the global bundle is absent or outdated, install the current bundle locally. `--force` SHALL materialize the current bundle locally even when the global bundle is compatible.
- Forced local and global projections deliberately coexist. ZPP SHALL NOT claim that one overrides the other because supported agents do not resolve same-named global and project skills uniformly. Every lifecycle operation SHALL detect and report differing managed scope versions without silently selecting one.
- Detect a ZPP-managed installation through owned bundle metadata and compatibility information, not folder names alone.
- Preserve unrelated agent state and reject invalid, conflicting, or user-owned destinations without overwrite. The force option bypasses global deduplication only; it does not authorize destructive replacement.
- Update only the explicitly selected scope and leave every other managed scope unchanged. Removal requires confirmation unless `--yes` or `-y` is supplied and removes only the selected ZPP-managed projection. Global updates SHALL NOT rewrite forced project-local projections.
- Preserve proposal-first ownership of intent and constraints while concrete user-visible examples move into the complete Gherkin feature set before utility planning or implementation.

## Capabilities

### New Capabilities

- `workflow-skill-distribution`: packaged ownership, global and repository-local installation, compatible-global deduplication, forced local projection, collision behavior, and safe managed lifecycle for the permanent workflow-skill bundle.

### Modified Capabilities

- `global-bootstrap-and-agent-setup`: revise the command surface and the existing no-agent-skills guarantee so permanent workflow skills can be installed through an explicitly accepted lifecycle without embedding them in native context hooks.

## Impact

- Adds packaged skill artifacts beneath `src/zpp/artifacts/skills` and agent-specific installation adapters beneath the established utility boundaries.
- Adds or revises public CLI behavior for installing and maintaining global and project-local workflow skills.
- Revises the canonical `global-bootstrap-and-agent-setup` behavior formed for ZPP 0.9.0.
- Keeps the current `.codex/skills/zpp-*` directories as uncommitted development sources until the accepted feature contract authorizes packaging work.
- Does not add platform/framework policy to the permanent skills or make `skill_lookup` executable.
