@blast-surface-permit
Feature: Guard worktree modification behind a declared blast surface
  Nothing modifies a worktree under a session until its affected surface is
  declared, expanded to closure, checked, and explicitly permitted. Reading
  costs nothing. Unlocking is the moment the guarantee is asserted.

  Scenario: Refuse an undeclared modification
    Given a disposable Git worktree with an established session and no declared claim
    When an operation that modifies the worktree runs under that session
    Then the operation is refused
    And the refusal reports that an explicit affected claim is required

  Scenario: Accept a declared claim
    Given a disposable Git worktree with an established session
    When a caller declares an affected claim naming its repository and authority
    Then the session records exactly that claim

  Scenario: Leave read-only resolution permit-free
    Given a disposable Git worktree with an established session
    When traits resolve under that session
    Then resolution succeeds without a declared claim
    And the session holds no lease

  Scenario: Expand a claim to its closure
    Given a registered authority graph where one authority has a dependent authority
    When a claim naming only the depended-upon authority is resolved
    Then the reported closure includes the dependent authority

  Scenario: Report a blocked closure
    Given a resolved closure overlapping an authority leased by another session
    When lockability is evaluated for that closure
    Then the closure is reported as not lockable
    And the report names the conflicting authorities and their blocking owners

  Scenario: Report a lockable closure
    Given a resolved closure overlapping no authority leased by another session
    When lockability is evaluated for that closure
    Then the closure is reported as lockable with its complete resolved membership

  Scenario: Acquire under explicit go-ahead
    Given a reported lockable closure for an established session
    When an explicit go-ahead is given for that closure
    Then the session holds the permit for every authority in the closure

  Scenario: Refuse acquisition without go-ahead
    Given a reported lockable closure for an established session
    When no explicit go-ahead is given
    Then the session holds no permit and no lease exists for that closure

  Scenario: Invalidate a stale closure
    Given a reported lockable closure that changes before acquisition
    When acquisition is attempted against the earlier closure
    Then acquisition is refused
    And the refusal requires re-evaluation and a new go-ahead

  Scenario: Release a boundary-safe session
    Given a session holding a permit whose boundary is safe
    When an explicit unlock targets that session
    Then the held leases are dropped
    And reconciliation debt is recorded for its generated members


  Scenario: Require force authority for a forced unlock
    Given a session holding a permit
    When a forced unlock is requested without explicit force authority
    Then the operation is refused
    And the refusal reports that explicit force authority is required
