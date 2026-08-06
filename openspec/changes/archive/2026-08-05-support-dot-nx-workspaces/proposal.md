## Why

Official Nx non-JavaScript initialization creates repository-root `nx` and `nx.bat` wrappers backed by `.nx/installation`. ZPP currently overlooks that portable wrapper on POSIX and can retain a relative Windows wrapper returned by executable lookup, causing valid repository-owned Nx workspaces to fail surface inspection.

## What Changes

- Recognize the official repository-root Nx wrappers after an existing `node_modules/.bin` wrapper and before a PATH executable.
- Normalize every discovered Nx executable to an absolute path before inspection or execution.
- Preserve ZPP's existing boundary: it consumes only an established project/target surface and never installs, migrates, downloads, or configures Nx.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `verification-orchestration`: repository-local Nx discovery also supports the official `.nx/installation` root wrappers used by non-JavaScript repositories.

## Impact

Affects Nx executable discovery, its focused native tests, and the existing repository-owned Nx feature contract. No new dependency or framework plugin is introduced.

## Unresolved — Do Not Assume

None. Existing `node_modules/.bin` wrappers retain first preference, root `.nx` wrappers are second, and PATH remains the fallback.
