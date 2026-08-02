# build-zpp-system

Build ZPP 0.9.0 around profiles, single-file Markdown traits, trait.json triggers, config.json traitsConfig overrides, bootstrap behavior, Typer, and the established artifacts, cli, core, and utils boundaries.

## Workflow authority

Use [`establish-workflow-skills`](../establish-workflow-skills/proposal.md) as the sole workflow-policy authority. The local `.codex/skills/zpp-*` definitions execute their individual mechanics; this product change must not duplicate or reinterpret their sequence.

The product proposal and complete Gherkin contract have been reconciled around global user-home native Pi, Codex, and Claude Code lifecycle hooks. Checkpoint `6c261fc` records that contract. After fallback checkpoint `109da49` exposed the missing batch-agent preflight boundary, replacement utility checkpoint `9e59ad3` made the explicit read-only preflights green. The integrated product is root-verified by 5 Behave features, 55 scenarios, 434 steps, and 45 unit tests; green integration checkpoint `6021688` records that gate. Five canonical capability deltas are formed from that evidence, pass strict OpenSpec validation, and are recorded by specification-formation checkpoint `f607541`.

Do not use the old governance plugin, old ZPP gates, or current application remnants as workflow authority.
