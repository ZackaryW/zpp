# ZPP

ZPP gives coding agents repository-specific working guidance without copying a
large, universal prompt into every project. It resolves small trait families from
the current repository and selected stores, installs a bounded workflow family for
supported agents, coordinates governed OpenSpec work, and runs repository-owned
verification.

## What it looks like

```text
PS C:\Users\ZackaryWang\Documents\GitHub\zpp> zpp

 Usage: zpp [OPTIONS] COMMAND [ARGS]...

 Resolve repository-oriented workflow traits for coding agents.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --version                                                          │
│ --path                      <path>  ZPP home containing managed    │
│                                     Bundler state.                 │
│ --install-completion                Install completion for the     │
│                                     current shell.                 │
│ --show-completion                   Show completion for the        │
│                                     current shell, to copy it or   │
│                                     customize the installation.    │
│ --help                              Show this message and exit.    │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ init      Set up the consolidated workflow for agents that carry   │
│           no ZPP projection.                                       │
│ sync      Bring installed ZPP integrations up to par with the      │
│           packaged assets.                                         │
│ open      Create and open the selected ZPP home.                   │
│ reset     Remove ZPP user integrations and replace managed Bundler │
│           state.                                                   │
│ resolve   Resolve repository, invoking-agent, and packaged trait   │
│           sources.                                                 │
│ behave    Run repository-owned affected verification through       │
│           zpp.behave.                                              │
│ bypass    Run one explicitly acknowledged child without Bundler    │
│           coordination.                                            │
│ trait     Initialize exact repository trait attachments through    │
│           Bundler.                                                 │
│ lease     Operate the Bundler lease lifecycle governed by          │
│           zpps-workflow-kernel.                                    │
│ workflow  Manage the packaged workflow family and hook through     │
│           Agent Router.                                            │
╰────────────────────────────────────────────────────────────────────╯
```

## Getting started

ZPP requires Python 3.12 or newer. Install it directly from the Git repository with
[`uv`](https://docs.astral.sh/uv/):

```powershell
uv tool install git+https://github.com/ZackaryW/zpp.git
```

Initialize ZPP for one or more supported agents, then inspect the guidance selected
for a repository:

```powershell
zpp init --agent codex
zpp resolve C:\path\to\repository --agent codex --explain
```

ZPP currently integrates with Codex, Claude Code, Kimi, and Pi through Agent Router.
Normal resolution prints the selected instruction bodies; `--explain` adds the
context, evidence, provenance, and deterministic selection decisions.

## Documentation

- [Traits and resolution](https://github.com/ZackaryW/zpp/blob/main/docs/traits.md)
- [Agent workflows](https://github.com/ZackaryW/zpp/blob/main/docs/workflows.md)
- [Repository verification](https://github.com/ZackaryW/zpp/blob/main/docs/verification.md)
- [OpenSpec and Bundler coordination](https://github.com/ZackaryW/zpp/blob/main/docs/coordination.md)
- [CLI reference](https://github.com/ZackaryW/zpp/blob/main/docs/cli.md)

The repository is licensed under the terms in
[LICENSE](https://github.com/ZackaryW/zpp/blob/main/LICENSE).
