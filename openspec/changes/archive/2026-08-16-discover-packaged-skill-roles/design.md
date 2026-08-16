## Context

See `proposal.md` — Why. Two constraints shape the approach.

First, packaged assets are read through `importlib.resources`, not the filesystem, so discovery must work against a `Traversable` and must materialise each skill through `as_file` before Agent Router loads it. The existing packaged-trait scan already establishes that pattern and the ordering convention (`casefold`, then exact name) that this change reuses.

Second, `uv_build` includes everything beneath `module-root` in both wheel and sdist, and consults neither git tracking nor `.gitignore`. Any file placed under `src/zpp/artifacts/skills/` therefore ships. This is what makes vendored copies viable and what makes stray files in a role directory a packaging concern rather than a local-only annoyance.

## Goals / Non-Goals

**Goals:**

- One discovery rule that serves both the existing packaged skills and any future one, with no name list in Python.
- Failure modes that are loud at load time rather than silent at projection time, since a wrong inventory reaches a user's agent configuration.
- Keep vendored upstream content byte-faithful, so drift is a reviewable diff rather than an edit.

**Non-Goals:**

- Discovering skills from anywhere other than ZPP's own packaged artifacts. Plugin-contributed skills would be an Agent Router artifact-extension concern, mirroring `ZppTraitArtifactExtension` for traits, and are not in this change.
- Making role names configurable or open-ended. Exactly two roles exist, and their meanings are fixed.

## Decisions

**Role directories over a flat scan with an exclusion.** A flat `skills/` scan would have to exclude `zpp-workflow` by name, which keeps a name constant and, worse, keeps it in the one place where being wrong is silent — the workflow skill would simply be projected twice. Roles make the distinction structural: the workflow skill is not a companion skill because it does not live in the companion role. Alternative considered and rejected: a declarative `skills.toml` manifest, which restores a hand-maintained inventory that can drift from the directory it describes and reintroduces exactly the problem this change removes.

**A directory is a skill only when it carries `SKILL.md`.** This keeps a `README.md`, a stray `__pycache__`, or an editor artifact in a role directory from being handed to `Skill.from_path` as a malformed skill. It also makes the rule explainable in one sentence, which matters because contributors will add skills by copying a directory.

**Loud failure on an unusable role.** A missing role directory, an empty companion role, or a workflow role holding anything other than exactly one skill raises rather than returning an empty or partial tuple. An empty inventory would otherwise flow into `zpp init` as a successful no-op and silently skip projections the user expects. This is a new failure surface that the previous name-list approach got for free, since a missing named directory failed immediately.

**Vendored copies over a git submodule.** Rejected by the owner during clarification. Recorded here because the trade-off is real and worth carrying forward: a submodule would guarantee provenance but would bring the entire `zmem` repository — 110 files including its own `src/`, `tests/`, and `pyproject.toml` — into `src/zpp/artifacts/`, all of which `uv_build` would ship. Vendoring two directories keeps the wheel to what it needs. The cost is that vendored content can drift, which the sync workflow addresses.

**Sync triggered by `pyproject.toml` updates.** Chosen by the owner. This ties refresh to release-shaped moments rather than to every upstream commit, so a vendored skill is current whenever ZPP is about to ship, without a bot committing on unrelated pushes.

**Discovery order becomes projection order.** Rather than carry a separate ordering concept, the deterministic scan order is the projection and removal order. This is a visible behavior change — the packaged pair currently projects as `zpp-configure-behave` then `zpp-author-trait`, and sorted order inverts that — so the specs state projection order in terms of "the deterministic packaged order" instead of naming skills.

## Risks / Trade-offs

- **Vendored content silently diverges from upstream between syncs.** → The sync workflow replaces directories wholesale and surfaces the difference for review; vendored skills are never hand-edited, so any local diff is itself the signal.
- **A stray file committed into a role directory ships in the wheel.** → The `SKILL.md` rule means it is ignored by discovery rather than projected, so the blast radius is package size, not a broken agent install.
- **Every ZPP user now receives two `zmem` skills whether or not they use `zmem`.** → Companion skills are dormant by contract: they are manually invoked guides that no hook, trait, or workflow transition can trigger. The cost is inventory noise in the agent's skill list, which the owner accepted by asking for them to be bound to the installation.
- **Per-agent asset count and order change.** → This breaks assertions in `contracts.py`, `test_cli.py`, and `test_end_to_end.py`. These are updated as part of this change rather than left to fail, and the specs now describe counts structurally ("one result per projected asset") so a future companion skill does not break them again.
- **Loud failure on an empty companion role could break a partial checkout.** → Accepted deliberately. A packaged inventory that silently shrinks is worse than one that refuses to load.

## Migration Plan

No user-facing migration. Existing installations are reconciled by the ordinary `zpp init` path, which installs the two new companion skills and safely reconciles the rest; `zpp reset` removes what it discovers. The restructure moves directories inside ZPP's own package and changes no installed destination path.

## Open Questions

None. The two CI questions — commit target and tracked ref — were settled by the owner before the task breakdown: the workflow commits directly to the default branch and tracks `zmem` default-branch HEAD. Because it writes to the default branch unreviewed, the workflow must make no change when content is identical, so an unchanged sync produces no commit and no history noise.
