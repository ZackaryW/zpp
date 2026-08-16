## Why

ZPP discovers its packaged trait inventory by scanning `artifacts/traits/*.toml`, but its packaged skill inventory is a hardcoded literal tuple. Adding a packaged skill therefore requires editing a Python constant, three requirement documents, one BDD contract, and several unit assertions, and the closed inventory is asserted as canonical authority in `repository-authoring-skills`. That asymmetry now blocks concrete work: two skills from the `zmem` repository (`zmem-author-commits`, `zmem-query-memory`) should ship with ZPP and install alongside the existing authoring skills, and there is no way to add them without reopening every one of those hardcoded declarations.

## What Changes

- Packaged skills move from a flat `artifacts/skills/<name>/` layout to role directories: `artifacts/skills/workflow/` and `artifacts/skills/companion/`. A directory is a skill only when it contains `SKILL.md`.
- The packaged skill inventory becomes discovered rather than declared. The `PACKAGED_AUTHORING_SKILL_NAMES` literal is removed and replaced by a deterministic sorted directory scan, mirroring the existing packaged-trait scan.
- The `workflow` role must resolve to exactly one skill; a missing role, an empty companion role, or a workflow role holding zero or several skills fails loudly rather than silently projecting a wrong inventory.
- Two vendored `zmem` skills are added to the companion role and are consequently installed by `zpp init` and preflighted and removed by `zpp reset` for every selected agent. `zmem-design-extensions` is deliberately not vendored.
- Per-agent projection and removal order becomes the discovered deterministic order instead of a hand-written sequence. **BREAKING** for anything asserting the previous fixed `zpp-configure-behave` then `zpp-author-trait` order, and for the per-agent lifecycle result count, which rises from 10 to 12.
- A GitHub Actions workflow re-syncs and replaces the two vendored `zmem` skill directories from their upstream repository when `pyproject.toml` is updated, keeping vendored copies from silently drifting.

## Capabilities

### New Capabilities

None. This change redistributes an existing inventory obligation across capabilities that already own it.

### Modified Capabilities

- `repository-authoring-skills`: the requirement that ZPP package *exactly* `zpp-configure-behave` and `zpp-author-trait` is superseded by an open, role-discovered companion inventory that still guarantees both authoring skills are present and still binds each to its authoring guidance.
- `openspec-skill-provisioning`: initialization loads and projects every discovered companion skill rather than a named pair, and per-agent projection order follows discovery order.
- `product-home-lifecycle`: reset preflights and removes every discovered companion skill rather than the two named authoring skills, in discovery order.

## Impact

- `src/zpp/artifacts/__init__.py`: `PACKAGED_AUTHORING_SKILL_NAMES` removed; `packaged_workflow_skill()` and the companion loader become role scans with explicit failure modes.
- `src/zpp/artifacts/skills/`: restructured into `workflow/` and `companion/`; two vendored `zmem` skill directories added.
- `src/zpp/cli/initialization.py`, `src/zpp/cli/reset.py`: call sites follow the renamed discovery entry point; reset projection order derives from discovery.
- `features/support/contracts.py`: reset projection order and initialization result counts no longer derive from the removed constant.
- `tests/unit/test_artifacts.py`, `tests/unit/test_cli.py`, `tests/integration/test_end_to_end.py`: inventory, order, and count assertions.
- `.github/workflows/`: new vendored-skill sync workflow. This file is CI artifact text, not runtime behavior, and carries no BDD or TDD obligation.
- Out of scope: `SUPPORTED_AGENTS` in `src/zpp/cli/reset.py`, and `OPENSPEC_CORE_SKILL_NAMES` in `src/zpp/utils/openspec.py` — the latter is an assertion against the external OpenSpec generator, not a ZPP inventory.

## Resolved CI Decisions

Settled by the owner during clarification:

- The sync workflow commits re-synced vendored skills directly to the default branch. It does not open a pull request.
- The sync tracks the `zmem` default branch HEAD.

No unresolved product decisions remain for this change.
