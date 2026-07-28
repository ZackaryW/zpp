## 1. Coordinate Bounded Implementation

- [ ] 1.1 Have the primary agent assign non-overlapping subagent ownership for scoped resolver work and `learn-zpp` skill/publication work, retaining shared-file integration and final verification itself.
- [ ] 1.2 Run the repository's resolved BDD/TDD preflights and record the target paths, stack fragments, and fail-first proof requirements before any production edit.
- [ ] 1.3 Characterize current root-only config resolution and `--sources` output so compatibility assertions cover repositories with no nested `zpp.toml`.

## 2. Specify Scoped Resolution Failures First

- [ ] 2.1 Add failing behavior scenarios for a Python `sdk/python/zpp.toml` applying to its subtree but not the Rust root or sibling tree.
- [ ] 2.2 Add failing unit tests for root-to-target multi-level overlays, scalar replacement, list union, recursive table merge, file targets, and ordered provenance.
- [ ] 2.3 Add failing tests for nested `[governance]` and `[profiles]` errors that name the canonical file and every prohibited section.
- [ ] 2.4 Add failing boundary tests proving canonical targets, parent traversal, filesystem indirection, and sibling paths cannot consume overlays outside the resolved governance root.

## 3. Implement Target-Scoped Config

- [ ] 3.1 Separate governance-root resolution from scoped ordinary-config discovery in `zpp/core/governance.py` without changing the four-mode `zpp resolve` result.
- [ ] 3.2 Gather descendant `zpp.toml` files from root to target, treat file targets as their parent, and merge them with existing scalar/list/table semantics.
- [ ] 3.3 Validate scoped files before merging and emit precise root-only authority errors for `[governance]` and `[profiles]`.
- [ ] 3.4 Extend source attribution and `zpp config resolve <PATH> --sources --json` with an ordered scoped-layer representation while retaining root-only compatibility.
- [ ] 3.5 Make every scoped-resolution scenario and unit test green, then run the nearest resolver and CLI suites.

## 4. Create and Validate learn-zpp

- [ ] 4.1 Initialize `skills/learn-zpp` with the standard skill-creator scaffold, valid `SKILL.md`, and generated `agents/openai.yaml`.
- [ ] 4.2 Author the concise evidence-first diagnostic workflow and one-level references covering resolver/config concepts, source hierarchy, common traps, and mutation routing without duplicating the README.
- [ ] 4.3 Validate the skill with the standard validator and regenerate `agents/openai.yaml` if its interface metadata is stale.
- [ ] 4.4 Use fresh subagents to forward-test realistic zpp misunderstandings, including target/root confusion and an unverified Git submodule claim, then tighten the skill until both follow authoritative evidence.

## 5. Publish the Skill Subtree

- [ ] 5.1 Add CI automation that validates `skills/learn-zpp` and advances `dist/learn-zpp` from `git subtree split --prefix=skills/learn-zpp` only after relevant changes land on `main`.
- [ ] 5.2 Add tests or workflow checks proving the distribution branch root contains `SKILL.md`, `agents/openai.yaml`, and declared resources with no extra zpp repository tree.
- [ ] 5.3 Publish and verify the initial `dist/learn-zpp` commit, recording the exact commit for the dependent governance-plugin change.

## 6. Document and Verify

- [ ] 6.1 Update zpp's config documentation with nested authoring, root-only authority, merge examples, source reporting, and the no-reset boundary.
- [ ] 6.2 Run the full Python test suite, BDD suite, static/format checks, and distribution workflow validation; capture BDD/TDD proof blocks required by the resolved governance.
- [ ] 6.3 Run `openspec validate c260727-monorepo-zpp-grounding` and confirm every artifact and delta spec passes.
- [ ] 6.4 Have the primary agent review all subagent changes, confirm no out-of-scope governance or search behavior changed, and hand the verified upstream commit to the dependent proposal.
