## Context

zpp currently treats `.code-workspace` as layout truth, mirrors each imported workset into OpenSpec, stores machine-local absolute member paths in a sidecar, and resolves membership only when the query path is beneath one of those paths. OpenSpec separately registers each store id to one global root. Those models are sound for one checkout per logical member but cannot isolate a second project checkout and a matching governance-store branch without either rewriting user layout or changing global registry state.

The coordinated governance-of-agents-1v2 change consumes the effective root and lease APIs defined here. zpp remains the sole owner of workset, path, branch, and concurrency semantics.

## Goals / Non-Goals

**Goals:**

- Preserve stable logical workset membership across independent clones and Git worktrees.
- Give each project branch a session-scoped governance checkout without changing the registered store root.
- Automatically provision through an intentional mutating command and provide explicit overrides.
- Allow concurrent readers and isolated writers while preventing concurrent writes to one effective governance branch.
- Preserve existing behavior for worksets without a dedicated store.

**Non-Goals:**

- Modify OpenSpec's global store registry or on-disk data directly.
- Make `zpp resolve` or session-start hooks mutate Git or workset state.
- Infer that every repository containing `openspec/` is a dedicated governance store.
- Coordinate locks across machines; leases are machine-local protection for local agent sessions.
- Prove that implementation branches in other repositories have merged.

## Decisions

### Detect one dedicated store structurally

A dedicated store member is identified by `.openspec-store/store.yaml`; an ordinary member with only `openspec/` remains a self-governed project. Import and sync accept zero or one store and reject more than one. Doctor reports legacy violations, and resolution fails closed when a containing workset is invalid.

This uses OpenSpec's existing store marker instead of repository-name heuristics or treating every local spec root as shared governance.

### Separate logical member identity from checkout path

Exact path containment remains the first and fastest membership match. If it misses, zpp derives a Git repository identity from the shared Git common directory for worktrees or a normalized primary remote URL for independent clones, then compares it with registered members. A unique match aliases the checkout to the existing logical member name; zero matches remain outside the workset, and multiple matches fail as ambiguous.

The alias is session-local unless the owner explicitly persists an override. Branch names are not repository identity.

### Resolve an effective governance context

Resolution retains the registered store id and base root, and adds an effective context containing the logical project member, project branch, governance branch, and effective governance root. The default governance branch is `<member-name>/<project-branch>`. A pre-existing branch/worktree is reused; otherwise the branch starts from the store's `origin/HEAD`.

Manual overrides may select a governance branch, base ref, or existing checkout. Overrides are machine-local and must not enter the shared `.zpp-workset` path-free profile file.

The OpenSpec registry always continues to point at the stable base checkout. Consumers operate from the effective root instead of re-registering the same store id.

### Keep inspection read-only and provision through workset open

`zpp resolve`, config resolution, status, doctor, and session-start mounting never create branches, worktrees, locks, worksets, or files. When isolation is required but absent, resolution returns a structured `provisioning-required` failure with a copyable remediation command.

`zpp workset open` is the automatic provisioning boundary. Given the current checkout or an explicit project path, it resolves the logical member, creates or reuses the governance worktree, and opens a zpp-owned session view that substitutes checkout paths without rewriting the user-owned `.code-workspace`. Manual provisioning exposes the same operation with branch/base/path overrides.

The session view is created and removed only through the OpenSpec CLI or zpp-owned state; zpp never writes OpenSpec's data directory directly.

### Use machine-local reader/writer leases

Leases are keyed by canonical effective governance root plus governance branch. Read leases coexist; a write lease is exclusive. Sessions on different effective branches do not block each other.

Lease records live under `~/.zpp`, include an opaque session id, process metadata where available, acquisition/renewal timestamps, and mode. Mutating governance workflows acquire or upgrade before writing and renew while active. An expired lease is reported as stale and can be cleared through an explicit confirmation/override; a live lease cannot be silently stolen.

### Use OpenSpec-valid date-addressed change ids

New change ids use `cYYMMDD-<descriptive-name>`. The leading `c` is required because OpenSpec rejects ids beginning with a digit. This convention is validated where zpp provisions or inspects branch-isolated governance work.

## Risks / Trade-offs

- **Remote URL identity can be ambiguous or absent** → Prefer Git common-directory identity, normalize remotes, fail on multiple matches, and provide an explicit member override.
- **Automatic Git worktree creation can fail on dirty state, missing `origin/HEAD`, or branch collisions** → Provision only through mutating commands, preflight every condition, and support `--base`, `--branch`, and `--checkout` overrides.
- **Generated session views add local lifecycle state** → Keep them zpp-owned, identify them explicitly, exclude them from ordinary orphan diagnostics, and make cleanup idempotent.
- **Stale leases can block work after crashed sessions** → Use renewable timestamps, surface owner/session evidence, and require explicit stale-lease recovery.
- **Automatic isolation changes store-backed worksets** → Roll out with doctor previews and retain a rollback path that removes zpp-owned views/worktrees without touching project repositories or the registered base store.

## Migration Plan

1. Add read-only detection and doctor reporting for store cardinality, Git aliases, and prospective effective contexts.
2. Add provisioning and session-view support behind the new workset behavior, with tests covering exact paths, worktrees, independent clones, and ambiguity.
3. Add leases and expose their state in JSON and human status.
4. Enable automatic isolation for valid single-store worksets.
5. Update documentation and coordinate release with governance-of-agents-1v2.

Rollback removes zpp-owned session views, lease files, and governance worktrees after confirming their paths are under zpp's state directory. It does not edit `.code-workspace`, project checkouts, or the OpenSpec registry.

## Open Questions

None. The coordinated 1v2 proposal defines workflow consumption and promotion policy.
