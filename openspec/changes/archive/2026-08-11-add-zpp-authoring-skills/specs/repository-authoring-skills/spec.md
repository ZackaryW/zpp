## ADDED Requirements

### Requirement: Packaged manual authoring skill set
ZPP SHALL package exactly `zpp-configure-behave` and `zpp-author-trait` as portable Agent Router skills. Each skill SHALL be a manually invoked operation guide for an explicit repository-authoring request and SHALL NOT run from an agent hook, trait activation, workflow stage transition, initialization side effect beyond projection, or repository detection alone. The skills SHALL introduce no new ZPP command and SHALL use only existing public repository commands and files.

#### Scenario: Inspect the packaged authoring inventory
- **WHEN** a caller loads ZPP's packaged authoring skills
- **THEN** it receives `zpp-configure-behave` followed by `zpp-author-trait` as valid detached Agent Router skills

#### Scenario: Leave authoring skills dormant
- **WHEN** an installed agent starts a session or runs the consolidated workflow without an explicit behavior-mapping or trait-authoring request
- **THEN** neither authoring skill edits a repository, invokes verification, resolves a trait, or advances workflow state

### Requirement: Repository behavior mapping authoring guidance
The `zpp-configure-behave` skill SHALL guide an agent to discover the containing Git worktree, inspect existing repository-owned verification entry points and any root `zpp.behave.yaml`, and create or revise that dedicated version-one mapping only for an explicit owner request. It SHALL use `zpp behave init` for absent mapping initialization, preserve valid authored declarations not in scope, and configure only explicit `argv`, `nx`, or `go-task` providers supported by ZPP.

The skill SHALL derive executable arguments only from existing repository configuration or an explicit owner choice. It SHALL segment targets around stable independently executable or cacheable verification boundaries, keep target identities stable and ordered, associate repository paths conservatively, and use command-local gates only as stable target subsets. Shared, unmapped, invalid, or uncertain impact SHALL remain eligible to broaden selection according to ZPP runtime policy; the skill SHALL NOT optimize by creating a false-negative path exclusion, embedding shell syntax, inventing a command, or granting a mapping workflow-completion authority.

After authoring, the skill SHALL validate the mapping and exercise the owner-selected relevant exact, affected, gate, or complete ZPP behavior surface without treating a failed or insufficient result as success.

#### Scenario: Segment an established verification surface
- **WHEN** an owner asks the skill to configure behavior coordination and repository evidence establishes several independently executable verification boundaries
- **THEN** the skill authors stable ordered targets and conservative path rules using an explicitly supported provider and existing executable arguments

#### Scenario: Refuse an invented provider command
- **WHEN** repository evidence and owner input do not establish the command or provider arguments required by a proposed mapping
- **THEN** the skill leaves that executable declaration unresolved and requests the missing owner choice instead of guessing or writing it

#### Scenario: Preserve broad fallback for shared impact
- **WHEN** common infrastructure or an uncertain changed path can affect more than one declared target
- **THEN** the authored mapping preserves ZPP's ability to select every potentially affected target rather than excluding work for segmentation efficiency

### Requirement: Repository trait authoring guidance
The `zpp-author-trait` skill SHALL guide an agent to discover the containing Git worktree and create or revise one requested `.zpp/traits/{family}.toml` document. It SHALL use the existing `zpp trait init` operation when initialization is needed and SHALL keep the document bound to one basename-derived family with complete ordered flavors.

The skill SHALL select `automatic`, `manual`, or `always-run` activation and `first-win`, `all`, or `extend` selection from the owner's requested behavior; use `repository-overwrite` only for an explicit repository-level replacement; distinguish known-context `[trait.facet]` constraints from observable `[[trait.when]]` evidence; and give every flavor a complete `[trait.content].body`. It SHALL NOT introduce body inheritance, templates, providers, workflow authority, stage control, or activation by prose alone.

After authoring, the skill SHALL validate the document and use focused `zpp resolve --trait ... --explain` invocations with representative explicit facets or repository evidence to inspect selection, ordering, dominance, backfilled context, and unmatched behavior. It SHALL preserve unrelated families and SHALL NOT make an unmatched manual flavor contribute a forced body.

#### Scenario: Author an always-run repository trait
- **WHEN** an owner requests repository guidance that must participate in every common resolution
- **THEN** the skill authors one `always-run` family whose self-contained flavors remain governed by its declared selection policy without granting operational authority

#### Scenario: Author evidence-backed specialization
- **WHEN** an owner requests a flavor selected from observable repository evidence with facets reusable by other families
- **THEN** the skill places observable predicates under `trait.when`, descriptive constraints under `trait.facet`, and validates the derived context and selected complete body through explanation output

#### Scenario: Preserve explicit manual activation
- **WHEN** an owner requests a manual family
- **THEN** the skill verifies that common resolution excludes it and direct named resolution applies normal matching without forcing unmatched content
