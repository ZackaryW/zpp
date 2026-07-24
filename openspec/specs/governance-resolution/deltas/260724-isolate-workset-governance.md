## ADDED Requirements

### Requirement: Resolution reports the effective governance context
For a directory associated with a valid single-store workset, zpp SHALL report both the stable registered store identity/base root and the session-effective governance branch/root. The effective context SHALL also name the logical project member and project branch used for derivation. Config and trait consumers SHALL use the effective root while store-id validation continues to use the global registry.

#### Scenario: Isolated feature context resolves
- **WHEN** resolution runs in an aliased `project-a` checkout on `feature-x` whose governance worktree is provisioned
- **THEN** the result retains the registered store id and base root and reports `project-a/feature-x` plus its worktree as the effective governance context

### Requirement: Invalid or unprovisioned isolation fails closed
Resolution SHALL NOT silently fall back to the globally registered base store when a recognized project context requires isolation. A multi-store workset SHALL return an invalid-workset failure, and a missing derived governance checkout SHALL return a provisioning-required failure. Both failures SHALL carry machine-readable evidence and human remediation.

#### Scenario: Missing worktree cannot bleed into base
- **WHEN** a feature checkout uniquely matches a store-backed workset but its derived governance worktree is absent
- **THEN** resolution does not return the registered base root as effective and instead requires provisioning

#### Scenario: Invalid multi-store workset cannot choose
- **WHEN** the containing workset has more than one dedicated store
- **THEN** resolution fails without selecting a store by path order, member order, or profile
