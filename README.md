# ZPP 0.9.0

ZPP is a standalone profile and trait resolver. It composes concise advisory traits from user and project layers, then exposes the effective Markdown through one source-authoritative command.

## Initialize

```console
zpp init
zpp init --agent pi --agent codex
```

Initialization creates neutral user state without modifying the current project:

```text
~/.zpp/
├── global/
│   ├── config.json
│   ├── trait.json
│   └── traits/
├── profiles/
│   └── default/
│       ├── config.json
│       ├── trait.json
│       └── traits/
├── saved/
│   └── _bindings.json
└── cached/
```

With no explicit `--agent`, an interactive terminal offers Pi, Codex, and Claude Code. Noninteractive initialization skips agent setup. Selected integrations are installed globally through each agent's native lifecycle mechanism:

- Pi: `~/.pi/agent/extensions/zpp/index.ts`
- Codex: `~/.codex/hooks.json`
- Claude Code: `~/.claude/settings.json`

ZPP does not install agent skills, instruction paragraphs, repository-local integrations, or trust settings.

## Profiles, saved overrides, and local layers

```console
zpp profile create work
zpp profile copy default work
zpp profile list
zpp profile remove work --yes
zpp global activate work

zpp profile saved create personal C:\work\project
zpp profile saved list
zpp profile saved remove personal --yes

zpp local init
zpp local init src\package
```

The persistent, user-owned `default` profile contains the platform-neutral
standard traits. Initialization creates it only when absent and never reapplies
bundled content over an existing valid default.

`zpp profile copy` copies authored profile bytes without copying cache state.
`zpp global activate` archives the prior global layer as a collision-safe
timestamped profile and copies the selected profile into global. Set
`ZPP_PROFILE` for a temporary, non-mutating profile layer after global state.
Saved overrides bind one reusable layer to one or more canonical existing
directories; the closest matching ancestor wins.

Repository and subfolder `.zpp` layers are opt-in and must be inside a Git worktree.

## Traits

Each trait is one Markdown file with YAML frontmatter:

```markdown
---
name: review-errors
description: Inspect the smallest relevant failure first
order: 100
config:
  useThis: true
skill_lookup:
  - error-review
---
Inspect the smallest relevant failure output before changing implementation.
```

`trait.json` owns activation. A rule can be conditionless or use one fixed `which` or `workspace_contain` condition:

```json
[
  {"trait": "review-errors"},
  {"trait": "python", "workspace_contain": ["**/*.py"]},
  {"trait": "git-tools", "which": "git"}
]
```

`config.json` controls trigger replacement and shallow per-trait configuration overlays:

```json
{
  "trait_overwrites": false,
  "traitsConfig": {
    "review-errors": {"useThis": false}
  }
}
```

## Resolve

```console
zpp resolve
zpp resolve C:\work\project
```

Resolution layers global, optional `ZPP_PROFILE`, the closest saved override, repository root, and nested `.zpp` directories toward the target. It emits complete effective Markdown documents on stdout. No active traits produces empty stdout.

Authored Markdown remains authoritative and byte-unchanged. Participating layers are compiled lazily into independent `traits.json` caches with certification sidecars; invalid or stale source never falls back to old trait output.

## Development

```console
uv sync --all-groups
uv run pytest
uv run behave
```
