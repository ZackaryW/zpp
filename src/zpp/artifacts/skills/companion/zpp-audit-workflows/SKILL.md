---
name: zpp-audit-workflows
description: Audit a local ZPP source checkout interactively by assigning each complete packaged workflow to its own isolated simulation subagent and comparing declared contracts with runtime and verification evidence. Use for an explicit workflow sequencing or design-to-implementation audit; do not use for ordinary product work or repairs.
---

# Audit complete workflows locally

Audit the workflow system by closing synthetic changes in disposable repositories.
Begin read-only in the ZPP source checkout; source correction occurs only through an
accepted interactive closeout with matching mutation authority.

Read [references/audit-contract.md](references/audit-contract.md) completely before
creating assignments, running simulations, classifying evidence, or reporting a
result.

## Establish the audit set

1. Resolve the containing Git worktree and require a ZPP source checkout containing
   `src/zpp/artifacts/workflow_contracts/workflows`. If the checkout or required
   delegation tools are unavailable, report the missing prerequisite instead of
   narrowing the audit.
2. Capture the current Git status, default-home `zpp lease status`, and read-only
   `zpp workflow run remind <root>` output. These are contamination sentinels, not
   audit authority.
3. Enumerate workflow JSON with `rg --files` and use `jq -e` to preserve typed names,
   modes, stage IDs, component identities, and order. Cross-check the packaged loader
   and its focused tests. Do not keep or infer a separate workflow list.
4. Resolve each workflow's playbook plus every referenced component JSON and
   `SKILL.md`. Missing evidence is a blocking finding for that workflow.

## Delegate one disposable workflow per subagent

Create one distinct bounded subagent assignment for every discovered complete
workflow. Never give two workflows to one subagent or let a child select another
workflow. Queue assignments when concurrency is exhausted; queuing does not permit
agent reuse. Give each child only its workflow identity, repository root, the audit
contract, resolved evidence paths, and the read-only/isolation boundary.

Each child must create a fresh empty temporary directory, run `git init`, initialize
OpenSpec with `openspec init <temporary-repository> --tools none --no-animation`, and
create a unique synthetic change. It must use `zpp --path
<temporary-product-home> ...` for every simulated workflow command and must not
register the disposable OpenSpec root as a persistent store. It may mutate its
temporary repository and run targeted verification, but it must not edit the ZPP
checkout, use the caller's product home, or acquire or mutate a real lease.

Fail closed before every OpenSpec command that can create, update, synchronize,
validate, or archive state. Run it with the temporary repository as the explicit
working directory, require `git rev-parse --show-toplevel` to equal that repository,
and require structured `openspec context --json` to report the same exact root. Stop
with a critical `isolation-failure` before the OpenSpec command on any mismatch.
Recheck source Git status immediately after every OpenSpec mutation; never rely on an
earlier initialization target to preserve a later process working directory.

## Run the complete playbook sequence

Give each workflow a minimal synthetic request that exercises its custom purpose and
branches. The child follows the assigned playbook as an agent would: start the
workflow, inspect the first pending stage, read the selected component contract and
skill, create a bounded mock input and result, evaluate the playbook-owned branches,
check and record the accepted result through the real reminder CLI, and repeat in
declared order.

Use real Git, OpenSpec, workflow registration, JSON, status, validation, sync/archive,
and targeted verification surfaces. Product-specific stage work may be mocked, but
every mock must satisfy the component result vocabulary and stopping boundary.
Planning-operation, sync, verification re-entry, finalization, and archive branches
remain visible even when they are not registered stages. Close the synthetic change
by validating and archiving it locally and stopping its reminder. A component or
branch gap must not terminate later safe observations: preserve the failure, state
the explicit mock assumption, and continue when that does not falsify the audit.

Maintain a gap ledger. The child may fix a `fixture-gap` only inside its temporary
repository and must retain the before/after evidence. A source-level gap remains open
and read-only. Require the child to return the structured per-workflow result from
the audit contract. Treat a missing, interrupted, or malformed child result as
blocked, never passing.

## Compare and review

After all initial assignments return, recapture the contamination sentinels. Any
difference attributable to the audit is a critical isolation failure. Aggregate the
results without erasing workflow-specific findings, lead with the overall outcome,
and present a concise result for every workflow.

Continue interactively until every source gap is `accepted-fix`, `deferred`,
`rejected`, or `blocked`. Apply an accepted fix only when the current repository
change already authorizes that exact source mutation; otherwise require a separately
invoked appropriate workflow. Update the owning design, implementation, and exact
verification together. A rerun always creates a fresh subagent, Git repository,
OpenSpec root, product home, and synthetic change for only that workflow, preserves
the other and superseded results, and names the earlier revision. Report completion
only when every workflow sequence closes and every gap has an explicit closeout.

Never use audit closeout to infer authority to customize a live workflow, commit,
archive a real change, abandon, bypass, or continue another playbook.
