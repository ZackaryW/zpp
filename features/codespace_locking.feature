Feature: Gate concurrent writes through explicit ZPP codespaces
  ZPP users can claim complete physical checkouts on one machine, isolate real
  conflicts, retain explicit read-only context, and open optional multi-folder
  views without treating those views as write ownership.

  Scenario Outline: Lock an uncontested explicit target set and its writable OpenSpec authority
    Given <input source> names committed project checkouts
    And one project uses a repo-local OpenSpec root
    And another project resolves to an external writable OpenSpec store
    And the projects also use a registered store only as a reference
    And no active codespace claims any resolved physical checkout
    When the user runs zpp codespace lock using <input source>
    Then one durable codespace claim owns every complete project checkout exactly once
    And the claim also owns the external writable store checkout exactly once
    And the repo-local OpenSpec root is covered by its containing project checkout
    And the reference-only store remains shared and unclaimed
    And the claim records each target's full starting commit hash
    And no Git worktree or OpenSpec workset is created
    And no editor or agent is opened

    Examples:
      | input source                     |
      | an explicit workspace descriptor |
      | an explicit path list            |

  Scenario: Lock explicit read-only context without claiming it
    Given explicit writable paths and explicit read-only repository paths have committed heads
    And a read-only repository resolves external OpenSpec stores
    And another active codespace already claims one selected read-only repository
    When the user runs zpp codespace lock with the writable paths and --read-only paths
    Then one codespace view records the writable and read-only repositories with their access roles
    And only the complete writable OpenSpec closure is exclusively claimed
    And no read-only repository is treated as a conflict or receives an isolated worktree
    And related stores of a read-only repository are omitted unless independently selected
    And the same read-only repository can remain in both codespaces

  Scenario: Resolve a path-free lock without using worksets as authority
    Given the current directory is inside a checkout claimed by one active ZPP codespace
    When the user runs zpp codespace lock without paths
    Then ZPP identifies the existing codespace
    And no second claim or OpenSpec workset is created
    Given instead no active claim or explicit input supplies writable targets
    When the user runs zpp codespace lock without paths
    Then locking is rejected without inferring ownership from an OpenSpec workset
    And locking does not guess the folders open in an editor
    When the user repeats locking with an explicit workspace descriptor or path list
    Then ZPP resolves the explicitly requested writable targets

  Scenario: Do not infer a codespace from shared read-only context
    Given the current directory belongs only to a read-only member of one or more codespaces
    When the user runs a codespace command without an identity or activated environment
    Then ZPP requires explicit codespace selection
    And no claim or codespace view is changed

  Scenario: Competing processes cannot acquire the same checkout
    Given two ZPP processes on the same machine request claims containing the same physical checkout
    When both attempt to acquire their complete target sets concurrently
    Then exactly one complete codespace claim becomes active
    And the other request reports the active owner of the conflicting checkout
    And no partial claim remains from the rejected request

  Scenario: Commit movement does not replace an active claim
    Given an active codespace records the full starting commit hashes of its claimed checkouts
    And one claimed checkout later receives file changes and new commits
    When ZPP inspects or re-locks the same effective target set
    Then the existing codespace remains active
    And its starting commit hashes remain unchanged
    And no claim or optional workset generation is replaced because of commit movement
    And current dirty and commit state is reported separately

  Scenario Outline: Reject unresolved targets without partial state
    Given <unresolved target>
    And all codespace claim and optional workset state is recorded
    When the user attempts to lock the requested target set
    Then locking is rejected with the unresolved target identified
    And all recorded codespace claim and optional workset state is unchanged

    Examples:
      | unresolved target                                             |
      | a requested repository has no first commit                    |
      | a selected read-only repository has no first commit           |
      | an associated store is neither writable nor reference-only    |

  Scenario: Report the complete overlapping checkout set before mitigation
    Given one codespace claims Project A, Project B, and writable Store 1
    And another request contains uncontested Project C, the claimed Project B checkout, and Store 1
    And the claimed Project B checkout has advanced to a new commit
    When the user attempts to lock the requested target set
    Then the conflict report includes Project B and Store 1 together
    And Project B remains conflicting despite its changed current commit
    And Project C is not reported as conflicting
    And no mitigation occurs before the user confirms it

  Scenario: Decline mitigation without changing either codespace
    Given a requested codespace conflicts with an active codespace
    And the complete project, store, optional workset, and claim state is recorded
    When the user declines the grouped mitigation offer
    Then no worktree, branch, claim, or OpenSpec workset is created
    And the complete recorded state is unchanged

  Scenario: Mitigate only conflicting physical checkouts
    Given one codespace claims Project A, Project B, and writable Store 1
    And another request contains uncontested Project C, Project B, and Store 1
    And the requested codespace begins from the same starting commits as the active codespace
    When the user confirms conflict mitigation
    Then Project C continues using its canonical checkout
    And Project B and Store 1 receive distinct sibling worktrees named from the new codespace instance
    And each generated worktree branches from its target's recorded starting commit
    And no uncommitted content is copied into a generated worktree
    And the mitigated codespace claims the isolated physical checkouts
    And its private OpenSpec registry maps the original Store 1 id to the isolated Store 1 checkout
    And the shared global OpenSpec registry is unchanged
    And no OpenSpec workset is created until opening is requested
    And ZPP offers to open the prepared codespace without changing the existing workspace

  Scenario: Opening maintains one optional projection per active codespace
    Given a prepared codespace with writable and read-only members has no OpenSpec workset projection
    When the user declines the offer to open it
    Then the prepared codespace and its claim remain available without a projection
    And the current editor or agent remains unchanged
    When the user later runs zpp codespace open for the prepared codespace
    Then ZPP creates and opens one owned projection named `zpp-<instance>-g<generation>`
    And the projection contains the complete writable and read-only view
    And repeated opening reuses that projection while its effective paths are unchanged
    When the codespace membership or effective paths later change
    Then opening replaces the projection with the next structural generation
    And the superseded ZPP-owned projection is removed

  Scenario: Never overwrite an existing mitigation path or branch
    Given mitigation would use a sibling path or branch that already exists
    And the complete project, store, optional workset, and claim state is recorded
    When the user confirms mitigation
    Then mitigation is rejected without reusing or overwriting the existing path or branch
    And the complete recorded state is unchanged

  Scenario Outline: Edit every supported codespace membership transition
    Given an active codespace contains committed writable and read-only members
    When the user runs zpp codespace edit with <operation> for a committed path and --yes
    Then ZPP applies <effect> to the complete successor shape
    And the narrower zpp codespace add command is unavailable

    Examples:
      | operation       | effect                                      |
      | --add           | a new exclusively claimed writable member  |
      | --add-read-only | a new non-owning read-only member           |
      | --remove        | removal of the selected member              |
      | --promote       | promotion from read-only to writable        |
      | --demote        | demotion from writable to read-only         |

  Scenario: Replace an edited codespace identity atomically
    Given an active codespace has a durable mixed-access shape and may have one optional projection
    And the complete original codespace state is recorded
    When one valid edit changes several members and access roles
    Then one successor identity and snapshot are calculated from the resulting roles, paths, and current full commits
    And the successor atomically replaces the superseded active identity and writable claim
    And no unlocked interval or partial successor shape is observable
    And the superseded projection is removed or replaced with the successor projection
    And later file changes and commits do not automatically recalculate the successor identity

  Scenario: Confirm an interactive edit before replacing its existing lock
    Given a shape-changing edit targets an active codespace without --yes or -y
    When the user accepts the complete successor shape
    Then ZPP separately asks to release the superseded lock
    When the user accepts the release confirmation
    Then ZPP performs the atomic successor replacement
    Given instead the user declines either confirmation
    Then the original identity, claim, shape, and optional projection remain unchanged

  Scenario: Explicit yes authority covers both edit confirmations
    Given a shape-changing edit targets an active codespace
    When the user runs zpp codespace edit with --yes or -y
    Then both replacement confirmations are preauthorized
    And ZPP performs the same atomic successor replacement

  Scenario: Reject an invalid or failed edit without changing the codespace
    Given an edit contains contradictory operations or cannot complete validation, mitigation, or replacement
    And the complete original codespace state is recorded
    When the user attempts the edit
    Then the edit is rejected before any partial successor becomes active
    And the original identity, claim, shape, and optional projection remain unchanged

  Scenario: Leave an unchanged edit as a no-op
    Given an edit produces the existing effective membership, roles, and paths
    When the user runs zpp codespace edit
    Then the existing identity and snapshot remain unchanged
    And ZPP requests no replacement confirmation

  Scenario: Preserve generated work across a shape edit
    Given an active codespace contains retained, removed, and demoted generated writable members
    When the user confirms the shape edit
    Then retained generated members transfer to the successor identity
    And removed generated worktrees and branches remain reconciliation debt under the superseded identity
    And a demoted member references its canonical checkout read-only in the successor
    And its generated worktree and branch remain superseded reconciliation debt
    And no generated content is deleted

  Scenario: Activate or execute within a mitigated private store registry
    Given a mitigated codespace maps original logical store ids to isolated store checkouts
    When the user runs zpp codespace activate for that codespace
    Then the resulting shell uses the codespace's private OpenSpec registry
    When the user runs zpp codespace exec for that codespace with an OpenSpec command
    Then that command uses the same private OpenSpec registry
    And both paths preserve the original logical store ids
    And neither path changes shared global OpenSpec registration

  Scenario: Inspect and release a codespace without deleting work
    Given an active codespace has writable and read-only physical checkout targets and a durable claim
    And an unrelated user-owned OpenSpec workset exists
    When the user runs zpp codespace list and zpp codespace status
    Then the active codespace and every writable and read-only member are inspectable with their access roles
    And no read-only member is reported as claimed, generated, or pending reconciliation merely for joining the view
    When the user runs zpp codespace unlock for the active codespace
    Then its write ownership and optional ZPP-owned projection are removed
    And every project and store worktree is preserved
    And only outstanding generated-checkout and branch reconciliation debt is retained
    And the unrelated user-owned OpenSpec workset is unchanged

  Scenario: Cleanup and finalization preserve unresolved work
    Given a released codespace has a clean generated worktree and a dirty generated worktree
    When the user runs zpp codespace cleanup
    Then only the clean ZPP-owned generated worktree is removed
    And the dirty generated worktree and all of its content are preserved
    And no canonical checkout or user-owned worktree is removed
    When every retained branch is reconciled or explicitly abandoned and generated worktrees are gone
    And the reconciliation workflow or user runs zpp codespace finalize
    Then the released record is removed

  Scenario: Recovery removes only provably orphaned ZPP state
    Given a durable codespace claim was abandoned without being unlocked
    And its generated worktrees may contain dirty files
    And orphaned ZPP-owned projections and unrelated user-owned worksets exist
    When the user explicitly confirms forced recovery
    Then the abandoned claim and its orphaned ZPP-owned projections are removed
    And every generated worktree and dirty file is preserved
    And the unrelated user-owned worksets are unchanged
    And no active claim expires automatically before that recovery

  Scenario: Mutating boundaries discard only orphaned projections
    Given a ZPP-owned workset projection is absent from the durable active codespace index
    And user-owned worksets, branches, and worktrees also exist
    When the user runs any mutating zpp codespace command
    Then the orphaned ZPP-owned projection is removed
    And no user-owned workset, branch, or worktree is removed

  Scenario: Finalized history does not grow the active catalog
    Given codespaces have previously used many different target combinations
    And every released generated checkout and branch has received a final disposition
    When those released codespaces are finalized
    Then the durable catalog retains only active claims and unresolved generated work
    And it retains no complete historical workset projections for the finalized codespaces

  Scenario: Codespace lifecycle never merges isolated work
    Given a mitigated codespace records every generated project and store branch
    When the user locks, edits, opens, unlocks, cleans, recovers, or finalizes that codespace
    Then ZPP performs no automatic branch merge
    And the recorded branch metadata remains available until the explicit reconciliation workflow gives it a disposition

  Scenario: Agent guards reject writes to associated read-only context
    Given an agent is associated with a codespace containing a read-only repository
    When a supported direct edit or write targets that read-only repository
    Then the installed agent guard rejects the mutation as read-only in the associated codespace
    And unsupported tools, arbitrary shell effects, manual editor actions, and cross-machine writes remain outside the guarantee
