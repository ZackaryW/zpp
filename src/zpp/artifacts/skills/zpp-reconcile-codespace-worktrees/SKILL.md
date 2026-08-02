---
name: zpp-reconcile-codespace-worktrees
description: Reconcile explicitly selected branches recorded by a ZPP codespace after isolated work is ready to integrate. Use only when the owner explicitly requests codespace branch reconciliation; never trigger from lock, add, open, unlock, cleanup, or recovery.
---

# Reconcile codespace worktrees explicitly

Require an explicit reconciliation request and a codespace identifier. Codespace
lifecycle commands preserve isolation and metadata; they never authorize a
merge, rebase, branch deletion, or worktree deletion.

1. Read the recorded codespace state through `zpp codespace status ID --json`.
   Consume the released claim's generated-checkout and branch metadata. Require
   every selected generated member to retain its effective path, source path,
   branch, commit, and source/effective checkout identities.
2. Inspect the current repository and recorded branch state without changing
   it. Report missing paths or branches, dirty worktrees, divergence, and the
   source commit each isolated branch began from.
3. Present all affected project and governing-store branches together. Ask for
   the intended destination and reconciliation strategy when either is not
   explicit; do not infer merge versus rebase or choose conflict resolutions.
4. Apply only the explicitly selected strategy, one repository at a time.
   Stop on the first conflict and preserve the remaining branches and
   worktrees unchanged.
5. Run the repository's relevant verification after reconciliation. Give every
   retained branch an explicit reconciled or abandoned disposition before
   finalization, then report resulting commits and remaining worktrees.

Never reconcile reference-only stores. Never delete recorded branches,
worktrees, or released metadata merely because reconciliation succeeded.
Cleanup and history retention remain separate explicit operations.
