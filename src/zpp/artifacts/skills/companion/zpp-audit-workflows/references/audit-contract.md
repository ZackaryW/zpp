# Workflow Audit Contract

Use this contract for initial assignments and reruns. The coordinator owns discovery,
source-gap closeout, and aggregation; one child owns exactly one workflow and one
disposable mock repository.

## Assignment

Supply:

- the exact workflow name, ZPP source root, and audit revision;
- its workflow-contract path and playbook `SKILL.md` path;
- every stage in declared order with component-contract and component-skill paths;
- canonical specification, capability feature, focused test, runtime, and CLI paths;
- unique temporary repository and product-home parent paths; and
- the earlier result identity when this assignment is a rerun.

The child verifies every supplied path and may discover additional evidence. It must
not silently discard missing evidence or add another workflow.

Use these minimal synthetic requests unless current workflow design requires a more
precise equivalent:

| Workflow | Synthetic request |
| --- | --- |
| `zpp-new-feature` | Add one observable marker capability with one acceptance example |
| `zpp-fix-bug` | Seed an observable failing marker, preserve its reproduction, and correct only that defect |
| `zpp-scaffold` | Create a package/capability skeleton with one small observable loading boundary so conditional behavior stages are exercised |
| `zpp-generic-workflow` | Apply a mixed marker maintenance update with one behavior and one structural concern |

These requests are fixture inputs, not permanent product requirements.

## Disposable workspace

For every assignment and rerun:

1. Create a fresh temporary directory and verify it is empty.
2. Run `git init <temporary-repository>` and configure repository-local mock identity
   only when commits are required by the sequence.
3. Run `openspec init <temporary-repository> --tools none --no-animation`. Do not
   project agent tools or register the root as a persistent OpenSpec store.
4. Use `openspec new change <synthetic-change>` from that repository. Record the
   initially incomplete planning state as a fixture gap, then create only the minimum
   coherent artifacts needed by the assigned synthetic request.
5. Use a separate fresh `zpp --path <temporary-product-home>` prefix for every
   workflow reminder command.

The ZPP source checkout remains read-only during a child run. Snapshot its Git status
plus default-home reminder and lease output before and after all assignments. Never
clean a difference to make isolation appear successful.

## Full mock sequence

Start the exact workflow against the disposable repository and synthetic change.
Then repeat this procedure until no registered stage remains:

1. Read the first pending stage from structured status and confirm it equals the next
   workflow-contract stage.
2. Read the selected component JSON and `SKILL.md` completely.
3. Construct a minimal mock input satisfying the component's readiness and the
   playbook's stage-specific configuration.
4. Run `workflow run check` and require a matching allowed result.
5. Produce a mock component result using a literal token from the component JSON
   vocabulary. Keep explanatory reasons separate; for example, contract result
   `skipped` may carry reason `not applicable`, but the recorded token remains
   `skipped`.
6. Evaluate and record every playbook-owned branch caused by that result. Adapter
   operations outside the registered stage list remain distinct ledger events.
7. Run `workflow run record` and confirm only the expected stage advances.
8. Preserve exact input, result, commands, structured output, branch decision, and
   any assumption before continuing.

The branch ledger must explicitly cover applicable planning-operation selection,
exploration/re-entry, specification synchronization and re-entry, repository evidence
re-entry, semantic change verification, finalization, and archive. Do not claim a
branch passed because its target component was mentioned. Use real OpenSpec status,
instructions, strict validation, and local sync/archive behavior where those surfaces
can operate on the fixture; mock only product-specific work or external owner facts.

Closeout requires all of the following:

- every declared stage has one matching recorded accepted result;
- every applicable custom branch has an observed decision and bounded result;
- the synthetic OpenSpec change passes strict validation;
- local archive uses the explicit non-interactive confirmation required by the
  installed CLI and produces an archive path;
- the isolated reminder is stopped; and
- no persistent store, real Bundler lease, source file, default-home reminder, or
  default-home lease changed.

## Evidence matrix

| Layer | Required comparison |
| --- | --- |
| Contract | JSON schema validity, workflow identity/mode, unique stage IDs, order, references, effect, and result vocabulary |
| Playbook | Mandatory start, stage-specific inputs, custom decisions/branches, closeout, and absence of duplicated mechanical ordering |
| Components | Identity, readiness, effect, result vocabulary, substantive procedure, failure behavior, and stopping boundary |
| Mock transition | Exact inputs, selected component, check result, component result, record result, next stage, and branch events |
| Runtime/CLI | Registration persistence, matching/mismatching checks, accepted recording, stage customization, stop, and separation from leases |
| OpenSpec | Initialized local root, synthetic change status/instructions, strict validation, sync/archive result, and archive path |
| Specifications | Canonical requirements governing composition, registration, projection, authority, and custom workflow behavior |
| Verification | Exact Behave and focused pytest targets; unexecuted targets remain `not-run` |

Use CodeGraph before text search when `.codegraph/` exists. Otherwise use `rg` for
bounded discovery and `jq -e` for typed JSON. Prefer capability-targeted Behave and
focused pytest selectors; do not run a full repository suite inside every child.

## Gap ledger and closeout

Classify the gap origin first:

- `fixture-gap`: the disposable repository lacks a prerequisite the workflow can
  truthfully supply without changing ZPP source;
- `contract-drift`: workflow/component JSON is invalid or contradicts procedure;
- `playbook-drift`: custom Markdown behavior is missing, duplicated, or conflicts
  with mechanical authority;
- `runtime-drift`: CLI, reminder, kernel, or lease behavior contradicts authority;
- `specification-drift`: canonical requirements conflict with declared/observed
  behavior;
- `verification-drift`: required behavior lacks exact executable coverage or current
  coverage contradicts authority; or
- `isolation-failure`: the audit changed source or live reminder/lease state.

Every gap includes workflow, audit revision, transition/stage, type, severity,
expected behavior, observed behavior, exact evidence, reproduction, mock assumption
used to continue, proposed closeout, and closeout state.

Closeout states are:

- `closed-in-fixture`: repaired only inside the disposable repository, retaining
  failure and repair evidence;
- `open`: awaiting interactive source decision;
- `accepted-fix`: owner accepted an exact source correction under matching mutation
  authority;
- `deferred`: owner explicitly retained the gap for later work;
- `rejected`: owner rejected the proposed gap or correction with rationale; or
- `blocked`: evidence or authority prevents resolution.

Children may apply only `closed-in-fixture`. The coordinator presents source gaps
interactively and edits the ZPP checkout only for `accepted-fix` under an already
authorized repository change or separately invoked repair workflow. An accepted fix
must reconcile the owning design, implementation, and exact verification together.

## Per-workflow result

Return:

- workflow, revision, assignment/subagent identity, and status: `closed`, `findings`,
  `blocked`, or `failed`;
- temporary Git repository, OpenSpec root/change, product home, and archive identity;
- declared and recorded stages in order;
- custom branch ledger;
- evidence inspected at every matrix layer;
- mock transitions and targeted verification outcomes;
- complete gap ledger and unresolved evidence questions; and
- source/default-home contamination comparison.

`closed` requires a validated archived synthetic change, closed reminder, every
declared stage and applicable branch observed, no contamination, and no `open` gap.

## Aggregate and rerun

Report discovered, closed, findings, blocked, and failed counts, then one concise
section per workflow. Preserve detailed and superseded evidence. A rerun increments
only the selected workflow's revision, names the superseded result, uses a fresh
subagent, empty Git repository, OpenSpec root/change, and product home, and leaves all
other workflow results unchanged. Overall completion requires every workflow sequence
to close and every gap to have an explicit non-`open` closeout state.
