## Context

The clarification skill is distributed as a packaged, user-visible workflow artifact. Its temporal-history guidance currently names the authority comparison but does not constrain discovery tightly enough to prevent an open-ended `zmem search` invocation.

## Goals / Non-Goals

**Goals:**

- Make bounded `zmem recall` the only clarification discovery mechanism.
- Preserve `zmem show` for details of an already identified record.
- Keep absent temporal history non-blocking when canonical OpenSpec and repository evidence remain available.

**Non-Goals:**

- Change the general-purpose `zpp-use-zmem` skill or the zmem CLI.
- Remove temporal-history comparison from clarification.

## Decisions

The packaged clarification skill states the command boundary directly because it is the executable workflow contract installed for every supported agent. The workflow BDD surface installs that packaged bundle through the public command and verifies the resulting skill text, matching the repository's existing skill-distribution contract tests.

Broad-search fallback was rejected because it recreates the unbounded operation this change removes. Treating empty recall as an error was rejected because canonical OpenSpec remains current authority and repository evidence can still settle the change.

## Risks / Trade-offs

- [A relevant record is missed by bounded filters] -> Allow additional bounded recall filters and `zmem show` for already identified records, while continuing from current authority when none are found.
- [Packaged and installed skill text diverge] -> Verify the installed projection produced by `zpp workflow install`, not only the source artifact.
