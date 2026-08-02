Feature: Resolve effective traits as Markdown
  ZPP users can resolve activated trait documents through global, profile, saved,
  repository, and nested layers without exposing cache or policy internals.

  Scenario: Selecting the default profile resolves the platform-neutral base
    Given a clean user home with initialized ZPP state
    And ZPP_PROFILE is "default"
    And rg, jq, and zmem are unavailable on PATH
    When the user runs zpp resolve for an existing target
    Then resolution succeeds
    And stdout contains exactly these effective trait documents in order:
      | name                  |
      | automatic-workflow    |
      | codespace-claim-guard |
      | zero-assumptions      |
      | ponytail              |
    And automatic-workflow has effective mode "automatic"
    And stdout contains no Python-specific trait

  Scenario: A local configuration changes automatic progression to manual
    Given a clean user home with initialized ZPP state
    And ZPP_PROFILE is "default"
    And the repository layer overrides automatic-workflow mode to "manual"
    When the user runs zpp resolve for the repository target
    Then resolution succeeds
    And automatic-workflow remains active with effective mode "manual"
    And codespace-claim-guard remains active
    And the same platform-neutral base traits remain active

  Scenario Outline: Optional platform workflow traits remain independently selectable
    Given a clean user home with initialized ZPP state
    And ZPP_PROFILE is "default"
    And the repository layer additionally activates <trait>
    When the user runs zpp resolve for the repository target
    Then resolution succeeds
    And stdout contains <trait> with only <responsibility> guidance
    And stdout contains no other optional platform workflow trait

    Examples:
      | trait              | responsibility      |
      | python-bdd         | Behave               |
      | python-tdd         | pytest               |
      | python-build       | the uv environment   |
      | python-django-tdd  | Django testing       |
      | typescript-bdd     | TypeScript BDD       |
      | typescript-tdd     | TypeScript TDD       |
      | flutter-bdd        | Flutter BDD          |
      | flutter-tdd        | Flutter TDD          |

  Scenario: Authored and configured traits remain inactive without a trigger
    Given a clean user home with an initialized global ZPP layer
    And the current directory is an existing target
    And the global layer authors a valid neutral trait
    And the global layer configures that trait
    And the global trait trigger configuration is empty
    When the user runs zpp resolve without a target argument
    Then resolution succeeds
    And stdout is empty
    And stderr is empty

  Scenario: A conditionless rule activates whenever its layer participates
    Given a clean user home with an initialized global ZPP layer
    And the global layer authors a valid neutral trait
    And the global trait trigger configuration contains only that trait name
    When the user runs zpp resolve for an existing target
    Then resolution succeeds
    And stdout contains exactly the complete effective neutral trait document

  Scenario: Fixed triggers activate each matching trait once and exclude forbidden traversal
    Given an existing target contains a matching workspace file for the second alternative of a workspace_contain rule
    And a fixture executable named neutral-tool is available on PATH
    And matching decoy files exist only under .git, an independent cache directory, and a directory symlink
    And the composed trigger rules include matching which and workspace_contain rules for the same neutral trait
    And the composed trigger rules include traits whose only matches are the excluded decoys
    And the composed trigger rules include a trait whose executable is unavailable
    When the user runs zpp resolve for the target
    Then resolution succeeds
    And stdout contains the matching neutral trait exactly once
    And stdout contains no trait matched only through .git, an independent cache directory, or directory symlink traversal
    And stdout contains no trait whose executable is unavailable
    And the resolved skill lookup remains passive frontmatter metadata

  Scenario: A trigger replacement boundary clears inherited activation before later extension
    Given the global layer activates trait alpha
    And the repository-root layer sets trait_overwrites to true without a trait.json file
    And a nested layer uses extending trigger behavior and activates trait beta
    And trait gamma is authored and configured but is not named by an active trigger
    When the user runs zpp resolve for the nested target
    Then resolution succeeds
    And stdout contains exactly the effective trait document named beta

  Scenario: All participating layers compose in established precedence order
    Given an existing target is nested inside a Git worktree
    And ZPP_PROFILE names an existing work profile
    And global, work profile, repository-root, and root-to-target nested layers participate
    And two saved bindings are ancestors of the target with different saved layer names
    And the closer saved binding is nested below the farther saved binding
    And each participating layer supplies a definition or configuration for the same activated neutral trait
    And the closest nested layer supplies the winning description, order, default config, skill lookup, and advisory body
    And successive traitsConfig values contain distinct keys and replacement values for the same nested object key
    When the user runs zpp resolve for the target
    Then resolution succeeds
    And the work profile participates after global
    And only the closest matching saved layer participates
    And repository layers participate from the repository root toward the target
    And the effective trait uses the complete document from the closest nested definition
    And its effective config contains distinct layered keys
    And its latest nested object value replaces rather than recursively merges earlier nested object values

  Scenario: A saved override resolves for a target outside Git
    Given an existing target is outside every Git worktree
    And the target descends from a saved binding
    And global and saved rules activate different neutral traits
    When the user runs zpp resolve for the target
    Then resolution succeeds
    And stdout contains exactly the global and saved effective trait documents in order
    And no repository or subfolder layer is required

  Scenario: Effective trait order is stable after document replacement
    Given traits are first activated in the order alpha, beta, gamma, delta, epsilon, zeta
    And one of those traits is activated by a later duplicate rule
    And gamma and delta have order 100
    And zeta has order 200
    And beta and epsilon have no order
    And alpha originally has an explicit order
    And a later layer completely replaces alpha with an authored document that has no order
    And traitsConfig for zeta contains a config key named order
    When the user runs zpp resolve for the target
    Then resolution succeeds
    And stdout contains exactly these effective trait documents in order:
      | name    |
      | gamma   |
      | delta   |
      | zeta    |
      | alpha   |
      | beta    |
      | epsilon |

  Scenario: Resolution emits a complete native effective trait document
    Given an activated neutral trait has all accepted frontmatter fields
    And its description and advisory body contain UTF-8 text
    And its advisory body contains deliberate whitespace
    And a participating layer overrides part of its config
    When the user runs zpp resolve for the target
    Then resolution succeeds
    And stdout contains exactly one complete Markdown trait document
    And its YAML frontmatter semantically contains name, description, order, effective config, and ordered skill_lookup
    And its body preserves the authored UTF-8 text and whitespace
    And the effective config contains the accepted shallow override

  Scenario Outline: Invalid resolution context fails without fallback
    Given <invalid context>
    When the user runs <invocation>
    Then resolution fails with exit code 1
    And stdout is empty
    And stderr identifies <diagnostic subject> without a stack trace
    And no fallback resolution is returned

    Examples:
      | invalid context                                             | invocation                           | diagnostic subject       |
      | the requested target does not exist                         | zpp resolve for the missing target   | the missing target        |
      | the requested target exists as a file                       | zpp resolve for the file target      | the file target           |
      | ZPP_PROFILE names a profile that does not exist             | zpp resolve for an existing target   | the unknown profile       |
      | the saved index binds the target to a saved layer that does not exist | zpp resolve for an existing target   | the missing saved layer   |
