## Context

See `proposal.md`. Nx's non-JavaScript installation creates root wrappers plus an ignored `.nx/installation`. ZPP currently checks only `node_modules/.bin` explicitly, then accepts `shutil.which("nx")` without normalization; on Windows that lookup can return the generated root batch wrapper as a relative path.

## Goals / Non-Goals

**Goals:**

- Consume both official package-local and non-JavaScript repository-local Nx wrappers portably.
- Give subprocess inspection and execution one absolute path.

**Non-Goals:**

- Initialize Nx, install plugins, or interpret project configuration.
- Change provider selection or Nx command construction.

## Decisions

### Extend the existing ordered discovery

Discovery will retain `node_modules/.bin` first, check the platform-native root wrapper second, and resolve a PATH result last. Every accepted regular non-symlink wrapper is returned as an absolute path.

Alternative considered: rely on current-directory behavior in executable lookup. Rejected because it differs by platform and produced a relative Windows batch path that failed when reused by ZPP.

### Keep execution generic

The existing argument-safe process runner and Nx surface inspection remain unchanged. Absolute batch paths already execute correctly on supported Windows Python, while the POSIX root wrapper is a normal executable script.

## Risks / Trade-offs

- [A malicious repository wrapper shadows PATH] -> This is already the explicit repository-owned precedence contract; reject symlinks and require a regular file.
- [A checked-out POSIX wrapper lacks execute permission] -> Surface inspection fails closed as an unavailable configured provider.
