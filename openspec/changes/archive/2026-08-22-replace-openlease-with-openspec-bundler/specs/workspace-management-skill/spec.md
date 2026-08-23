## REMOVED Requirements

### Requirement: Packaged manual workspace-management guidance
**Reason**: The OpenLease workspace lifecycle is removed and Bundler leasing is automatic within `zpp-workflow`.
**Migration**: None; no replacement companion skill is packaged.

### Requirement: Evidence-backed command and state-root selection
**Reason**: The removed workspace operations no longer select provider commands or workspace state.
**Migration**: Bundler lease commands use the selected ZPP home's `bundler` state child automatically.

### Requirement: Operation-specific workspace authority
**Reason**: Successor, reconciliation, handoff, cleanup, and preparation mutations are removed.
**Migration**: Bundle abandonment remains the only explicitly authorized recovery release.

### Requirement: Complete successor and reconciliation handoff
**Reason**: ZPP no longer creates or retains successors or reconciliation paths.
**Migration**: None.
