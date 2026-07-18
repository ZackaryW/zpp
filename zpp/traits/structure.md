---
name: structure
description: Single responsibility, soft size limits — splits are refactors
---

## structure

**When**: after implementing — review every file you created or grew before
considering the work done.

**What**: one responsibility per unit, size kept within soft limits, and any
split is a pure refactor.

**How**:

- One responsibility per function. Needs "and" to describe → split.
- One responsibility per file. Real second concern → new file named for it.
  Speculative concern → ponytail says no.
- No unrequested abstractions (see ponytail).
- Soft limits: function ≤ ~40 lines, file ≤ ~300 lines. Exceeding → justify or
  split; deliberate acceptance → `zmem(DEBT)`.
- Splits are refactors: all scenarios and tests stay green throughout.
