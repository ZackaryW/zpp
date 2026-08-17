## Why

ZPP can create a complete integration and remove one, but it cannot repair the one already installed. When packaged skills, companion skills, or the native hook move ahead of a machine's projections, the only recovery is `zpp init --force`, which reprojects every integration whether or not it drifted and gives no account of what was stale. `init` therefore serves two unrelated purposes, and neither the user nor the command can distinguish first-time setup from repair.

## What Changes

- Add `zpp sync`, which inspects every user-scope ZPP projection for the agents that already have an installation and reprojects only those reporting a drifted or absent state.
- Report each projection's observed state rather than only its mutation, so an unchanged integration is visibly current rather than silently skipped.
- Accept `--force` on `zpp sync` to reproject owned projections regardless of observed drift.
- Keep `unmanaged` and `conflict` projections reported and unmodified under every flag, because Agent Router refuses to replace an artifact it did not install and ZPP reaches it only through public projection contracts.
- **BREAKING** Reject `zpp init` per selected agent when that agent already carries any ZPP skill or hook at its target surface, directing it to `zpp sync` while still initializing the selected agents that carry none.
- **BREAKING** Remove `zpp init --force` and reject it as unsupported, leaving `zpp sync --force` as the only reprojection path.
- Treat an agent holding any ZPP projection as installed, so a partially projected agent is repaired by `zpp sync` rather than completed by `zpp init`.
- Select agents through the established interactive prompt and report through the human-readable lifecycle summary, keeping machine-readable output behind an explicit `--json` option rather than emitting it by default.
- Share one projection inventory across `init`, `sync`, and `reset` so the three lifecycle commands cannot describe different integrations.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `product-home-lifecycle`: Adds drift-selected synchronization as a distinct lifecycle operation, constrains root initialization to first-time projection, and requires one shared projection inventory across the lifecycle commands. Its Purpose broadens from home selection and reset to the complete integration lifecycle.

## Impact

- `src/zpp/cli/initialization.py`, `src/zpp/cli/reset.py`, a new `src/zpp/cli/sync.py`, and the command registry in `src/zpp/cli/application.py`.
- The shared projection inventory currently private to `reset_projections`.
- Existing scripted `zpp init` invocations against an installed machine begin failing and must move to `zpp sync`.
- `product-home-lifecycle` gains initialization rejection, which no capability currently owns. Root initialization behavior is presently split across `automatic-trait-hooks`, `openspec-skill-provisioning`, and `consolidated-workflow-skill`, none of which governs the command as a lifecycle operation. This change places the lifecycle rule with `reset` and its shared preflight rather than creating a fourth partial owner, and does not relocate the existing hook or skill provisioning requirements.

## Unresolved — Do Not Assume

None.
