# OpenSpec and Bundler coordination

OpenSpec Bundler owns repository attachments, store topology, durable owners, and
atomic leases. ZPP owns trait document decoding, topology-aware composition,
workflow coordination, and the public lease commands.

## Store topology

A store declares its UUID, optional parent, and ZPP namespace in
`openspec/bundler.toml`:

```toml
version = 1
uuid = "8f85ef9f-d18a-4787-903e-1ecb920acb77"
parent = "52b7223b-3d15-4e8a-98f7-d8ddc90fbf1c"

[extensions.zpp-traits]
```

Trait resolution composes only the selected store's root-to-target parent chain.
When a governed workflow mutates OpenSpec, the workflow kernel acquires one bundle
for the exact targets before the mutation begins.

A requested parent holds its descendant closure. Independent roots requested
together form one atomic crew, so a partial multi-store acquisition is not accepted.

## Ordinary acquisition

Workflows normally provide repository roots and change names:

```powershell
zpp lease acquire --root C:\repo-a --change add-auth
zpp lease acquire `
  --root C:\repo-a --change add-auth `
  --root C:\repo-b --change update-client
```

ZPP then owns OpenSpec registration, `openspec/bundler.toml` preparation, durable
owner selection from the ZPP home, topology resolution, and atomic acquisition.
Users and skills do not need to calculate store UUIDs or owner IDs.

The explicit diagnostic form remains available for recovery:

```powershell
zpp lease acquire --owner OWNER --member UUID:CHANGE --member UUID:CHANGE
```

## Inspect and finish

```text
zpp lease status
zpp lease audit --bundle UUID --path PATH [--path PATH ...]
zpp lease archive --bundle UUID --member UUID:CHANGE [--owner OWNER]
zpp lease complete --bundle UUID [--owner OWNER]
zpp lease abandon --bundle UUID [--owner OWNER]
```

Finalization audits changed OpenSpec paths, records each observed archive, and
completes the bundle only after every member is archived and every required gate
succeeds. `abandon` releases a retained bundle without claiming that its members were
archived.

## Coordination overrides

`ZPP_WORKFLOW_COORDINATION` can override automatic selection with strict version-1
JSON containing an optional `owner_id` and optional `stores` mapping from absolute
repository roots to registered OpenSpec store IDs. Unknown or invalid fields fail
before bootstrap. The variable cannot disable leasing.

## Exceptional bypass

An owner can explicitly run one child command without Bundler coordination:

```powershell
zpp bypass --reason "emergency diagnosis" --acknowledge -- COMMAND ARG...
```

ZPP prints a warning and the exact child command to standard error, and the bypass is
scoped to that child process. Bypass does not grant mutation, archive, checkpoint,
verification, or lifecycle authority.

Reminder state is independent of this lifecycle. See [Agent workflows](workflows.md)
for target-scoped reminder runs.
