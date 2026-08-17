# Workspace command contract

Use the installed coordination CLI as an internal provider. This reference
classifies its current command families; installed `--help` remains authority for
the executable and every option, argument, and nested command.

## Resolve the executable and state

1. Prefer the command environment already declared by the repository or agent.
   The executable may be directly available or exposed through that environment's
   runner. Do not install, upgrade, or substitute it implicitly.
2. Run `openlease --help` through that environment, then inspect help for the
   required command and nested subcommand.
3. Supply the selected ZPP home's exact `openlease` child through the provider's
   state-root option. The default selected home is `~/.zpp`; an explicit home
   replaces that default. Keep the selected home, provider state, repository
   targets, and generated worktree base as distinct paths.
4. Prefer structured output when current help supports it and use `jq` for JSON
   inspection. Preserve typed identifiers and fail on invalid input.

If the executable, command family, required option, or state-root control is not
present in current help, the requested operation is unavailable.

## Classify command families

| Purpose | Current family | Authority |
| --- | --- | --- |
| Observe workspace state | `status`, `plan`, `lockable` | Read-only |
| Register topology | `register repository`, `register authority` | Exact node mutation |
| Declare topology | `relate parent`, `relate dependency` | Exact relationship mutation |
| Create or associate durable work | `space create`, `space associate`, `associate`, `affect` | Exact workspace and target mutation |
| Change lease lifecycle | `lock`, `open`, `defer`, `isolate`, `release` | Exact workspace, authority, and lease mutation |
| Resolve retained work | `recover`, `finalize`, `handoff`, `abandon`, `cleanup` | Exact successor or disposition mutation |
| Reconcile integration paths | `reconcile plan`, `reconcile apply` | Plan is read-only; apply mutates one authorized path |
| Repair failed preparation | `preparation resume`, `preparation rollback` | Exact failed preparation mutation |

Other installed families are outside the requested workspace operation unless
the owner names them and current help proves their relevance. Never infer argv
from this table.

## Mutation gate

Before invoking a mutating family, preserve an evidence record with:

- installed executable and help revision observed in the current environment;
- selected ZPP home and exact provider state root;
- exact workspace, authority, repository, relationship, lease, successor,
  reconciliation path, and filesystem targets affected;
- relevant status, plan, and lockability output;
- proposed command assembled only from current help;
- explicit authority covering every affected target;
- rollback, recovery, or retained-state consequence reported by current evidence.

Re-inspect after execution. Do not reuse a reconciliation plan after its observed
state changes. Do not widen an authorized target set, choose a callback, resolve
a conflict, or perform destructive cleanup because another workflow gate passed.
