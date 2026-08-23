## 1. Remote Dependency Source

- [ ] 1.1 Replace the local Bundler source override with the immutable GitHub direct dependency
- [ ] 1.2 Regenerate and inspect `uv.lock` for the exact remote commit with no adjacent-path source

## 2. Verification

- [ ] 2.1 Sync from the locked remote dependency and run lint, format, and complete tests
- [ ] 2.2 Run every capability-owned BDD root independently and strict OpenSpec validation
- [ ] 2.3 Build the wheel and sdist and verify their metadata carries the remote Bundler requirement
