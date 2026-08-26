## ADDED Requirements

### Requirement: Hierarchical workflow instruction ownership
Packaged workflow instructions SHALL have one lowest valid owner. A complete
`zpp-*` playbook SHALL retain only workflow selection, ordered orchestration,
workflow-specific configuration, and branches that cannot be decided by an invoked
component. Behavior repeated by complete playbooks for the same bounded action SHALL
reside in the `zpps-*` stage, adapter, or evidence skill that performs that action.
Lifecycle guarding repeated by multiple `zpps-*` components SHALL reside in
`zpps-workflow-kernel` and SHALL be consumed by concise component references rather
than copied procedures.

Moving shared lifecycle policy to the kernel SHALL NOT make the kernel a dispatcher,
move capability-local declarations or bindings out of their owning component, or
make a bounded component depend on a playbook invocation for standalone admission.
Instructions that are ordinary agent knowledge and add no ZPP-specific constraint,
authority, procedure, result, or failure behavior SHALL be removed rather than moved
to a runtime contract, component JSON, or another skill. The packaged family SHALL
preserve each workflow's complete stage progression and each component's substantive
bounded operation after consolidation.

#### Scenario: Resolve repeated instruction ownership
- **WHEN** the same instruction appears in multiple packaged workflow or component skills
- **THEN** ZPP retains it at the lowest valid workflow, component, or kernel owner, or removes it when it adds no ZPP-specific behavior

