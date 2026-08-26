# CLI reference

This page records the current public command shapes. Run `zpp COMMAND --help` for
the complete option descriptions provided by the installed version. The rendered
top-level command screen is shown on the [project home page](../README.md).

## Global options

```text
zpp [--version] [--path PATH] [--install-completion] [--show-completion] COMMAND
```

`--path` selects the ZPP home containing managed Bundler state. It defaults to
`~/.zpp`.

## Lifecycle and home

```text
zpp init [--agent AGENT ...] [--json]
zpp sync [--agent AGENT ...] [--force] [--json]
zpp open
zpp reset [--yes] [--json]
```

See the root [Getting started](../README.md#getting-started) section for installation
and first use. The ZPP home defaults to `~/.zpp`; `zpp open` creates and opens the
selected home, while `zpp reset --yes` removes intact user-scope integrations and
replaces only its managed Bundler state.

## Resolution and trait documents

```text
zpp resolve [TARGET] [--stage STAGE] [--facet NAME=VALUE ...]
            [--trait FAMILY ...] [--agent AGENT] [--explain]
zpp trait init DOCUMENT [TARGET]
```

`DOCUMENT` is `context` or one exact trait-family name. See
[Traits and resolution](traits.md).

## Repository verification

```text
zpp behave COMMAND [--all | --target TARGET ... | --gate GATE |
                    --base REV --head REV]
```

`COMMAND` can be `init` or a command declared in `zpp.behave.yaml`. See
[Repository verification](verification.md).

## Workflow installation and reminders

```text
zpp workflow install|update|remove
    [--agent AGENT ...] [--target PATH | --global]

zpp workflow run start WORKFLOW --root ROOT --change CHANGE
zpp workflow run status --root ROOT --change CHANGE
zpp workflow run stop --root ROOT --change CHANGE
zpp workflow run check --root ROOT --change CHANGE --component COMPONENT
    [--workflow WORKFLOW]
zpp workflow run record --root ROOT --change CHANGE
    --component COMPONENT --result RESULT [--bundle UUID]
zpp workflow run remind [ROOT]
zpp workflow run stage insert --root ROOT --change CHANGE --id ID
    --component COMPONENT [--before ID | --after ID]
zpp workflow run stage delete --root ROOT --change CHANGE --id ID
zpp workflow run stage modify --root ROOT --change CHANGE --id ID
    --component COMPONENT
zpp workflow run stage upsert --root ROOT --change CHANGE --id ID
    --component COMPONENT [--before ID | --after ID]
```

See [Agent workflows](workflows.md) for family composition, reminder semantics, and
authority boundaries.

## Bundler leases

```text
zpp lease acquire --root ROOT --change CHANGE
    [--root ROOT --change CHANGE ...]
zpp lease acquire --owner OWNER --member UUID:CHANGE
    [--member UUID:CHANGE ...]
zpp lease status
zpp lease audit --bundle UUID --path PATH [--path PATH ...]
zpp lease archive --bundle UUID --member UUID:CHANGE [--owner OWNER]
zpp lease complete --bundle UUID [--owner OWNER]
zpp lease abandon --bundle UUID [--owner OWNER]
```

See [OpenSpec and Bundler coordination](coordination.md).

## One-command bypass

```text
zpp bypass --reason TEXT --acknowledge -- COMMAND [ARG ...]
```

Bypass is exceptional and applies only to the child command. It does not grant any
other workflow authority.
