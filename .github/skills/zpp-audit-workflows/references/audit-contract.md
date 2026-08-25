# Serial workflow audit contract

The coordinator owns discovery, the reusable mock base, feedback decisions, source
status checks, and progression. One subagent owns exactly one workflow and one fresh
clone.

## Assignment

Supply the exact workflow name, source revision, workflow JSON, playbook, referenced
component contracts and skills, fresh clone, fresh product home, synthetic change
name, baseline sentinels, and this result contract. The child must not initialize a
new base, select another workflow, edit the source checkout, register a persistent
store, or acquire a real lease.

The child starts the isolated reminder before product work. It follows the full
playbook and lets its planning-operation branch create and complete the synthetic
change in the clone. At every registered stage it reads the pending stage, component
JSON, and component skill; checks the real reminder; produces a literal result from
the component vocabulary; records only an accepted result; and confirms that exactly
the expected stage advanced.

Planning selection, exploration/re-entry, synchronization/re-entry, repository
evidence, semantic verification, finalization, and archive remain visible branch
events even when they are not registered stages. Use real Git, OpenSpec status and
instructions, strict validation, local archive, reminder commands, and focused
verification. Mock only product-specific work.

Before every OpenSpec mutation, require the assigned clone, `git rev-parse
--show-toplevel`, and `openspec context --json` root to resolve to the same exact
path. Recapture source Git status immediately afterward. Stop on a mismatch.

## Feedback checkpoint

Return one structured result before the coordinator may assign another workflow:

- workflow, source revision, subagent, clone, product home, change, and archive;
- declared and recorded stages in order;
- observed branch events with input, component result, decision, and re-entry;
- focused verification and contamination comparisons;
- fixture and source gap ledger; and
- status: `closed`, `findings`, `blocked`, or `failed`.

Classify source gaps as contract, playbook, runtime, specification, verification, or
isolation drift. Fixture repairs remain `closed-in-fixture`; source recommendations
remain `open` until accepted, deferred, rejected, or blocked.

An accepted source recommendation returns to the full workflow phases. Preserve the
old result, make the authorized correction through the applicable ZPP playbook, and
rerun the same workflow with a new subagent and fresh clone. Do not proceed to the
next workflow merely because another workflow is likely to report the same gap.
