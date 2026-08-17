## 1. Bounded artifact-only maintenance

- [x] 1.1 Narrow the packaged workflow skill's artifact-only route to ungoverned artifacts and name the spec-governed exclusion
- [x] 1.2 State in the packaged workflow skill that a spec-governed artifact change reconciles canonical specifications before finalization

## 2. Monorepo behavior ownership

- [x] 2.1 Reconcile the shipped monorepo behavior-ownership paragraph into the canonical specification

## 3. Shipped scenario binding rule

- [x] 3.1 State the scenario binding obligation in the packaged `bdd` trait guidance for each language flavor
- [x] 3.2 State the prose-to-specification routing obligation in the packaged workflow skill's shaping guidance
- [x] 3.3 Reconcile both into the canonical specification

## 4. Withdraw wording assertions

- [ ] 4.1 Remove the literal `SKILL.md` phrase assertions from `verify_workflow_contract`, retaining its artifact parsing and inventory assertions
- [ ] 4.2 Remove the remaining trait-body wording assertions across the contract functions
- [ ] 4.3 Confirm each removed assertion's obligation is present as a canonical requirement, and add the requirement where it is not

## 5. Bind scenarios to the public system

- [ ] 5.1 Replace `register_exact_steps` recorders with bindings that exercise the behavior each step names
- [ ] 5.2 Select verification by scenario rather than running one capability-wide block after every scenario, and remove the `lru_cache` that compensates for the repetition
- [ ] 5.3 Withdraw scenarios describing agent conduct no code observes, confirming each is already a canonical requirement
- [ ] 5.4 Keep each capability root independently runnable

## 6. Path portability

- [x] 6.1 Repair the forward-slash path comparisons in `verify_repository_contract`
- [x] 6.2 Repair the same comparisons in `test_agent_router_adapter` and `test_openlease_adapter`

## 7. Finalization

- [ ] 7.1 Run strict OpenSpec validation and the complete established verification set
- [ ] 7.2 Archive the change and commit the logical update
