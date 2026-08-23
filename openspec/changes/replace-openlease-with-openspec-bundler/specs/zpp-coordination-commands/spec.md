## REMOVED Requirements

### Requirement: ZPP-owned coordination command surface
**Reason**: The broad `zpp workspace` OpenLease surface is replaced by a minimal Bundler lease bridge used automatically by the workflow.
**Migration**: Use the workflow; there are no command aliases.

### Requirement: Distinct read-only inspection
**Reason**: Sessions, OpenLease closures, reconciliation plans, and successor dispositions no longer exist.
**Migration**: Bundler conflict results are reported by acquisition.

### Requirement: CLI-enforced destructive authority
**Reason**: The destructive workspace operations are removed.
**Migration**: Only exact-bundle abandonment retains an explicit owner check.

### Requirement: Refuse widened coordination targets
**Reason**: Bundler acquires only the declared member roots and their manifest-defined descendant closure.
**Migration**: Name every independent store/change member in the automatic workflow request.
