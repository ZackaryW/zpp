---
name: zpps-finalize
description: Assess supplied repository, semantic-verification, and archive evidence for finalization without invoking those operations or completing the lifecycle.
---

# Assemble final change evidence

Accept either playbook configuration or a direct partial invocation. Require the
accepted contract revision, exact repository and store roots, every change member,
retained Bundler owner and bundle identity when mutation occurred, completed-phase
and checkpoint evidence, changed-path inventory, and any repository verification,
semantic verification, and archive results already obtained by the caller. This
assessment is read-only and does not require prior kernel delegation.

Check that changed paths match the accepted scope and bundle membership. Require
truthful repository command evidence for every relevant shaped obligation and build
gate, semantic verification covering tasks, requirements, design, bindings, duplicate
authority, and orphan authority, and archive results for every member when archival
was authorized.

Return one of:

- `repository-evidence-required` with exact missing targets and sufficiency criteria;
- `change-verification-required` with the change identities and evidence to assess;
- `archive-required` with the exact single or bulk archive scope;
- `blocked` with failed or inconsistent evidence; or
- `completed` with the assembled paths, verification, and archive identities.

The caller explicitly invokes the signaled component and re-enters finalization with
its result. Never invoke another `zpps-*` skill, convert insufficient evidence into
success, expand a lease, complete a bundle, select continuation, authorize a commit,
archive a change, or declare lifecycle completion.
