# Explicit control flow

State the owning stage, entry gate, completion gate, and next handoff. Automatic
workflow continues across satisfied gates without asking for routine approval.
Pause only for unresolved clarification, a genuinely new product boundary, or
a missing or changed utility shape unless the user establishes another gate.

Name every fallback and its return path. Falling back to an earlier stage must
complete that stage's verification and checkpoint behavior again before moving
forward. A failed command is evidence to diagnose, not permission to weaken the
gate or silently choose a different contract.

Separate advice from authority. Skill lookup is passive metadata. A skill does
not grant mutation, commit, merge, deletion, external coordination, or failed-
gate bypass. Report a true block only after safe in-scope alternatives are
exhausted; otherwise continue through the declared handoff.
