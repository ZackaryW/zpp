---
name: coverage
description: Verify coverage, never assume it — every changed branch exercised or explicitly deferred
---

## coverage

**When**: code with a test suite was added or changed and the work is about
to be presented as done.

**What**: coverage is verified by a report, never assumed from "the tests
pass".

**How**:

- Run coverage with the project's test runner (per the repo's declared
  tdd/bdd stack).
- Every new or changed function appears in the report with its branches
  exercised.
- Uncovered changed code → add a test, or record the deferral as
  `zmem(DEBT)` with a ceiling and an upgrade path.
- Don't re-run unit tests already covered by a passing BDD step in this
  cycle.
- The full suite is green before the work is presented.
