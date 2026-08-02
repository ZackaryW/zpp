## MODIFIED Requirements

### Requirement: Named profile lifecycle
ZPP SHALL create, list, and remove named profiles under initialized user state. Profile and saved names MUST match `^[a-z0-9][a-z0-9_-]*$`.

The permanent `default` profile SHALL always be present after initialization and SHALL be listed with other profiles. Profile creation SHALL produce one neutral authored layer, fill only missing valid state, preserve existing authored bytes, create no derived cache, and reject invalid existing state without partial writes. Listing SHALL emit profile names in lexical order.

#### Scenario: Create and list profiles
- **WHEN** a user creates absent or already-valid named profiles and then lists them
- **THEN** each created profile is one preserved neutral authored layer without a cache and the lexical list includes the permanent default

#### Scenario: Reject an invalid profile creation
- **WHEN** a requested name is invalid or the named profile contains invalid managed state
- **THEN** creation fails with the relevant name or source identified and complete user state unchanged

### Requirement: Confirmed profile removal
Profile removal SHALL require confirmation unless `--yes` or `-y` is supplied. Confirmed removal SHALL remove only the named profile and its independent cache. Declined removal SHALL change nothing.

The permanent `default` profile SHALL NOT be removable. Removing the profile currently named by `ZPP_PROFILE` SHALL NOT alter that environment variable or any other profile.

#### Scenario: Remove one profile
- **WHEN** a user confirms removal of a removable named profile
- **THEN** only that profile and its independent cache are removed while other profiles and `ZPP_PROFILE` remain unchanged

#### Scenario: Protect the default profile
- **WHEN** a user requests removal of the permanent default profile
- **THEN** removal is rejected and complete user state remains unchanged
