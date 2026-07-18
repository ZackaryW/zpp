# Design: workset-profiles

## Context

Today the sidecar carries a `store` field per member (rule 3: personal binding) plus a single workset-wide `[overlay]`. That mixes two jobs — composition and governance — in one machine-local file, requires dedicated bind/unbind machinery, creates a second source of governance truth that doctor must reconcile, and cannot be shared. The owner's direction, converged over the clarify conversation: config profiles instead of bindings; `default` is a profile, not a mechanism; repo files always win; shared mode via a paired file in the workspace folder.

## Goals / Non-Goals

**Goals:**

- One concept (profiles) replaces two (bindings + overlay).
- Collaboration: a committed `.zpp-workset` file gives every teammate the same profiles.
- Portability: shared files carry no absolute paths — names only; paths derive from the `.code-workspace`.

**Non-Goals:**

- No migration shim for old sidecars (pre-1.0; BREAKING accepted).
- No per-member config outside profiles (a member points at a profile; it does not carry inline config).
- No change to `ZPP_TRAITS` (still replaces the workset tier per session) or to snapshot scope.

## Decisions

### D1: Profiles are zpp.toml-shaped named blocks; `default` is just a name

`[profiles.<name>]` sections hold the same shape as any zpp.toml tier (`[governance]`, `[traits]`, `[zmem]`, `[doctor]`, …). Every member resolves to `profiles.default` unless its entry says `profile = "<name>"`. No special default machinery: absence of `profiles.default` simply means members with no pointer get an empty middle tier.

### D2: Binding is config, not machinery

`[governance] store` inside a profile is the personal/shared binding. `bind`/`unbind` commands and the member `store` field are deleted. Governance resolution keeps its rule order — local root → repo `zpp.toml` → workset (now: member's profile) → ungoverned — so "repo beats profile" holds for bindings exactly as it does for every other key.

### D3: The `.zpp-workset` shared file

`<stem>.zpp-workset` sits beside `<stem>.code-workspace` (same folder, same relative-path anchor, committed together). TOML: `[profiles.*]` plus `[members.<name>]` entries carrying only `profile` pointers — never paths. When the file exists, it is the source of truth for profiles/pointers; the `~/.zpp` sidecar keeps machine-local state only (workspace path, member path cache from import/sync, snapshots). When absent, profiles live in the sidecar (personal mode, today's behavior). Import and sync detect the file by name pairing; zpp MAY write it only via explicit profile-editing commands — sync never creates or deletes it.

### D4: Multi-workset membership

A repo in several worksets takes the alphabetically-first workset's profile; doctor warns with the full list. Deterministic and visible; union across worksets was rejected — merging two profiles from unrelated views invites silent scalar collisions.

### D5: Store tier is a profile too - zpp.default.toml removed

"Default is a profile" applies at every tier: a store publishes by declaring `[profiles.default]` (and others) inside its own `zpp.toml`; the top level of that file remains the store repo's self-config and is never inherited by governed repos. `zpp.default.toml` no longer exists (BREAKING). Self-governed repos read both layers from one file: the default profile as the store tier, the top level as the repo tier.

### D6: One-level profile extends

`extends = "<name>"` merges the parent's config under the child's (child wins, standard merge). One level only - a parent's own extends is ignored - so chains cannot form. Motivated by the demonstrated need: a pointed profile wanting default's traits plus a store binding.

### D7: Doctor checks shared-file correspondence

Every `[members.X]` entry in a `.zpp-workset` must name a real workspace member; mismatches (typos) were silently ignored and are now doctor findings.

### D8: Fail-first discipline

behave scenarios drive: default-profile resolution, explicit pointer, repo-overrides-profile, profile-sourced store binding (rule 3), shared-file mode (names-only portability), personal fallback, multi-workset warning. Existing bind-based scenarios and units are rewritten, not kept alongside.

## Risks / Trade-offs

- [BREAKING sidecar schema] → accepted pre-1.0; doctor reports unreadable/legacy sidecars with a re-import suggestion.
- [Shared file is a committed voice able to bind repos to stores] → same trust level as a committed `zpp.toml` — it is reviewed, versioned team config, strictly weaker than the repo's own file, and builtin traits remain unshadowable.
- [Two possible profile homes (shared file vs sidecar)] → precedence is absolute (file present → file wins entirely; no merging between homes), and status/doctor name which home is active.
- [Alphabetical multi-workset rule can surprise] → doctor warning names the winner and the shadowed worksets.

## Open Questions

- Profile-editing CLI surface (`zpp workset profile set/show`?) — decide at implementation; hand-editing the TOML is acceptable for this round.
