# Proposal: bootstrap-zpp-core

## Why

The Pathverse governance toolchain is a polyglot pile held together by ~30 duplicated shell scripts (`.sh` + `.ps1` pairs for setup, pv-doctor's 13 checks, build-agents, skill config checks), and its central protocol — which repo is governed by which OpenSpec store, under which layered config — is implemented ad hoc across compose.py, `pva.toml` conventions, and prose discipline in skills ("keep the `--store` flag on follow-ups"). openspec deliberately does not model project→store bindings, multi-repo compositions carry no governance semantics, and nothing owns the answer to "which governance mode is this repo in?".

zpp (zack's project protocol) fills that gap: one Python-on-uv CLI that is the authoritative implementation of the protocol, wrapping — never replacing — openspec, zmem, and codegraph.

## What Changes

- New Python package `zpp` (distributed via `uv tool install`), exposing a `zpp` CLI.
- `zpp workset` command group: wraps `openspec workset` and adds what it refuses to hold — `import`/`sync` from user-owned `.code-workspace` files (one-way: the workspace file is layout truth, zpp never writes it), a machine-local sidecar for member semantics (store bindings, roles, config overlays), `bind`, `status`, `doctor`.
- `zpp snapshot` command group: local-only undo for zpp's own state (sidecar + workspace-file text), auto-taken before every mutating command; recovery from tamperment and wrong edits. Not a backup tool, not a distribution mechanism — sharing happens by committing the `.code-workspace`.
- `zpp bootstrap`: absorbs `scripts/setup.{sh,ps1}` from governance-of-agents-1 — installs the governance toolchain (node, jq, rg, codegraph, zmem, openspec CLI) with uv as the sole manual prerequisite.
- `zpp doctor`: absorbs pv-doctor's duplicated check scripts — cross-platform environment verification from one codebase.
- `zpp config resolve`: the single authority for layered governance config (repo `zpp.toml` → workset sidecar overlay → store `zpp.default.toml`; merge semantics inherited from pva). zpp reads only its own protocol files — `pva.toml` stays with the legacy compose stack.
- Four-mode governance resolution, first hit wins: local openspec root → self-governed; in-repo binding → externally governed (committed fact); sidecar binding → externally governed (personal view); none → explicitly ungoverned. Single-repo work self-governs via a local `openspec/` root with no governance repo required.

## Capabilities

### New Capabilities

- `workset-management`: import/sync worksets from `.code-workspace` files, delegate composition and opening to `openspec workset`, maintain the machine-local sidecar (bindings, member metadata), report status and doctor drift.
- `governance-resolution`: determine any directory's governance mode (self-governed / externally governed by committed fact / externally governed by personal view / ungoverned) and resolve the effective layered config.
- `snapshot-recovery`: local snapshots of zpp-owned state, auto-taken before mutations, with take/list/restore for recovering from wrong edits or tampering.
- `environment-bootstrap`: install and verify the governance toolchain cross-platform (`zpp bootstrap`, `zpp doctor`), replacing the duplicated shell scripts.

### Modified Capabilities

<!-- none — this store is new; governance-of-agents-1 specs are out of scope for this change -->

## Impact

- New repo content: Python package, `pyproject.toml`, CLI entry point.
- External interfaces consumed: `openspec workset`/`store` CLI (`--json` where available), the openspec store registry (read-only), `.code-workspace` JSONC files (read-only), `zpp.toml` / `zpp.default.toml` formats.
- New machine-local state: `~/.zpp/` (sidecars, snapshots, registry of workset-file locations).
- governance-of-agents-1 is unchanged by this change; script retirement there happens later, once zpp proves equivalent.
