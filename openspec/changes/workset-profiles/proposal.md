# Proposal: workset-profiles

## Why

Workset member bindings are a special mechanism (`bind`/`unbind`, a `store` field per member) that duplicates what config already expresses, lives only in a machine-local sidecar, and cannot be shared with collaborators. Profiles dissolve the special case: a workset carries named zpp.toml-style config blocks, members resolve to the `default` profile unless they point at another, and the whole thing can live in a committed `.zpp-workset` file next to the `.code-workspace` — shareable, and anchored to the same folder so relative paths resolve identically for both files.

## What Changes

- **Named profiles replace member bindings.** A workset config holds `[profiles.<name>]` blocks (zpp.toml-shaped). Every member resolves to `profiles.default`; a member entry may point elsewhere with `profile = "<name>"`. A store binding is just `[governance] store = "<id>"` inside a profile — `zpp workset bind`/`unbind` and the per-member `store` field are removed. **BREAKING** for existing sidecars carrying `store` fields.
- **Tier order unchanged, but the store tier is a profile too**: the store's published `default` profile → member's workset profile → repo `zpp.toml` (repo always wins; scalars override, lists union). **`zpp.default.toml` is removed** (**BREAKING**): a store publishes via `[profiles.*]` inside its own `zpp.toml` — top level stays the store repo's self-config, profiles are what it publishes. Governance resolution keeps its shape — rule 3 is now "the member's profile declares `[governance] store`" instead of the sidecar `store` field.
- **Profiles may extend one level**: `extends = "<name>"` merges the parent's config under the child's (child wins; no chains) — so a pointed profile can inherit `default`'s traits and add a binding.
- **Doctor checks shared-file correspondence**: a `.zpp-workset` `[members.X]` entry naming a member the workspace lacks is reported (typos were silently ignored).
- **Shared mode: the `.zpp-workset` file.** `<name>.zpp-workset` beside `<name>.code-workspace`, committed together. When present it is the source of truth for profiles and member pointers; members are referenced **by name only** — paths always derive from the `.code-workspace` on each machine. Without it, profiles live in the personal `~/.zpp` sidecar as today. Import/sync detect the file automatically.
- **Multi-workset membership rule**: when a repo is a member of several worksets, the alphabetically-first workset's profile applies and `zpp workset doctor` warns.
- `~/.zpp` keeps only machine-local state: the name→workspace registry, member path cache, snapshots, and personal profiles when no shared file exists. `ZPP_TRAITS` continues to replace the workset tier per session.

## Capabilities

### New Capabilities

<!-- none — this reshapes existing capabilities -->

### Modified Capabilities

- `workset-management`: bind/unbind requirement replaced by profiles (named blocks, default resolution, explicit pointers, shared `.zpp-workset` mode); status reports each member's live resolution and applied profile.
- `governance-resolution`: rule 3 re-sourced from member profiles; the layered-config middle tier becomes the member's profile.
- `trait-system`: application-tier wording updates from "workset sidecar overlay" to "member's workset profile" (env override semantics unchanged).

## Impact

- Code: `core/sidecar.py` (profiles model, shared-file loading), `core/worksets.py` (bind/unbind removed, profile pointers, doctor rules), `core/governance.py` (profile-sourced rule 3 and middle tier), `cli/workset.py` (`bind`/`unbind` commands removed; `status` shows profiles).
- Files: new `.zpp-workset` format (TOML); sidecar schema change (BREAKING; no migration shim — pre-1.0, owner-only installs).
- Tests: behave scenarios for profile resolution, shared-file mode, multi-workset warning; existing bind-based scenarios rewritten.
