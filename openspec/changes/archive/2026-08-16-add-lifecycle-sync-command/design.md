## Context

`reset_projections` already builds the complete per-agent asset set and pairs each entry with an inspection callable and a removal callable. `zpp reset` inspects then removes; `zpp init` projects unconditionally and, under `--force`, removes and reprojects. No command inspects and then repairs, so a machine whose packaged assets moved ahead of its projections has no recovery short of reprojecting everything.

Agent Router already reports the states this needs — `current`, `outdated`, `absent`, `unmanaged`, and `conflict` — and refuses to replace an artifact it did not install even when asked to force. That refusal is the boundary the design has to respect rather than work around.

## Goals / Non-Goals

**Goals:**

- Give each lifecycle command exactly one job: `init` creates, `sync` repairs, `reset` removes.
- Repair only what drifted, and say what was inspected rather than only what changed.
- Derive all three commands from one projection inventory.

**Non-Goals:**

- Changing `zpp reset` semantics, its preflight, or its ownership boundary.
- Adopting, deleting, or overwriting native assets outside Agent Router's projection contracts.
- Project-scope synchronization. `zpp workflow` retains its own scoped install, update, and remove.
- Changing `zpp workflow`'s unconditional JSON output, which remains as it is today.

## Decisions

**`--force` means "reproject owned entries regardless of observed state", not "take over foreign files".** Agent Router raises `ConflictError` for an unmanaged target and for a mismatched ownership record even when `force=True` is passed, so the stronger reading is unavailable without ZPP deleting files directly. That would contradict the canonical requirement that ZPP use Agent Router only through its public projection contracts, so the weaker reading is the only coherent one and the specification states the preservation explicitly rather than leaving it to be discovered.

**Any present ZPP projection makes an agent installed.** A partially projected agent is exactly the state synchronization exists to repair, so letting initialization complete it would restore the overlap this change removes. The rule is coarse deliberately: "some entries present" is a single observable condition, whereas "enough entries present to count" would need a threshold nothing else in the lifecycle defines.

**Initialization rejects per agent rather than per invocation.** Rejecting the whole invocation would make a single installed agent block setting up a new one, which is the common case when adding an agent to a machine that already runs ZPP. Per-agent rejection keeps each agent's outcome independent and reportable, and initialization already reports per-agent results.

**`init --force` is removed rather than repurposed as a rejection override.** Retaining it would leave two commands reprojecting owned artifacts identically, which is the ambiguity that made root initialization serve two purposes. Removing it is breaking for existing scripts, and the specification records the obsolete option explicitly so that supplying it fails rather than being silently ignored.

**The shared inventory carries projection alongside inspection and removal.** `reset_projections` already pairs inspection with removal; adding a projection callable makes one structure serve all three commands. The alternative, a second inventory for synchronization, reintroduces the drift between command asset sets that discovering companion skills by role was meant to eliminate.

## Risks / Trade-offs

Removing `init --force` breaks any script that reprojects by re-running initialization. There is no compatibility shim: the option is specified as rejected, so the failure is immediate and legible rather than silent. `zpp sync --force` is the replacement and covers the same intent.

Treating any present projection as installed means a genuinely broken half-installation cannot be repaired by initialization. Synchronization handles it, but a caller whose instinct is to re-run `init` gets a rejection with a pointer instead of a repair, which is one extra step.

Synchronization reports state for every entry, so its default output must aggregate rather than enumerate to stay one line. The existing lifecycle summary already aggregates by status and tolerates unknown statuses, so the observed states extend it without a new reporting shape.
