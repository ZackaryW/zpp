# Proposal: configurable-doctor

## Why

The doctor/bootstrap toolchain table is hardcoded: every machine checks the same tools, and a governance store cannot publish fleet-wide toolchain expectations for the repos it governs. The governance-of-agents-1v2 migration needs exactly that — pv-doctor's per-store tool checks retire only if a store can declare "these tools, plus these, minus those" through zpp's config tiers. A `[doctor]` section closes the gap with two small knobs.

## What Changes

- **`[doctor]` config section**, resolved through the standard tiers (store defaults → workset overlay → repo `zpp.toml`), path-aware: `zpp doctor [PATH]` and `zpp bootstrap` resolve the section for their context, so a store's `zpp.default.toml` governs every repo bound to it.
- **`doctor.exclude = ["<cmd>", ...]`** removes builtin table entries from **both** doctor and bootstrap — an excluded tool is neither checked nor installed, preserving the invariant that the two commands can never disagree about what the toolchain is.
- **`[[doctor.more]]`** repeatable entries add extra tools: `which = "<cmd>"`, `successnote = "<note>"`. They are **detect-only** — doctor reports them via `shutil.which`; bootstrap never installs them. When a `more` tool is **present**, its `successnote` is displayed as usage guidance (so a reader — human or agent — skips steps that would install or re-introduce the capability); when missing, it reports plainly with no hint.
- **`which`-only this round**: file-presence check kinds (pv-doctor's constitution/global-asset checks) are out of scope and remain with a micro pv-doctor skill until a later change.

## Capabilities

### New Capabilities

<!-- none — this extends an existing capability -->

### Modified Capabilities

- `environment-bootstrap`: gains two requirements — config-driven table filtering (`doctor.exclude`, honored by both doctor and bootstrap) and additional detect-only tools (`[[doctor.more]]` with present-state `successnote`).

## Impact

- Code: `zpp/core/toolchain.py` (config-aware table assembly), `zpp/cli/root.py` (`doctor`/`bootstrap` gain a PATH argument for context resolution).
- Config: the `[doctor]` section joins `[traits]`, `[tdd]`, `[bdd]`, `[zmem]`, `[governance]` in the layered files; lists union across tiers per the standard merge.
- Tests: BDD scenarios in `features/doctor_config.feature`; pytest units for table assembly.
- Downstream: unblocks retiring pv-doctor's tool checks in the 1v2 migration (store-published `[doctor]` in `zpp.default.toml`).
