## Why

zpp currently gives every directory one governance root but resolves ordinary configuration only from that root, so a multi-language monorepo cannot declare Python policy for `sdk/python/` without also exposing it at the Rust root. Agents and downstream governance skills then compensate with inference, which has repeatedly produced incorrect resolver and Git assumptions instead of evidence-backed behavior.

## What Changes

- Resolve ordinary configuration through root-bounded nested `zpp.toml` overlays between the governance root and the requested target path.
- Preserve the existing merge rules: nearer scalars replace inherited scalars, lists union without duplicates, and tables merge recursively.
- Reserve `[governance]` and `[profiles.*]` for the resolved governance root; nested declarations fail with an error naming the file and prohibited section.
- Report scoped layers and their provenance through `zpp config resolve <PATH> --sources --json` without changing the governance root returned by `zpp resolve`.
- Add an authoritative, focused `skills/learn-zpp` knowledge-and-diagnostic skill that requires CLI/spec/documentation evidence and routes mutations to existing workflows.
- Publish that skill from the zpp repository through an automatically maintained subtree-split `dist/learn-zpp` branch for pinned submodule consumption.

## Capabilities

### New Capabilities

- `zpp-grounding`: Evidence-first zpp orientation and diagnosis, plus validated publication of the `learn-zpp` skill from its authoritative source directory.

### Modified Capabilities

- `governance-resolution`: Effective configuration becomes target-aware through nested ordinary-config overlays bounded by the resolved governance root.

## Impact

- Affects `zpp/core/governance.py`, the config CLI/source-reporting surface, resolver and CLI tests, documentation, and CI/release automation.
- Adds `skills/learn-zpp/` and a generated `dist/learn-zpp` branch; the main branch remains the source of truth.
- Nested authority sections that were previously inert inside a self-governed root will now fail explicitly.
- Enables downstream governance consumers to select policy by the actual code target without changing store, workset, or isolation authority.

## Governance Provenance
- Mode: `persistence`
- Intended base: `main`
