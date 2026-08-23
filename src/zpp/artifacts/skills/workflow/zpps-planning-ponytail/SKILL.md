---
name: zpps-planning-ponytail
description: Plan only the utility boundaries required by accepted behavior using the complete Ponytail ladder, from playbook or direct explicit configuration.
---

# Plan utilities with Ponytail

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository roots, shaped behavior and binding
inventory, dependency evidence, and any predecessor outcome relevant to utility
planning. This procedure is read-only unless the caller explicitly asks it to write a
planning artifact. For such a write, require a current kernel assessment with a
durable owner, exact registered store UUID, exact change member, and matching Bundler
membership; otherwise return `kernel-assessment-required`,
`durable-owner-required`, or `store-registration-required` with the unresolved
targets. A repo-local root remains valid for read-only inspection and a
`repo:<path>` trace locator, not Bundler mutation.

For each proposed utility responsibility, apply these rungs in order:

1. Confirm the responsibility is required by accepted behavior.
2. Reuse suitable repository code.
3. Use the standard library.
4. Use the native platform.
5. Use an already installed dependency.
6. Write the minimum repository-owned code.

When a confirmed non-trivial responsibility survives those rungs, compare maintained
packages by maturity, integration cost, security and maintenance fit, and the
proportion of their surface actually required. Use no universal percentage threshold.

Produce a disposable signature-level plan naming ownership, inputs, outputs, failure
contracts, seams, dependency decisions, and verification intent. Return `completed`,
`blocked`, or `skipped: not applicable`, with `kernel-assessment-required`,
`durable-owner-required`, or `store-registration-required` when that is the blocking
reason, plus the ladder evidence and any changed planning paths. A skip is truthful
only when the complete accepted behavior needs no
utility change. When this skill writes a governed task artifact, update only supplied
planning tasks whose text and scope are each fully satisfied by the completed
Ponytail plan. Never mark a partial, implementation, adjacent, inferred, or unrelated
task complete.

Never invoke another `zpps-*` skill, implement utilities, select workflow
continuation, mutate OpenSpec incidentally, expand a lease, checkpoint, or claim
lifecycle completion.
