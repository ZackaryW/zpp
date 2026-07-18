# Design: configurable-doctor

## Context

`core/toolchain.py` holds one hardcoded `TOOLS` table consumed by both `doctor()` (detect-only) and `bootstrap()` (idempotent install) — the spec invariant is that the two can never disagree. Config layering (`governance.resolve_config`) already serves sectioned config through store → workset/env → repo tiers with list-union merge; `[traits]` proved that a new domain is a new section with no resolver change. The 1v2 migration needs stores to publish toolchain expectations, and pv-doctor's 26 platform-duplicated check scripts retire against exactly this seam.

Owner decisions from the clarify interview: the format is `doctor.exclude = []` plus repeatable `[[doctor.more]]` with `which`/`successnote`; `successnote` is shown when the tool is **present**, as usage guidance that lets a reader skip install/recommendation steps; `which`-only this round; tiers path-aware; exclude binds doctor and bootstrap equally.

## Goals / Non-Goals

**Goals:**

- Store-publishable toolchain config through the existing tiers, path-aware.
- Exclude and extend the builtin table without forking the doctor/bootstrap invariant.
- `successnote` as present-state usage guidance (capability discovery, not fix hints).

**Non-Goals:**

- No file-presence or content check kinds (`exists = <path>`) — a later change; pv-doctor's constitution/global-asset checks stay in a micro skill.
- No install strategies for `more` tools — they are detect-only by definition; a tool zpp should install belongs in the builtin table.
- No per-tool enable/disable beyond `exclude` (no `only = []` allowlist — YAGNI until a store needs it).

## Decisions

### D1: One effective table, assembled from config

`_effective_tools(path)` = builtin `TOOLS` minus `exclude`, plus `more` entries mapped to `{cmd: which, note: successnote, detect_only: True}`. Both `doctor()` and `bootstrap()` consume only the effective table — exclude therefore binds both by construction, not by parallel filtering. This preserves the spec's agreement invariant structurally.

### D2: `[doctor]` rides the standard tiers, path-aware

`zpp doctor [PATH]` / `zpp bootstrap [PATH]` resolve `[doctor]` via `governance.resolve_config(path)`. Lists union across tiers (standard merge): a store's `zpp.default.toml` publishes fleet expectations, a repo's `zpp.toml` adds repo-specific tools, `exclude` entries union too. Resolution failures degrade to the builtin table (doctor must work on a broken machine — that is its job).

### D3: `successnote` semantics — present-state usage guidance

When a `more` tool is present: `✓ <cmd>  <successnote>` — the note tells the reader the capability already exists and how it is used, so downstream steps or agent recommendations that would install/introduce it are skipped. When missing: `✗ <cmd>` plainly, no hint — the format deliberately carries no fix text this round. Builtin tools keep their existing version/hint behavior.

### D4: `more` tools and bootstrap

Bootstrap skips `detect_only` entries entirely — present or missing, it neither installs nor counts them as manual steps. A missing `more` tool is doctor-visible (exit 1) but never a bootstrap concern; the format has no install strategy on purpose.

### D5: Fail-first discipline

behave scenarios in `features/doctor_config.feature` drive the capability; pytest units cover `_effective_tools` assembly (exclude, more, union across tiers, degraded resolution). RED before GREEN per group, per the repo's declared `[bdd]`/`[tdd]` stacks.

## Risks / Trade-offs

- [Excluding a load-bearing tool (e.g. `openspec`) silences real breakage] → exclude is honored verbatim — the config tiers are owner-authored and the store tier can't be shed by a session; doctor's report shows nothing for excluded tools rather than pretending health.
- [`[doctor]` resolution itself needs a working environment] → degraded path: any resolution failure falls back to the builtin table with a warning, so doctor never crashes on the machines that need it most.
- [more entries with duplicate `which` across tiers] → list-union dedups identical entries; differing notes for the same cmd keep first occurrence (base tier wins), consistent with the standard merge.

## Open Questions

- None — scope was settled in the clarify interview; the deferred `exists` check kind is recorded as a non-goal, not an open question.
