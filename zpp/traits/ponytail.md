---
name: ponytail
description: The minimalism ladder — stop at the first rung that holds
---

## ponytail

**When**: every line of code you are about to write or change, in any task.

**What**: stop at the first rung that holds; never skip a lower rung for
"clarity" or "future needs".

**How** — climb in order, stop at the first rung that answers:

1. **Necessity** — does this need to exist? Speculative → YAGNI, say so in one line.
2. **Stdlib** — does the standard library do it? Use it.
3. **Native** — does a platform primitive cover it (DB constraint, CSS, built-in)? Use it.
4. **Existing dep** — does an installed dependency solve it? Never add a new one for what few lines can do.
5. **One-liner** — can it be one expression? Write it.
6. **Minimum** — the least code that makes the test pass.

No premature abstraction: no interface with one implementation, no factory for
one product, no layer added for hypothetical future needs. Deletion over
addition; boring over clever.

Ponytail never licenses skipping: input validation at trust boundaries, error
handling that prevents data loss, security, accessibility, or anything
explicitly requested.
