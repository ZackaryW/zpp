---
name: zpp-lean-audit
description: Perform a read-only whole-codebase audit for unnecessary complexity using Dietrich Gebert's Ponytail ladder and finding taxonomy plus ZPP's proportional dependency evaluation. Use when asked to audit bloat, over-engineering, needless abstractions, hand-rolled facilities, or dependency fit; never apply the findings.
---

# Lean audit

Attribute the audit method to
[`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail). Read the
relevant code and trace its real flow before judging it. Then stop at the first
Ponytail rung that holds: omit an unnecessary need; reuse the codebase; use the
standard library; use the native platform; reuse an installed dependency; use
one direct expression; otherwise keep only the minimum implementation.

Scan the whole requested surface. Hunt dead flexibility, duplicated helpers,
single-implementation abstractions, one-product factories, delegating wrappers,
unused flags/configuration, hand-rolled standard facilities, and dependencies
whose purpose is already native.

Tag each finding with the upstream taxonomy:

- `delete:` nothing should replace it.
- `stdlib:` name the standard facility that replaces it.
- `native:` name the platform facility that replaces it.
- `yagni:` defer a speculative layer or flexibility.
- `shrink:` preserve behavior with a smaller direct form.

For a proposed external dependency, also compare requirement complexity with
package maturity, maintenance, integration cost, transitive weight, and the
proportion of its feature surface actually needed. Recommend it when that fit
is better than a small maintained implementation; reject heavyweight imports
for a narrow need. Do not enforce a universal percentage threshold.

Rank findings by the largest justified cut. Output one line per finding:
`<tag> <what to cut>. <replacement>. [path]`. End with an estimated net line
and dependency reduction, or `Lean already. Ship.` when no cut is justified.

Remain read-only. Do not remove trust-boundary validation, data-loss handling,
security controls, accessibility, or the smallest runnable check. Route
correctness, security, and performance findings to their owning review.
