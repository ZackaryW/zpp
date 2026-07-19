# Design: config-empty-hint

## Context

Empty resolution is legitimate (ungoverned or unconfigured contexts) but
currently indistinguishable from "something is broken" to a newcomer. The
lean audit cut `zpp init`; the on-ramp is a hint plus a template.

## Goals / Non-Goals

**Goals:**
- The moment of emptiness teaches the next step.
- A copy-paste `zpp.toml` template exists in the README.

**Non-Goals:**
- No `zpp init` or any scaffolding command (audited out — one-time action,
  permanent command surface).
- No auto-creation of `zpp.toml` (owner-authored doctrine).
- No hint on the JSON surface — agents consume the empty object as data.

## Decisions

- **Hint on human output only.** `emit()`'s human path appends the line;
  `--json` stays bare so scripted consumers never parse prose.
- **Template lives in the README**, not a packaged file: doctrine says
  owner-authored, so the on-ramp is documentation to copy, not a file zpp
  writes. Covers `[governance]`, `[tdd]`/`[bdd]` stack, `[traits] apply`,
  `[doctor]` — each commented.

## Risks / Trade-offs

- A README template can drift from config behavior. Bounded: the template
  only names sections the specs already govern, and doctor/config tests
  exercise those sections.
