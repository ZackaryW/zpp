## MODIFIED Requirements

### Requirement: Contextual trait consumption
For a selected workflow stage and repository target, the consolidated skill SHALL consume complete trait bodies already injected by ZPP's agent-native hook as contextual policy. The skill SHALL NOT instruct the agent to execute `zpp resolve`, publish `ZPP_CONTEXT`, or bootstrap trait context. The skill SHALL keep platform- and framework-specific policy outside its own invariant workflow contract.

#### Scenario: Specialize BDD shaping for Python
- **WHEN** the hook has injected BDD bodies selected from Python context and the workflow performs feature shaping
- **THEN** the skill applies those complete bodies as advisory context while retaining the same workflow authority boundary

#### Scenario: Inspect workflow bootstrap instructions
- **WHEN** a user inspects the consolidated workflow skill
- **THEN** it contains no instruction to run trait resolution or manage stored trait context

### Requirement: Explicit stage actions
The consolidated workflow skill SHALL require an explicit requested stage for each workflow invocation and SHALL NOT infer the stage from OpenSpec status, repository files, stored environment context, or trait output. When automatic continuation is separately authorized, the skill SHALL expose and execute each next stage as a distinct stage action. Automatic hook resolution SHALL remain stage-neutral and SHALL NOT select or advance a workflow stage.

#### Scenario: Reject an unnamed stage
- **WHEN** a workflow invocation does not identify the requested stage
- **THEN** the skill requests that stage rather than inferring one from current artifacts

#### Scenario: Continue through visible stage actions
- **WHEN** an authorized end-to-end workflow completes one stage and continues
- **THEN** the skill invokes the next stage explicitly without delegating stage choice to the trait hook
