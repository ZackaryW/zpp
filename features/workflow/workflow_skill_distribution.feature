Feature: Install and maintain a complete ZPP workflow integration
  ZPP users can install and maintain the owned workflow bundle, native hooks,
  required OpenSpec operation skills, and compatible standard-profile upgrades.

  Background:
    Given the packaged ZPP workflow bundle contains all twelve permanent skills

  Scenario: Install the bundle locally for explicitly selected agents
    Given the current directory is the root of a Git worktree
    And Codex, Pi, and Claude Code have no local ZPP workflow skills
    And Codex, Pi, and Claude Code have no ZPP integration
    And the current project has no authored ZPP layer
    When the user runs zpp workflow install --local with agents Codex, Pi, and Claude Code
    Then installation succeeds without offering agent selection
    And one managed bundle is installed in the repository-local Codex skill scope
    And one managed bundle is installed in the repository-local Pi skill scope under .pi
    And one managed bundle is installed in the repository-local Claude Code skill scope
    And every selected agent has the current ZPP-managed native lifecycle hooks
    And no repository-local OpenSpec operation skills are installed
    And the current project still has no authored ZPP layer

  Scenario: Install the complete integration globally for explicitly selected agents
    Given Codex, Pi, and Claude Code have no global ZPP workflow skills
    And Codex, Pi, and Claude Code have no global OpenSpec operation skills
    And Codex, Pi, and Claude Code have no ZPP integration
    And the valid persistent default profile is missing newly packaged standard entries
    And its existing authored files, triggers, configuration, and custom traits are recorded
    When the user runs zpp workflow install with agents Codex, Pi, and Claude Code
    Then installation succeeds without offering agent selection
    And one managed bundle is installed in the user-global Codex skill scope
    And one managed bundle is installed in the user-global Pi skill scope under .pi
    And one managed bundle is installed in the user-global Claude Code skill scope
    And every selected agent has its generated OpenSpec core operation skills
    And every selected agent has the current ZPP-managed native lifecycle hooks
    And the detected OpenSpec version is recorded for every generated projection
    And OpenSpec generation used an isolated project beneath the platform temporary directory
    And the temporary project is removed
    And no repository-local skill scope is changed
    And only the missing packaged standard entries are added to the persistent default profile
    And every recorded authored profile entry is unchanged

  Scenario: Codex workflow skills use scope-specific native roots
    Given valid initialized user state
    And the current directory is the root of a Git worktree
    And historical user content under global .agents skills is recorded
    And unrelated global Codex skill content is recorded
    When the user runs zpp workflow install with agent Codex
    Then the Codex global workflow bundle and generated OpenSpec skills coexist under .codex skills
    And no ZPP workflow projection is created or changed under global .agents skills
    And unrelated global Codex skill content is unchanged
    When the user runs zpp workflow install --local with agent Codex and --force
    Then the Codex local workflow bundle is installed under repository .agents skills
    And no Codex workflow bundle is installed under repository .codex skills
    And the global Codex skill roots remain unchanged

  Scenario: Explicitly bootstrap OpenSpec operation skills in local scope
    Given the current directory is the root of a Git worktree
    And Codex, Pi, and Claude Code have no local workflow skills
    When the user runs zpp workflow install --local --with-openspec for Codex, Pi, and Claude Code
    Then every selected agent has the managed ZPP workflow bundle in its native local skill scope
    And Codex has generated OpenSpec core operation skills under .codex
    And Pi has generated OpenSpec core operation skills under .pi
    And Claude Code has generated OpenSpec core operation skills under .claude
    And every selected agent has the current ZPP-managed native lifecycle hooks
    And the current project still has no authored ZPP layer

  Scenario: Install locally into an exact target inside a Git worktree
    Given "C:\work\repo\nested" is an existing directory inside a Git worktree
    And the current directory is outside that worktree
    When the user runs zpp workflow install --local "C:\work\repo\nested" with agent Claude Code
    Then the managed bundle is installed only in that exact directory's local Claude Code skill scope
    And no authored ZPP layer is created or modified

  Scenario Outline: Reject an invalid local target without changes
    Given <target state>
    And every agent skill scope is recorded
    When the user runs zpp workflow install --local <target> with agent Codex
    Then the invocation is rejected as a domain error
    And every agent skill scope is unchanged

    Examples:
      | target state                                      | target          |
      | "C:\missing" does not exist                      | "C:\missing"   |
      | "C:\work\file.txt" is an existing file          | "C:\work\file.txt" |
      | "C:\outside" is an existing directory outside Git | "C:\outside"   |

  Scenario: Default global scope rejects a local target without --local
    Given every agent skill scope is recorded
    When the user runs zpp workflow install "C:\work\repo" with agent Codex
    Then the invocation is rejected as a usage error
    And every agent skill scope is unchanged

  Scenario Outline: Removed and local-only options are rejected in global scope
    Given every agent skill scope is recorded
    When the user runs <invalid invocation>
    Then the invocation is rejected as a usage error
    And every agent skill scope is unchanged

    Examples:
      | invalid invocation                                        |
      | zpp workflow install --global with agent Codex            |
      | zpp workflow install with agent Codex and --force         |
      | zpp workflow install with agent Codex and --with-openspec |

  Scenario: Interactive selection configures all selected agents atomically
    Given an interactive terminal is available
    And every supported agent has no ZPP workflow skills
    When the user runs zpp workflow install --local and selects Pi and Claude Code
    Then one selector offers Pi, Codex, and Claude Code
    And the managed bundle is installed in the selected native local scopes
    And Pi uses its .pi local skill scope
    And Codex receives no workflow projection
    And both selected agents have the current ZPP-managed native lifecycle hooks

  Scenario: Empty and cancelled interactive selection make no changes
    Given an interactive terminal is available
    And every agent skill scope is recorded
    When the user submits zpp workflow install with no checked agent
    Then installation succeeds without changing any agent skill scope
    When the user cancels zpp workflow install from the agent selector
    Then installation is cancelled without changing any agent skill scope

  Scenario: Noninteractive invocation requires explicit agents
    Given no interactive terminal is available
    And every agent skill scope is recorded
    When the user runs zpp workflow install without an agent option
    Then the invocation is rejected as a usage error
    And every agent skill scope is unchanged

  Scenario: A compatible global bundle suppresses local duplication
    Given Codex has a compatible managed global ZPP workflow bundle
    And Codex has no local ZPP workflow bundle
    When the user runs zpp workflow install --local with agent Codex
    Then installation succeeds and reports that the compatible global bundle is reused
    And no local bundle is installed
    When the user repeats zpp workflow install --local with agent Codex and --force
    Then a compatible managed local bundle is installed
    And both managed scopes are reported without claiming scope precedence

  Scenario: An outdated global bundle does not suppress the current local bundle
    Given Claude Code has an outdated managed global ZPP workflow bundle
    And Claude Code has no local ZPP workflow bundle
    When the user runs zpp workflow install --local with agent Claude Code
    Then the current managed bundle is installed locally
    And the differing managed scope versions are reported without selecting one

  Scenario: Installation is idempotent for an already complete managed integration
    Given Pi has a compatible managed global ZPP workflow bundle under .pi
    And Pi has generated OpenSpec core operation skills for the detected recorded version
    And Pi has the current ZPP-managed native lifecycle hooks
    And the persistent default profile already contains every packaged standard entry
    And unrelated files surround every managed projection
    When the user runs zpp workflow install with agent Pi twice
    Then both installations succeed
    And every managed projection is byte-for-byte unchanged
    And OpenSpec skills are not regenerated
    And the unrelated files are byte-for-byte unchanged
    And the persistent default profile is byte-for-byte unchanged

  Scenario: A malformed persistent default blocks global workflow mutation
    Given Pi has no global ZPP integration
    And the persistent default profile is malformed
    When the user runs zpp workflow install with agent Pi
    Then installation fails as a managed-state rejection
    And Pi's workflow skills, OpenSpec skills, and native hooks remain unchanged
    And the malformed persistent default profile is unchanged

  Scenario: Every selected integration destination is preflighted before installation
    Given Pi has no global ZPP integration
    And Claude Code has an unmanaged global conflict at a required OpenSpec skill destination
    When the user runs zpp workflow install with agents Pi and Claude Code
    Then installation fails as a managed-state rejection
    And Pi's workflow skills, OpenSpec skills, and native hooks remain unchanged
    And the conflicting Claude Code content is unchanged

  Scenario: OpenSpec generation failure leaves every selected agent unchanged
    Given every selected agent integration is recorded
    And OpenSpec cannot generate one selected agent's core operation skills
    When the user runs zpp workflow install for those agents
    Then installation fails before committing any selected-agent change
    And every selected agent integration is byte-for-byte unchanged
    And the isolated temporary project is removed

  Scenario: Force never overwrites an unmanaged conflict
    Given Codex has an unmanaged local conflict at a required skill destination
    When the user runs zpp workflow install --local with agent Codex and --force
    Then installation fails as a managed-state rejection
    And the conflicting content is unchanged

  Scenario: Update changes only the selected managed scope
    Given Codex has outdated managed global and forced local ZPP workflow bundles
    And Claude Code has an outdated managed global ZPP workflow bundle
    When the user runs zpp workflow update with agent Codex
    Then only the Codex global managed bundle is updated to the packaged version
    And the forced local Codex bundle is unchanged
    And every Claude Code scope is unchanged
    And the differing Codex scope versions are reported

  Scenario: Global update adds only missing standard-profile entries
    Given Codex has a compatible managed global workflow integration
    And the valid persistent default profile is missing one packaged BDD-structure trait
    And a same-name packaged trait and existing trigger have user-authored content
    When the user runs zpp workflow update with agent Codex
    Then only the absent packaged trait is added to the persistent default profile
    And the same-name user file, existing trigger, configuration, and custom traits are unchanged
    When the user runs zpp workflow update --local with agent Codex
    Then the persistent default profile is byte-for-byte unchanged

  Scenario: Update preserves OpenSpec skills when the recorded version matches
    Given Codex has a managed global workflow integration
    And its OpenSpec projection records the currently detected OpenSpec version
    And the generated OpenSpec skills have distinguishable compatible content
    When the user runs zpp workflow update with agent Codex
    Then the ZPP workflow bundle is updated when needed
    And the generated OpenSpec skills are byte-for-byte unchanged

  Scenario: Update regenerates OpenSpec skills when the version changes
    Given Claude Code has a managed global workflow integration
    And its OpenSpec projection records a different version from the detected OpenSpec version
    When the user runs zpp workflow update with agent Claude Code
    Then the OpenSpec core operation skills are regenerated for Claude Code
    And the newly detected OpenSpec version is recorded
    And unrelated Claude Code content is byte-for-byte unchanged

  Scenario: Unavailable OpenSpec version is recorded as unknown
    Given OpenSpec can generate its core operation skills but cannot report its version
    When the user runs zpp workflow install with agent Codex
    Then the generated OpenSpec projection records an unknown version
    And installation otherwise completes normally

  Scenario: Update an intact historical managed bundle
    Given Codex has a historical managed global workflow bundle that predates one permanent skill
    And unrelated skills surround the historical managed projection
    When the user runs zpp workflow update with agent Codex
    Then the Codex global projection contains the complete current workflow bundle
    And only paths owned by the historical manifest were replaced
    And the unrelated global skills are byte-for-byte unchanged

  Scenario: Update reports an absent selected scope distinctly
    Given Codex has a compatible managed global ZPP workflow bundle
    And Codex has no local ZPP workflow bundle
    When the user runs zpp workflow update --local with agent Codex
    Then update reports that the local projection is not installed
    And it does not describe absent local state as unmanaged content
    And the compatible global bundle remains unchanged

  Scenario: Update rejects a selected scope that is not ZPP-managed
    Given Claude Code has an unmanaged global skill directory matching a permanent skill name
    And every agent skill scope is recorded
    When the user runs zpp workflow update with agent Claude Code
    Then update fails as a managed-state rejection
    And every agent skill scope is unchanged

  Scenario: Removal requires confirmation and removes only managed selected state
    Given Pi has a managed local ZPP workflow bundle surrounded by unrelated skills
    And Pi has generated local OpenSpec operation skills
    And Pi has current ZPP-managed native lifecycle hooks
    And Claude Code has a managed local ZPP workflow bundle
    And the user-owned default profile is recorded
    When the user runs zpp workflow remove --local with agent Pi and declines confirmation
    Then every agent skill scope is unchanged
    When the user runs zpp workflow remove --local with agent Pi and --yes
    Then only the managed Pi ZPP workflow projection is removed
    And Pi's generated OpenSpec operation skills are unchanged
    And Pi's native lifecycle hooks are unchanged
    And the unrelated skills are unchanged
    And the Claude Code projection is unchanged
    And the user-owned default profile is unchanged

  Scenario: Removal defaults to the selected global scope
    Given Pi has managed global and local ZPP workflow bundles
    And unrelated skills surround both managed projections
    When the user runs zpp workflow remove with agent Pi and --yes
    Then only the managed Pi global ZPP workflow projection is removed
    And the managed Pi local ZPP workflow projection is unchanged
    And the unrelated skills are unchanged

  Scenario: Top-level update discovers every installed managed global workflow
    Given valid initialized user state
    And Pi has an outdated managed global ZPP workflow bundle under .pi with no OpenSpec projection
    And Codex has a compatible managed global ZPP workflow bundle with a historical native hook
    And Claude Code has no managed global ZPP workflow bundle
    And unrelated files surround every agent surface
    When the user runs zpp update
    Then Pi and Codex contain the complete current twelve-skill workflow bundle
    And Pi receives generated OpenSpec core operation skills for the detected version
    And both installed workflows have the current ZPP-managed native lifecycle hooks
    And Claude Code receives no workflow, OpenSpec skill, or native hook
    And every unrelated file is byte-for-byte unchanged

  Scenario: Top-level update preserves and regenerates OpenSpec projections by version
    Given valid initialized user state
    And Pi and Claude Code have managed global workflow integrations
    And Pi's OpenSpec projection records the currently detected version with distinguishable content
    And Claude Code's OpenSpec projection records a different version
    When the user runs zpp update
    Then Pi's generated OpenSpec skills are byte-for-byte unchanged
    And Claude Code's OpenSpec core operation skills are regenerated
    And Claude Code records the newly detected OpenSpec version
    And both ZPP workflow bundles are current

  Scenario: One discovered conflict blocks the complete global update
    Given valid initialized user state whose default profile is missing one packaged entry
    And Pi has an outdated managed global workflow integration
    And Claude Code has modified content inside its managed global workflow projection
    And every included global surface is recorded
    When the user runs zpp update
    Then update fails as a managed-state rejection identifying Claude Code
    And the persistent default profile remains unchanged
    And every included hook, workflow bundle, and OpenSpec projection is byte-for-byte unchanged

  Scenario: Top-level update is idempotent and ignores local workflow state
    Given every supported agent has a complete compatible managed global workflow integration
    And their generated OpenSpec projections record the detected version
    And the persistent default profile contains every packaged standard entry
    And compatible and conflicting repository-local workflow projections are recorded
    When the user runs zpp update twice
    Then both updates succeed without rewriting any managed or authored global content
    And no OpenSpec projection is regenerated
    And every repository-local workflow projection is byte-for-byte unchanged

  Scenario: Automatic workflow guidance remains advisory and skill-backed
    Given a participating layer activates a conditionless automatic-workflow trait
    And that trait references the permanent workflow skills through skill lookup
    When the user resolves traits for the target
    Then the effective trait directs unattended continuation only across satisfied gates
    And completed checkpoints, successful verification, and ordinary stage transitions are not human gates
    And the effective trait pauses only for unresolved clarification, a new product boundary, or a missing or changed utility shape
    And the skill lookup remains passive frontmatter metadata
    And the trait does not grant mutation authority or bypass a failed gate

  Scenario: Explicit end-to-end delegation overrides a manual stage pause
    Given a participating layer activates automatic-workflow with mode "manual"
    And the user explicitly delegates the complete change end to end
    When a workflow stage completes with its gate satisfied
    Then the effective guidance directs continuation through the next owning workflow without requesting stage approval
    And the manual configuration remains unchanged
    And the trait still cannot execute a skill or grant mutation authority

  Scenario: Shared guidance is trait-owned rather than repeated across skills
    Given the initialized default profile contains the platform-neutral base traits
    When the user installs the managed bundle for every supported agent
    Then cross-cutting codespace claim, zero-assumption, and Ponytail guidance remains in its owning trait
    And each permanent skill contains only its stage-specific operations and gates
    And hard OpenSpec operation ownership, verification authority, and zmem materiality remain in their owning skills

  Scenario: Generic zmem, lean-audit, and skill-authoring guidance is installed coherently
    Given the packaged default profile contains executable-guarded tool-use traits
    When the user installs the managed bundle for every supported agent
    Then every native projection contains zpp-use-zmem, zpp-lean-audit, and zpp-author-skill
    And use-zmem looks up zpp-use-zmem and zpp-commit-zmem only when the zmem executable is available
    And zpp-use-zmem teaches recall, search, detail inspection, links, output interpretation, and current-authority verification
    And zpp-lean-audit is read-only and substantially attributed to the upstream Ponytail ladder, taxonomy, output, and safety boundaries
    And zpp-lean-audit preserves ZPP's proportional maturity evaluation for external dependencies
    And zpp-author-skill keeps context-continuity and explicit-control-flow guidance in focused references rather than runtime traits

  Scenario Outline: Claim guidance follows workflow automation without granting authority
    Given a participating layer activates codespace-claim-guard
    And automatic-workflow has effective mode <mode>
    When a write-capable ZPP workflow is about to mutate a physical checkout
    Then the claim guard directs <claim behavior>
    And the trait does not treat an OpenSpec workset as ownership
    And the trait rejects supported direct writes into associated read-only members
    And the trait cannot override a conflicting claim or grant mutation authority

    Examples:
      | mode        | claim behavior                                      |
      | "automatic" | automatic acquisition or verification of the claim |
      | "manual"    | prompting before claim acquisition                  |

  Scenario: Installed skill bodies remain platform-neutral
    When the user installs the managed bundle for every supported agent
    Then every native projection contains the same twelve permanent workflow skills
    And each skill retains its required packaged resources and scripts
    And no skill body contains platform, framework, test-runner, or agent-specific policy
    And all Python, Django, TypeScript, and Flutter workflow guidance remains in independent optional traits outside the skill bodies

  Scenario: Explicit behavior configuration keeps runtime authority in core
    Given the managed workflow bundle is installed
    When the user explicitly invokes zpp-configure-behavior for a repository
    Then the skill inspects the established verification structure and initializes zpp.behave.yaml through ZPP
    And it proposes only declarative target and impact relationships
    And it validates the mapping and runs its configured complete audit through ZPP
    And it does not supply runtime executable text, manage Nx plugins, or own filtering and execution

  Scenario: Install explicit codespace worktree reconciliation
    Given a mitigated codespace records its generated project and store branches
    When the user installs the managed bundle for every supported agent
    Then every native projection contains the permanent codespace worktree-reconciliation skill
    And the skill consumes the released claim's generated-checkout and branch metadata
    And reconciliation requires explicit invocation
    And the skill never makes codespace locking merge work automatically
    And successful reconciliation can give every retained branch a disposition before finalization

  Scenario: Related OpenSpec changes receive an owned terminal disposition
    Given a workflow relates a product change, a utility companion, and a temporary internal anchor
    And an unrelated OpenSpec change remains active
    When the mature workflow reaches finalization
    Then the product change is handed to the owning OpenSpec finalizer
    And the verified utility companion and consumed internal anchor are discarded
    And the unrelated active change is left untouched
    And completion requires a final audit of the related change set

  Scenario: Finalized OpenSpec archives become tracked history
    Given a mature product change has formed and checkpointed canonical specifications
    And its active OpenSpec proposal and capability deltas remain uncommitted
    When the owning OpenSpec finalizer archives the product change
    Then the exact finalized archive is handed to zpp-commit-zmem as material repository history
    And the archive checkpoint excludes unrelated active changes and disposable utility plans
    And archiving alone does not require a zmem annotation
    And the repository ignore policy keeps active changes hidden and finalized archives trackable

  Scenario: An unowned related change blocks workflow completion
    Given a consumed related OpenSpec change remains active without an owning stage
    When the workflow evaluates its completion gate
    Then the workflow cannot report completion
    And the unrelated OpenSpec change list is not required to be empty

  Scenario: Current authority and decision history remain distinct
    Given canonical OpenSpec records the currently accepted product behavior
    And zmem records chronological decisions including a later change of direction
    And an active OpenSpec change contains mutable proposal and capability delta specs
    When clarification establishes the product boundary
    Then it compares the later zmem direction with canonical OpenSpec
    And it treats canonical OpenSpec as the long-standing current authority
    And it treats zmem as temporal decision history rather than current product truth
    And it treats the active OpenSpec planning artifacts as temporary working state
    And no zmem dependency graph is required

  Scenario: Clarification classifies request ownership before product bootstrap
    Given a request combines repository-environment tooling and shipped source behavior
    When clarification determines whether product-change bootstrapping applies
    Then it classifies each outcome by observable ownership before listing, selecting, or creating product OpenSpec work
    And it keeps environmental work outside product capability deltas, Gherkin, and canonical specifications
    And it continues the product workflow only for the shipped source behavior
    And it does not classify an outcome from its path or filename alone

  Scenario: Clarification preserves OpenSpec's multi-artifact proposal shape
    Given an OpenSpec proposal declares multiple new or modified capabilities
    When clarification settles behavior for the complete change
    Then proposal.md retains the overview, capability inventory, impact, and unresolved owner decisions
    And each declared capability has its own specs capability delta document
    And settled behavior is persisted into its owning delta before clarification continues
    And design and task artifacts follow the selected OpenSpec schema rather than a ZPP one-file rule

  Scenario: Feature shaping and specification formation preserve artifact ownership
    Given a confirmed OpenSpec change contains proposal and capability delta documents
    When the workflow shapes the complete Gherkin feature set
    Then shaping consumes both proposal and capability delta documents
    And shaping removes only executable examples duplicated by Gherkin
    And shaping preserves stable intent, constraints, invariants, and acceptance obligations
    When mature green behavior later forms canonical specifications
    Then formation reconciles the existing capability deltas
    And formation does not create capability specifications for the first time

  Scenario: Feature shaping preserves justified monorepo subproject ownership
    Given a confirmed change affects public behavior in selected established monorepo subprojects
    When the workflow shapes the complete Gherkin feature set
    Then it identifies justifiably affected subprojects from established repository boundaries
    And it places executable behavior in each affected subproject's native feature surface
    And it does not require one root feature file, framework, runner, or uniform project structure
    And it excludes unaffected subprojects from the feature contract
    And it uses a cross-subproject scenario only for accepted behavior that crosses those boundaries

  Scenario: Memory validation is explicit rather than imposed on every commit
    Given a valid conventional commit message contains no zmem annotation
    When the bundled commit-message validator checks an ordinary commit
    Then validation succeeds with zero zmem annotations
    When the bundled commit-message validator checks a memory-bearing checkpoint
    Then validation fails because a canonical zmem annotation is required

  Scenario: Specification formation keeps history out of current authority
    Given mature green behavior reflects the latest accepted decision
    And zmem retains earlier directions, reversals, and their reasons
    When the workflow forms canonical OpenSpec specifications
    Then only the enduring current behavior enters canonical OpenSpec
    And abandoned or superseded chronology remains in zmem
    And no zmem checkpoint is created merely to mark specification formation
