## ADDED Requirements

### Requirement: Stage-owned OpenSpec change disposition
Permanent workflow skills SHALL own the lifecycle operations appropriate to
their stages. Clarification SHALL establish the session-local related set.
Utility planning SHALL register its companion as disposable, and utility
maturity SHALL discard it and verify its absence before wiring. Specification
formation SHALL hand the product change to the owning OpenSpec finalizer and
then audit the related set.

A consumed internal anchor whose consumer condition is satisfied SHALL be
discarded. Genuinely unfinished related work MAY remain active only under an
identified owning stage. A consumed related change without an owner SHALL block
the workflow completion claim.

#### Scenario: Apply stage-owned terminal dispositions
- **WHEN** a mature workflow disposes its utility scaffolding and finalizes its product change
- **THEN** the owning skills verify those dispositions and reject completion if any consumed related change remains unowned
