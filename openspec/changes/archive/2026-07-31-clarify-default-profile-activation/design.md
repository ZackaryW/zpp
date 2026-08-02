## Context

The runtime already provisions neutral global state separately from the
user-owned `default` profile. The ambiguity is confined to contract wording
that describes the profile's trigger configuration as activation.

## Goals / Non-Goals

**Goals:**
- Distinguish preset provisioning, explicit profile participation, and
  persistent global activation in the specification and executable examples.

**Non-Goals:**
- Change initialization, trait resolution, profile selection, or global
  activation behavior.

## Decisions

The feature contract will assert that initialization provisions an inactive
preset and that its trigger configuration selects the base traits. Existing
profile-selection and global-activation scenarios remain the executable proof
for the two explicit participation paths.

This keeps each assertion at its public entry point. Reusing the word
"activates" for authored trigger entries was rejected because it conflates
stored configuration with participation in resolution.

## Risks / Trade-offs

- **Risk:** The wording change could accidentally imply that explicit temporary
  profile selection is unsupported. **Mitigation:** Preserve
  `ZPP_PROFILE=default` as a distinct explicit path in the capability contract.
