## REMOVED Requirements

### Requirement: Automatic single-repository floorplan registration
**Reason**: OpenSpec registration and each store's version-1 Bundler manifest are the authority registry.
**Migration**: Register stores through OpenSpec and give each store one Bundler UUID.

### Requirement: Worktree-keyed session identity with explicit override
**Reason**: Read-only resolution is session-free and mutable workflows use durable owner identities.
**Migration**: None.

### Requirement: Session space establishment
**Reason**: ZPP composes repository attachments and selected-store namespaces without spaces.
**Migration**: Put repository input in `.zpp` documents and store input under `[extensions.zpp-traits]`.

### Requirement: Relationship-gated multi-repository work
**Reason**: Bundler parent containment and explicit atomic multi-root requests replace OpenLease relationships.
**Migration**: Declare `parent` in each child store manifest or request independent stores as multiple roots.
