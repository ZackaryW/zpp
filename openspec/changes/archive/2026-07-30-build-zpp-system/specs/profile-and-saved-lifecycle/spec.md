## Purpose

Defines named user profiles and reusable saved override layers as independent, safely managed sources of trait configuration.

## ADDED Requirements

### Requirement: Named profile lifecycle
ZPP SHALL create, list, and remove named profiles under initialized user state. Profile and saved names MUST match `^[a-z0-9][a-z0-9_-]*$`.

Profile creation SHALL produce one neutral authored layer, fill only missing valid state, preserve existing authored bytes, create no derived cache, and reject invalid existing state without partial writes. Listing SHALL emit profile names in lexical order and SHALL succeed silently when empty.

#### Scenario: Create and list profiles
- **WHEN** a user creates absent or already-valid named profiles and then lists them
- **THEN** each profile is one preserved neutral authored layer without a cache and the list contains lexical profile names

#### Scenario: Reject an invalid profile creation
- **WHEN** a requested name is invalid or the named profile contains invalid managed state
- **THEN** creation fails with the relevant name or source identified and complete user state unchanged

### Requirement: Confirmed profile removal
Profile removal SHALL require confirmation unless `--yes` or `-y` is supplied. Confirmed removal SHALL remove only the named profile and its independent cache. Declined removal SHALL change nothing.

Removing the profile currently named by `ZPP_PROFILE` SHALL NOT alter that environment variable or any other profile.

#### Scenario: Remove one profile
- **WHEN** a user confirms removal of a named profile
- **THEN** only that profile and its independent cache are removed while other profiles and `ZPP_PROFILE` remain unchanged

### Requirement: Saved override lifecycle
Saved overrides SHALL remain a command subgroup of profile management while being stored and resolved independently of named profiles. Creating a saved override SHALL require a valid name and an existing directory target, create or preserve one neutral authored saved layer, and create no derived cache.

One saved name MAY bind multiple canonical target directories. Repeating a canonically equivalent binding to the same name SHALL be idempotent. A target already owned by another saved name SHALL be rejected without changing user state.

#### Scenario: Create saved bindings
- **WHEN** a user creates one saved name for one or more valid canonical target directories
- **THEN** one independent authored saved layer exists and every distinct canonical target is bound to that name without rewriting existing authored bytes

#### Scenario: Reject an invalid saved creation
- **WHEN** a saved name is invalid, its target is missing or not a directory, its existing layer is invalid, or its target belongs to another saved name
- **THEN** creation fails with the relevant name, target, or managed source identified and complete user state unchanged

### Requirement: Saved listing and removal
Saved listing SHALL emit one `NAME<TAB>TARGET` line per binding in canonical-target order and SHALL succeed silently when empty.

Saved removal SHALL require confirmation unless bypassed by `--yes` or `-y`. Confirmed removal SHALL remove every binding for the name, its authored layer, and its independent cache while preserving other saved layers, bindings, and caches. Declined removal SHALL change nothing.

#### Scenario: List saved bindings
- **WHEN** a user lists saved overrides
- **THEN** every binding is emitted in canonical-target order without coupling it to named-profile activation

#### Scenario: Remove one saved override
- **WHEN** a user confirms removal of a saved name with one or more bindings
- **THEN** only that name's bindings, authored layer, and independent cache are removed
