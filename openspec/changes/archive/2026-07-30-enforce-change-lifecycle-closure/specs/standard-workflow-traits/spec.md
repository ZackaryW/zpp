## ADDED Requirements

### Requirement: Related change completion boundary
The `automatic-workflow` trait SHALL direct a workflow to treat every OpenSpec
change it selects, creates, or consumes as related workflow state. Before
reporting completion, each related change SHALL be archived, discarded, or
remain active under an identified owning stage.

The related set SHALL remain session-local rather than being persisted in a
product proposal or authored trait. Unrelated active changes SHALL remain
untouched, and workflow completion SHALL NOT require the global active-change
list to be empty.

#### Scenario: Reconcile related changes before completion
- **WHEN** a workflow reaches finalization with related and unrelated OpenSpec changes active
- **THEN** it completes only after every related change has an owned disposition while unrelated changes remain untouched

#### Scenario: Reject an unowned related change
- **WHEN** a consumed related change remains active without an owning stage
- **THEN** the workflow remains incomplete
