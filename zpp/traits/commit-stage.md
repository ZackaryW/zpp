---
name: commit-stage
description: Close every task by committing through the zmem grammar so git history stays a memory graph
---

## commit-stage

**When**: a task's changes are complete and ready to be committed — every
commit, since zmem ingests all of git history.

**What**: the commit is a memory write — shaped for the zmem parser, not just
the reader.

**How**:

- Load the `zmem-commit` skill and follow it exactly.
- Batch per its rules: one logical change per commit.
- Subject: conventional commit. Body: `zmem()` annotations for the task's
  decisions and lessons. Cite recalled history that drove a choice.
- Every deliberate deferral → `zmem(DEBT)` with a ceiling (the limit
  accepted) and an upgrade path (what triggers revisiting it).
- Where the repo runs a test-economy gate, run it before presenting the
  commit and record its reconciliation trail in the commit body; a failing
  gate blocks the commit.
