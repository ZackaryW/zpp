## ADDED Requirements

### Requirement: Immediate-operation component admission
Every packaged `zpps-*` discovery description and bounded procedure SHALL admit work from the caller's immediate necessary operation rather than from an eventual product outcome. When the next necessary work is to discover, compare, or validate unresolved external or repository evidence, admission SHALL select `zpps-explore` and remain read-only even if the caller ultimately intends a dependency, planning, implementation, synchronization, or archive mutation.

A mutating `zpps-*` component SHALL be eligible only when its exact bounded operation is already resolved and either the caller explicitly requests that mutation or an active playbook configures that exact component use. The existence of an active change, a mutating eventual outcome, an imperative verb, or pending tasks SHALL NOT independently admit a mutating component. If component admission remains ambiguous between read-only discovery and mutation, the workflow SHALL select read-only exploration or request one focused clarification before admitting mutation.

When an agent detects that the admitted component does not match the immediate operation, it SHALL report the mismatch to the caller immediately, stop using that component before performing further work, and preserve the result as a failed admission. Any continuation SHALL occur only through a separately admitted component; the misrouted component SHALL NOT reinterpret the request, yield a successful stage result, or continue merely because its internal procedure can inspect related evidence.

#### Scenario: Explore unresolved package integration evidence
- **WHEN** a caller ultimately wants to adopt published packages but the next necessary work is to discover their available versions and validate recent repository integration changes
- **THEN** the workflow admits `zpps-explore`, remains read-only, and does not admit `zpps-apply-change` from the eventual adoption outcome

#### Scenario: Admit an exact requested mutation
- **WHEN** the target and prerequisites of one bounded mutation are resolved and the caller explicitly requests that exact mutation or an active playbook configures it
- **THEN** the workflow may admit the matching mutating `zpps-*` component without treating earlier discovery as implementation authority

#### Scenario: Default ambiguous admission to read-only work
- **WHEN** a request does not establish whether its immediate bounded operation is evidence discovery or a resolved mutation
- **THEN** the workflow uses `zpps-explore` or one focused clarification and admits no mutating component

#### Scenario: Report a detected component mismatch first
- **WHEN** an agent detects that its admitted `zpps-*` component does not match the caller's immediate operation
- **THEN** it reports the failed admission immediately and stops that component before any separately admitted continuation
