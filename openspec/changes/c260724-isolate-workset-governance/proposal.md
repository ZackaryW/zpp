## Why

Workset membership currently binds one logical project to one absolute checkout path, while an OpenSpec store id binds globally to one registered checkout. Parallel branch work can therefore either lose its workset governance or share an unmerged governance checkout with unrelated sessions, allowing proposed decisions to bleed across branches.

## What Changes

- Enforce that a workset contains at most one dedicated OpenSpec store member while continuing to allow ordinary members with local `openspec/` roots.
- Resolve a session-scoped effective governance checkout without changing the global OpenSpec store registration.
- Automatically create or reuse isolated governance branches/worktrees for project branches, with explicit branch, base, and checkout overrides.
- Keep `resolve` and session-start inspection read-only; perform automatic provisioning through `workset open` and fail closed with remediation when a direct session needs provisioning.
- Add shared-reader/exclusive-writer governance leases keyed by effective governance branch, including stale-lease recovery.
- Standardize new change ids as `cYYMMDD-<descriptive-name>`, using the leading `c` to satisfy OpenSpec's letter-first rule.
- **BREAKING**: reject new or synchronized worksets containing multiple dedicated stores, and fail governance resolution for an existing invalid multi-store workset.

## Capabilities

### New Capabilities

- `governance-checkout-isolation`: Automatic and manually overridable branch/worktree provisioning, effective-root selection, and governance read/write leases.

### Modified Capabilities

- `workset-management`: Add the zero-or-one dedicated-store invariant, validation, doctor diagnostics, and branch-aware workset opening.
- `governance-resolution`: Return the effective governance root and fail closed for invalid or unprovisioned isolated contexts without mutating state.

## Impact

Affected areas include `zpp.core.worksets`, `zpp.core.sidecar`, `zpp.core.governance`, the OpenSpec adapter, workset CLI commands, machine-local zpp state, doctor/status output, tests, and README protocol documentation. Worksets without a dedicated store retain current behavior; store-backed worksets automatically adopt isolation, and existing multi-store worksets require repair.

## Governance Provenance

- Decision branch: `governance/c260724-isolate-workset-governance`
- Decision ref: `refs/heads/governance/c260724-isolate-workset-governance`
- Intended base: `main`
