# Repository verification

ZPP can coordinate affected verification declared by a repository. The mapping is
optional: native Behave, Cucumber, or another established BDD command can still be
run directly when a workflow selects it.

## Initialize the mapping

From the target Git worktree:

```powershell
zpp behave init
```

This initializes or validates the root `zpp.behave.yaml` as a dedicated raw Bundler
repository attachment. Direct initialization and execution do not create workflow
lease state.

For authoring or revising a real mapping, invoke the packaged
`zpp-configure-behave` companion skill. It discovers the repository's existing test
entry points and selects only the explicit `argv`, `nx`, or `go-task` providers that
ZPP supports.

## Mapping shape

A version-1 mapping declares commands, stable target identities, conservative path
rules, and optional workflow gates. This abbreviated example uses the `argv`
provider:

```yaml
version: 1
commands:
  bdd:
    provider:
      kind: argv
      argv: [uv, run, behave, "{targets}"]
    targets:
      core:
        value: features/core
        paths: [src/core/**]
      workflow:
        value: features/workflow
        paths: [src/workflow/**]
    gates:
      zpps-workflow-kernel: [workflow, core]
```

ZPP validates the YAML and executes only shell-free provider arguments declared by
the repository. It never infers executable command text from a prompt or installed
tool.

## Selection modes

Affected selection is the default:

```powershell
zpp behave bdd
```

The explicit alternatives are mutually exclusive:

```powershell
zpp behave bdd --all
zpp behave bdd --target core --target workflow
zpp behave bdd --gate zpps-workflow-kernel
zpp behave bdd --base origin/main --head HEAD
```

`--base` and `--head` must be supplied together. Repeated target identities are
deduplicated while preserving declaration order. A gate resolves only a configured
command-local target set; an unknown gate does not fall back to another mode.

Mapping presence never starts verification. Only an explicit `zpp behave COMMAND`
invocation executes the configured provider.

## Native BDD remains independent

`zpp.behave.yaml` is coordination, not a requirement for BDD. A workflow can run an
established repository Behave, Cucumber, or other BDD surface directly from current
repository configuration or an explicit owner choice.

BDD itself is applicable only to accepted public-system behavior. Pure function
matrices belong in focused unit tests, and documentation or non-observable policy
must not receive wording tests or synthetic scenarios merely to satisfy a workflow
stage.
