Feature: Gate concurrent work through explicit ZPP codespaces
  ZPP users can claim multi-project OpenSpec views without unnecessary
  divergence and can mitigate overlapping writable checkouts explicitly.

  Scenario: Lock an uncontested multi-store view without creating worktrees
    Given an OpenSpec workset contains committed projects and governing stores in a defined member order
    And the projects also use a registered store only as a reference
    And no active codespace claims any resolved writable checkout
    When the user runs zpp codespace lock for that workset
    Then ZPP registers a distinct owned OpenSpec workset using every canonical member path
    And one durable codespace claim covers every project and governing store
    And the reference-only store remains shared and unclaimed
    And the snapshot key contains the member commit hashes in OpenSpec workset order
    And no Git worktree is created
    And no editor or agent is opened

  Scenario: Resolve a path-free lock from an existing codespace
    Given the current directory is inside a checkout claimed by one active ZPP codespace
    When the user runs zpp codespace lock without a workset or paths
    Then ZPP identifies the existing codespace
    And no second claim or OpenSpec workset is created

  Scenario: Resolve a path-free lock from applicable OpenSpec worksets
    Given the current project is not part of an active ZPP codespace
    And exactly one OpenSpec workset applies to the current project
    When the user runs zpp codespace lock without a workset or paths
    Then ZPP locks the complete applicable OpenSpec workset
    When multiple OpenSpec worksets instead apply in an interactive terminal
    Then ZPP asks the user to select one workset
    When multiple OpenSpec worksets instead apply without an interactive terminal
    Then locking is rejected without creating a claim or workset

  Scenario: Require an explicit view when current membership cannot be determined
    Given the current directory identifies no active codespace or applicable OpenSpec workset
    When the user runs zpp codespace lock without a workset, workspace descriptor, or paths
    Then locking is rejected without guessing the open editor folders
    When the user repeats locking with an explicit workset, workspace descriptor, or path list
    Then ZPP resolves that explicit view

  Scenario: Preserve ordered commit identity and report dirty state separately
    Given a proposed workset has committed members whose ordered hashes include a duplicate
    And one member contains uncommitted changes
    When the user locks the uncontested workset
    Then the snapshot key preserves every hash and duplicate in member order
    And the dirty member is reported separately from the snapshot key
    And the uncommitted content remains only in its existing checkout

  Scenario Outline: Reject unresolved members without partial state
    Given <unresolved member>
    And all codespace and OpenSpec workset state is recorded
    When the user attempts to lock the workset
    Then locking is rejected with the unresolved member identified
    And all recorded codespace and OpenSpec workset state is unchanged

    Examples:
      | unresolved member                                               |
      | a proposed workset contains a repository without a first commit |
      | an associated store is neither governing nor reference-only     |

  Scenario: Report the complete overlapping writable closure before mitigation
    Given one codespace claims Project A, Project B, and Store 1
    And another proposed view contains Project C, the claimed Project B checkout, and Store 1
    And the claimed Project B checkout has advanced to a new commit
    When the user attempts to lock the proposed view
    Then the conflict report includes Project B and Store 1 together
    And Project B remains conflicting despite its changed current commit
    And Project C is not reported as conflicting
    And no mitigation occurs before the user confirms it

  Scenario: Decline mitigation without changing either view
    Given a proposed codespace conflicts with an active codespace
    And the complete project, store, workset, and claim state is recorded
    When the user declines the grouped mitigation offer
    Then no worktree, branch, claim, or OpenSpec workset is created
    And the complete recorded state is unchanged

  Scenario: Mitigate only the conflicting writable closure
    Given one codespace claims Project A, Project B, and writable Store 1
    And a proposed view contains uncontested Project C, Project B, and Store 1
    And the proposed view starts from the same commit snapshot as the active codespace
    When the user confirms conflict mitigation
    Then Project C continues using its canonical checkout
    And Project B and Store 1 receive distinct sibling worktrees named with the new codespace instance hash
    And each generated worktree branches from its member's snapshotted commit
    And no uncommitted content is copied into a generated worktree
    And the mitigated codespace has a distinct instance identifier despite sharing the starting snapshot
    And its private OpenSpec registry maps the original Store 1 id to the generated Store 1 worktree
    And the shared global OpenSpec registry is unchanged
    And ZPP registers the effective paths as a new owned OpenSpec workset
    And ZPP offers to open the prepared workset without changing the existing open workspace

  Scenario: Preserve a prepared codespace when optional opening is declined
    Given conflict mitigation has prepared a registered codespace workset
    When the user declines the offer to open it
    Then the prepared codespace and its claim remain available
    And the current editor or agent remains unchanged
    When the user later runs zpp codespace open for the prepared codespace
    Then ZPP opens its registered OpenSpec workset with the selected supported opener

  Scenario: Never overwrite an existing mitigation path or branch
    Given mitigation would use a sibling path or branch that already exists
    And the complete project, store, workset, and claim state is recorded
    When the user confirms mitigation
    Then mitigation is rejected without reusing or overwriting the existing path or branch
    And the complete recorded state is unchanged

  Scenario: Add paths by atomically replacing the owned workset
    Given an active codespace owns an OpenSpec workset and claim
    And additional committed paths and their stores introduce no unresolved conflict
    When the user runs zpp codespace add for those paths
    Then ZPP creates a new OpenSpec workset containing the complete resolved membership
    And the original OpenSpec workset is never modified in place
    And the claim transfers atomically to the new codespace
    And the superseded ZPP-owned workset registration is removed

  Scenario: Preserve the original codespace when adding cannot complete
    Given an active codespace owns an OpenSpec workset and claim
    And adding paths would require mitigation
    And the complete original codespace state is recorded
    When the user declines mitigation or replacement creation fails
    Then the original claim and OpenSpec workset remain active and unchanged
    And no replacement codespace is partially registered

  Scenario: Activate or execute within a mitigated private store registry
    Given a mitigated codespace maps original logical store ids to generated store worktrees
    When the user runs zpp codespace activate for that codespace
    Then the resulting shell uses the codespace's private OpenSpec registry
    When the user runs zpp codespace exec for that codespace with an OpenSpec command
    Then that command uses the same private OpenSpec registry
    And both paths preserve the original logical store ids
    And neither path changes shared global OpenSpec registration

  Scenario: Inspect and release a codespace without deleting work
    Given an active codespace has resolved members and a durable claim
    And an unrelated user-owned OpenSpec workset exists
    When the user runs zpp codespace list and zpp codespace status
    Then the active codespace and its claimed membership are inspectable
    When the user runs zpp codespace unlock for the active codespace
    Then its claim and ZPP-owned OpenSpec workset registration are removed
    And every project and store worktree is preserved
    And the unrelated user-owned OpenSpec workset is unchanged

  Scenario: Cleanup removes only safe generated worktrees
    Given an unlocked codespace has one clean generated worktree and one dirty generated worktree
    When the user runs zpp codespace cleanup
    Then the clean ZPP-owned generated worktree is removed
    And the dirty generated worktree and all of its content are preserved
    And no canonical checkout or user-owned worktree is removed

  Scenario: Forced recovery preserves abandoned work
    Given a durable codespace claim was abandoned without being unlocked
    And its generated worktrees may contain dirty files
    When the user explicitly confirms forced recovery
    Then the abandoned claim and its ZPP-owned OpenSpec workset registration are removed
    And every generated worktree and dirty file is preserved
    And no claim expires automatically before that recovery

  Scenario: Codespace preparation never merges isolated work
    Given a mitigated codespace records every generated project and store branch
    When the user locks, adds, opens, unlocks, cleans, or recovers that codespace
    Then ZPP performs no automatic branch merge
    And the recorded branch metadata remains available to the explicit reconciliation workflow
