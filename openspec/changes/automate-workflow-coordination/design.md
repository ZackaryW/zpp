## Context

See `proposal.md` for motivation. The current lease bridge accepts only an explicit owner plus `UUID:CHANGE` members. OpenSpec registration exposes a store ID and root, while Bundler discovers its UUID from `openspec/bundler.toml`; a freshly registered repository therefore still cannot be leased. The prompt-only workflow kernel requires both values before it may acquire, producing a circular and user-visible bootstrap.

ZPP already owns a selected product home whose `bundler` child stores lease state. OpenSpec Bundler persists each bundle's owner, exact members, topology digest, and archive progress, so a stable ZPP-home identity can survive agent turns without a second workflow-state model.

## Goals / Non-Goals

**Goals:**

- Make one accepted mutation request sufficient for the ZPP runtime to prepare and acquire coordination.
- Keep store UUIDs stable in store-owned manifests and workflow ownership stable in the selected ZPP home.
- Preserve exact-member leases, descendant closure, conflict visibility, path audit, archive recording, and complete release.
- Keep explicit low-level owner and UUID inputs available for diagnosis and recovery.
- Provide a separate, explicit, one-child-command bypass without making bypass an environment override.

**Non-Goals:**

- Add a workspace, session, claim, handoff, or persisted workflow-stage model.
- Silently repair an invalid manifest, ambiguous registration, topology error, or conflicting bundle.
- Infer mutation, archive, checkpoint, abandonment, or product-decision authority from automatic coordination.
- Change read-only resolution or require coordination state for it.
- Let skills own coordination algorithms or environment parsing.

## Decisions

### Persist one managed workflow owner per selected ZPP home

Add a strict versioned identity document beside the `bundler` state child. On first automatic acquisition, create a UUID-v4-backed owner such as `zpp:<uuid>` with exclusive/atomic initialization; on later calls, validate and reuse it. Resetting Bundler lease state SHALL preserve this owner identity because it identifies the ZPP installation, not an active bundle.

This is preferred over prompting because the value has no product semantics, over deriving from a filesystem path because paths move and leak machine details, and over a per-turn identity because bundles must survive agent restarts. Explicit owner input remains authoritative for manual recovery operations.

### Prepare repository targets before exact acquisition

Extend the lease bridge with an automatic target mode accepting ordered repository-root/change-name pairs. For each root it will:

1. resolve the nearest healthy OpenSpec root;
2. reuse the unique registration for that root or invoke public `openspec store register <root> --yes --json` when none exists;
3. create `openspec/bundler.toml` with a canonical UUID v4 when absent, using exclusive creation and rereading after a concurrent creator wins;
4. strictly validate an existing manifest and map the registered store ID to its Bundler UUID;
5. acquire one atomic bundle for the exact resulting UUID/change members under the managed owner.

Registration and manifest creation are bootstrap effects admitted by the already accepted mutation request. They occur before product-artifact mutation and are returned as changed paths/evidence. Invalid or ambiguous state blocks; it is never overwritten. Explicit UUID-member acquisition remains supported and may take an explicit owner.

The complete operation lives in ZPP's Python service and CLI. Skills provide roots, change names, and accepted authority, then consume one structured result. They do not reproduce the subprocess, JSON, filesystem, identity, or Bundler procedure.

### Treat environment input as strict override, never bypass

The runtime will read optional `ZPP_WORKFLOW_COORDINATION` as a versioned compact JSON object. Version 1 may contain an `owner_id` override and a `stores` object mapping resolved repository-root strings to explicit registered store IDs. Unknown fields, invalid JSON, empty identities, duplicate resolved roots, unknown registrations, and root/store mismatches block before any mutation. Missing fields retain automatic behavior.

Overrides affect selection only. The runtime still validates or creates the store manifest, resolves its actual UUID, builds the exact member set, and acquires a valid bundle. Skills do not read or forward this variable. This single typed document is preferred over several loosely related variables because multi-root operations remain representable and validation is atomic.

### Let bundle identity recover the managed owner

Archive recording, completion, and authorized abandonment will accept an omitted owner. In that mode the bridge loads the selected ZPP-home identity and requires the retained bundle to carry that exact owner before delegating to Bundler. An explicitly supplied owner continues to use Bundler's existing ownership check.

This removes redundant prompt plumbing while ensuring one ZPP home cannot silently operate another owner's retained bundle.

### Change the kernel admission envelope, not its authority boundary

For governed mutation, the kernel will require durable product authority plus exact repository roots and change names. It will no longer require the caller to pre-resolve registration, store UUIDs, owner IDs, or bundle IDs. The automatic bridge result becomes the guard containing exact resolved members and the bundle identity. All later path audit and archive completion rules remain unchanged.

Packaged playbooks and mutating components will request automatic preparation instead of returning `durable-owner-required` or `store-registration-required`. They still stop on concrete bootstrap or lease conflicts and never treat automatic preparation as product authority.

### Isolate full bypass in an explicit command wrapper

Add `zpp bypass --reason TEXT --acknowledge -- COMMAND...`. The command emits a warning to standard error before execution, creates an unguessable per-process bypass marker, and launches exactly one child with that marker in its environment. Governed-mutation runtime entry points recognize only the wrapper marker, return structured `coordination: bypassed` evidence, and skip registration, manifest, owner, and lease work. The wrapper returns the child's exit code and never persists the marker.

A raw `ZPP_WORKFLOW_COORDINATION` value cannot request bypass. This separates ordinary overrides from the dangerous escape hatch and makes bypass visible in both the terminal and structured workflow evidence. The wrapper is an execution mechanism, not proof of mutation, archive, checkpoint, or product authority; the agent invokes it only after explicit owner agreement in the conversation or controlling automation.

## Risks / Trade-offs

- [Automatic registration changes machine-local state] → Limit it to already authorized mutation, return the registry result, and never register an ambiguous or unhealthy root.
- [Manifest creation changes the repository before a lease is held] → Treat it as an idempotent topology bootstrap, create only when absent, use exclusive creation, and report the exact path for checkpoint review.
- [Concurrent first use races on identity or manifest creation] → Use exclusive creation followed by strict reread; never overwrite the winning valid identity.
- [A retained explicit-owner bundle cannot use managed defaults] → Fail ownership validation and require the existing explicit recovery option.
- [Automatic behavior could hide real contention] → Preserve Bundler conflict diagnostics verbatim and prohibit fallback to an unleased mutation.
- [Environment overrides could become a hidden bypass] → Use strict typed selection-only fields and reject any bypass field or unknown key.
- [Users may normalize bypass for convenience] → Require per-command acknowledgement and reason, warn before execution, avoid persistence, and expose bypass in structured results.

## Migration Plan

1. Add RED public scenarios for automatic bootstrap, identity reuse, and conflict preservation plus focused identity/registration/manifest unit matrices.
2. Implement strict product-home owner identity initialization and automatic store preparation as bounded utilities.
3. Extend the lease service and CLI with runtime-owned automatic target acquisition, strict `ZPP_WORKFLOW_COORDINATION` overrides, and optional managed-owner lifecycle operations while preserving explicit forms.
4. Add the explicit one-child `zpp bypass` wrapper and structured bypass evidence.
5. Update kernel, playbooks, and mutating component contracts to consume runtime results without owning coordination logic.
6. Run affected BDD roots, focused tests, the complete native test surface, lint, format, lock, supported-interpreter, and clean build gates.

Rollback removes automatic target mode and restores explicit workflow inputs. Created valid store manifests and the local ZPP-home identity remain harmless and may be retained; no active bundle is rewritten during migration.
