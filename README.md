# ZPP 0.9.0

ZPP is a standalone profile and trait resolver. It composes concise advisory traits from user and project layers, then exposes the effective Markdown through one source-authoritative command.

## Install

Install the ZPP command with [uv](https://docs.astral.sh/uv/guides/tools/):

```console
uv tool install git+https://github.com/ZackaryW/zpp.git
zpp --version
```

ZPP requires Python 3.14 or newer. The installed command is independent from
the optional governance plugins an agent application may load.

## Initialize ZPP and agent hooks

```console
zpp init
zpp init --agent codex --agent claude --agent pi
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

With no explicit `--agent`, an interactive terminal offers Pi, Codex, and Claude Code. Noninteractive initialization skips agent setup. Selected ZPP hooks are installed in global user space:

- Pi: `~/.pi/agent/extensions/zpp/index.ts`
- Codex: `~/.codex/hooks.json`
- Claude Code: `~/.claude/settings.json`

`zpp init` installs only these ZPP lifecycle hooks. It does not install workflow
skills, third-party plugins, instruction paragraphs, repository-local
integrations, or trust settings.

## Install the standard workflow

ZPP's standard workflow skills have an independent lifecycle. Install them
globally for one or more supported agents:

```console
zpp workflow install --global --agent codex --agent claude --agent pi
```

For a repository-local installation, provide its path and omit `--global`:

```console
zpp workflow install C:\work\project --agent codex
```

A compatible global workflow normally supersedes a local installation. Use
`--force` only when the project intentionally needs its own projection.

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

## Update

Update the executable, reconcile the selected global hooks, and then update
ZPP's workflow bundle if it is installed:

```console
uv tool upgrade zpp
zpp init --agent codex --agent claude --agent pi
zpp workflow update --global --agent codex --agent claude --agent pi
```

For a repository-local workflow, pass its path to `zpp workflow update` instead
of `--global`. These commands update ZPP-owned surfaces only; agent plugins have
their own installation and update lifecycles.

Initialization never overwrites an existing valid `default` profile. That
profile is user-owned, so newly packaged defaults must be reviewed and adopted
explicitly rather than silently merged.

## Development

```console
uv sync --all-groups
uv run pytest
uv run behave
```
