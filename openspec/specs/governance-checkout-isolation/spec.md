# governance-checkout-isolation

## Purpose

Defines logical member identity across cloned checkouts, branch-isolated governance worktrees, and local reader-writer governance leases.

## Requirements

### Requirement: Logical members accept isolated Git checkouts
zpp SHALL preserve an imported workset member's logical identity across Git worktrees and independent clones. Exact path containment SHALL win first; when it misses, zpp SHALL match a worktree by Git common-directory identity or an independent clone by normalized primary remote identity. zpp SHALL accept only a unique match and SHALL fail closed with ambiguity evidence when multiple logical members match.

#### Scenario: Independent clone matches one member
- **WHEN** a project checkout is outside the imported member path but has the same normalized primary remote as exactly one workset member
- **THEN** zpp resolves it as an alias of that logical member without changing the stored member path

#### Scenario: Multiple logical members share one remote
- **WHEN** remote identity matches more than one workset member
- **THEN** zpp reports an ambiguous member match and requires an explicit member override

### Requirement: Governance checkout is branch isolated
For a valid workset with one dedicated store, zpp SHALL derive the default governance branch as `<member-name>/<project-branch>` and SHALL use an isolated governance worktree as the session's effective governance root. A missing derived branch SHALL start from the governance store's `origin/HEAD`. Existing branches and worktrees SHALL be reused idempotently.

#### Scenario: Feature checkout receives an isolated store worktree
- **WHEN** `project-a` is on branch `feature-x` and automatic provisioning runs
- **THEN** zpp creates or reuses governance branch `project-a/feature-x` from the store default branch and reports its worktree as the effective governance root

#### Scenario: Existing derived branch is reused
- **WHEN** the derived governance branch and its worktree already exist
- **THEN** provisioning returns the existing effective root without creating a second branch or worktree

### Requirement: Isolation supports explicit overrides
The provisioning interface SHALL allow the owner to override the logical member, governance branch, base ref, or existing governance checkout. Overrides SHALL be machine-local and SHALL NOT add paths to a shared `.zpp-workset` file.

#### Scenario: Coordinated projects share an intentional governance branch
- **WHEN** the owner maps two project sessions to one explicitly selected governance branch
- **THEN** both sessions resolve that branch while normal write-lease exclusion still applies

### Requirement: Inspection never provisions
Read-only zpp commands, including governance resolution, config resolution, status, and doctor, SHALL NOT create Git branches, worktrees, session views, leases, or files. When a required isolated checkout is absent, resolution SHALL fail closed with structured provisioning guidance.

#### Scenario: Direct session needs provisioning
- **WHEN** resolution runs in a recognized project clone whose derived governance worktree does not exist
- **THEN** resolution returns a `provisioning-required` result and a copyable command without modifying any repository or zpp state

### Requirement: Governance writes use reader-writer leases
zpp SHALL provide machine-local leases keyed by the canonical effective governance root and governance branch. Read leases SHALL coexist. A write lease SHALL be exclusive against all other write leases for the same key, while leases for different governance branches SHALL remain independent.

#### Scenario: Two readers share one governance branch
- **WHEN** two sessions acquire read leases for the same effective governance branch
- **THEN** both leases succeed

#### Scenario: Second writer is blocked
- **WHEN** one live session holds the write lease and another session requests a write lease for the same effective governance branch
- **THEN** zpp refuses the second lease and reports the current holder

#### Scenario: Isolated writers proceed concurrently
- **WHEN** two sessions request write leases for different effective governance branches
- **THEN** both leases succeed

### Requirement: Stale lease recovery is explicit
Lease state SHALL include an opaque session id and renewable timestamp. zpp SHALL distinguish a live conflicting lease from a stale lease and SHALL require explicit confirmation or override before clearing stale state. A live lease SHALL NOT be silently stolen.

#### Scenario: Crashed writer leaves stale state
- **WHEN** a write lease has expired without renewal
- **THEN** zpp reports it as stale and offers an explicit recovery operation

### Requirement: Change ids are date addressed and OpenSpec valid
Branch-isolated governance workflows SHALL recognize new change ids in the form `cYYMMDD-<descriptive-name>`. zpp SHALL explain that the leading `c` preserves a compact date-addressed identity while satisfying OpenSpec's requirement that ids begin with a letter.

#### Scenario: Numeric-leading change id is proposed
- **WHEN** a workflow proposes an id beginning directly with `YYMMDD`
- **THEN** zpp rejects or normalizes it to the `cYYMMDD-<descriptive-name>` convention before artifact creation
