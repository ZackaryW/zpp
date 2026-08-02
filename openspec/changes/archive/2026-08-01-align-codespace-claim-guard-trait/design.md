## Context

See `proposal.md` for motivation. The packaged profile is the source for new default-profile installations, while an initialized default is deliberately user-owned and immutable under later initialization. Global activation already archives the prior global authored layer before copying a selected profile.

## Goals / Non-Goals

**Goals:**

- Make the packaged advisory match the existing codespace guard authority.
- Repair the current installation without replacing unrelated user-authored profile content.
- Restore the global executable from the current implementation checkout.

**Non-Goals:**

- Changing claim, hook, profile initialization, or activation semantics.
- Introducing automatic profile migrations or a new profile-update command.

## Decisions

- Update the existing trait body rather than duplicating guard policy in workflow skills. The trait owns cross-cutting advisory direction; core and installed hooks retain enforcement.
- Cover the correction through the existing claim-guidance BDD scenario. This keeps behavior at its public resolved-trait boundary and avoids a second scenario for the same trait.
- Repair the current default additively by adding the missing packaged trait and trigger while preserving every other authored byte. Then use `zpp global activate default` so the established archival lifecycle replaces global safely.
- Reinstall the local implementation with `uv tool install --force` so the global entry point and schema reader come from the same source revision.

## Risks / Trade-offs

- [An existing user profile is user-owned and may intentionally differ from packaged state] → Apply only the explicitly missing claim-guard document and trigger; do not refresh other files.
- [Global activation replaces current global authored state] → Use the existing activation command, which first archives that state as a collision-safe profile.
- [The installed executable and source both report 0.9.0] → Verify behavior through codespace status after reinstall instead of relying on version text.

## Migration Plan

1. Add the missing trait document and activation entry to the current default profile.
2. Activate the repaired default globally, preserving prior global state through the existing archive.
3. Force-reinstall ZPP from the implementation checkout.
4. Verify global codespace status and effective global trait resolution.
