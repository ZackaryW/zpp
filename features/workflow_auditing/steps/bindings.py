from __future__ import annotations

import support
from behave import given, then, when


def _audit(context) -> support.Audit:
    context.audit = support.Audit()
    return context.audit


@given("the packaged workflow audit")
def packaged_audit(context) -> None:
    _audit(context)


@given("completed results for every workflow audit assignment")
def completed_results(context) -> None:
    audit = _audit(context)
    context.results = {
        assignment.workflow: audit.simulate(assignment)
        for assignment in audit.assignments
    }


@when("a maintainer prepares the packaged workflow audit")
def prepare_audit(context) -> None:
    _audit(context)


@when("every workflow reminder is simulated independently")
def simulate_workflows(context) -> None:
    context.simulations = tuple(
        context.audit.simulate(assignment)
        for assignment in context.audit.assignments
    )


@when("workflow design and implementation evidence is compared")
def compare_evidence(context) -> None:
    context.results = context.audit.compare()


@when("a maintainer reruns one selected workflow")
def rerun_selected(context) -> None:
    assignment = context.audit.assignments[0]
    context.selected = assignment.workflow
    context.before = dict(context.results)
    context.results[assignment.workflow] = context.audit.simulate(
        assignment, revision=2
    )


@then("one distinct audit assignment exists per complete workflow contract")
def exact_assignments(context) -> None:
    assert len(context.audit.assignments) == len(context.audit.workflows)
    assert len({item.workflow for item in context.audit.assignments}) == len(
        context.audit.assignments
    )


@then("every assignment resolves its playbook and component evidence")
def assignments_resolve(context) -> None:
    for assignment in context.audit.assignments:
        assert assignment.contract_path.is_file(), assignment.contract_path
        assert assignment.playbook_path.is_file(), assignment.playbook_path
        assert assignment.component_paths
        assert all(path.is_file() for pair in assignment.component_paths for path in pair)


@then("every simulation exercises lifecycle and checklist updates")
def exercises_updates(context) -> None:
    expected = {"start", "check-match", "check-warning", "upsert", "delete", "record", "resume"}
    assert context.simulations
    assert all(set(item.operations) == expected for item in context.simulations)


@then("simulation state is unique and confined to disposable product homes")
def isolated_state(context) -> None:
    homes = {item.product_home for item in context.simulations}
    assert len(homes) == len(context.simulations)
    assert all(context.audit.base in home.parents for home in homes)
    assert all(home.is_dir() for home in homes)


@then("every workflow result identifies inspected evidence and typed findings")
def typed_results(context) -> None:
    assert set(context.results) == {item.workflow for item in context.audit.assignments}
    for result in context.results.values():
        assert result["evidence"]
        assert isinstance(result["findings"], tuple)
        assert set(result["checks"]) == {"contract", "simulation"}


@then("blocked or unexecuted evidence is not reported as passing")
def truthful_checks(context) -> None:
    assert all(
        result["checks"]["simulation"] == "not-run"
        for result in context.results.values()
    )


@then("the rerun uses a fresh assignment for only that workflow")
def fresh_rerun(context) -> None:
    before = context.before[context.selected]
    after = context.results[context.selected]
    assert before.product_home != after.product_home


@then("all other workflow results remain available")
def other_results_preserved(context) -> None:
    for workflow, result in context.before.items():
        if workflow != context.selected:
            assert context.results[workflow] is result
