from __future__ import annotations

import support
from behave import given, then, when


def _audit(context) -> support.Audit:
    context.audit = support.Audit()
    return context.audit


@given("disposable audit workspaces for every complete workflow")
def disposable_workspaces(context) -> None:
    _audit(context)


@given("completed mock results for every workflow")
def completed_results(context) -> None:
    audit = _audit(context)
    context.results = {
        assignment.workflow: audit.run_mock(assignment)
        for assignment in audit.assignments
    }


@when("a maintainer prepares disposable workflow audit repositories")
def prepare_repositories(context) -> None:
    audit = _audit(context)
    context.results = tuple(
        audit.run_mock(assignment) for assignment in audit.assignments
    )


@when("every synthetic change follows its complete workflow sequence")
def run_complete_sequences(context) -> None:
    context.results = tuple(
        context.audit.run_mock(assignment) for assignment in context.audit.assignments
    )


@when("incomplete mock fixtures are reconciled through closeout")
def reconcile_fixtures(context) -> None:
    context.results = tuple(
        context.audit.run_mock(assignment) for assignment in context.audit.assignments
    )


@when("an accepted workflow gap is rerun")
def rerun_gap(context) -> None:
    assignment = context.audit.assignments[0]
    context.selected = assignment.workflow
    context.before = dict(context.results)
    context.results[assignment.workflow] = context.audit.run_mock(
        assignment, revision=2
    )


@then("one fresh Git and OpenSpec workspace exists per complete workflow")
def fresh_workspaces(context) -> None:
    assert len(context.results) == len(context.audit.assignments)
    repositories = {result.repository for result in context.results}
    assert len(repositories) == len(context.results)
    for result in context.results:
        assert (result.repository / ".git").is_dir()
        assert (result.repository / "openspec").is_dir()


@then("every workspace has a unique isolated ZPP product home")
def isolated_homes(context) -> None:
    homes = {result.product_home for result in context.results}
    assert len(homes) == len(context.results)
    assert all(context.audit.base in home.parents for home in homes)


@then("every declared stage and required branch is observed")
def complete_stage_evidence(context) -> None:
    for result in context.results:
        assert result.recorded_stages == result.declared_stages
        assert set(result.branches) == {
            "planning-operation",
            "sync",
            "repository-verification",
            "change-verification",
            "finalization",
            "archive",
        }


@then("every synthetic change is validated archived and reminder-closed")
def closed_changes(context) -> None:
    for result in context.results:
        assert result.archive_path.is_dir()
        assert "strict-validation" in result.operations
        assert "reminder-stop" in result.operations


@then("every initial failure remains in a typed gap ledger")
def gap_ledger(context) -> None:
    for result in context.results:
        assert result.gaps
        assert all(gap.kind == "fixture-gap" for gap in result.gaps)
        assert all(gap.observed for gap in result.gaps)


@then("fixture repairs are distinguished from unresolved source gaps")
def fixture_closeout(context) -> None:
    for result in context.results:
        assert all(gap.closeout == "closed-in-fixture" for gap in result.gaps)
        assert not any(gap.kind == "source-gap" for gap in result.gaps)


@then("the selected workflow uses a fresh Git OpenSpec and product-home workspace")
def fresh_rerun(context) -> None:
    before = context.before[context.selected]
    after = context.results[context.selected]
    assert before.revision == 1 and after.revision == 2
    assert before.repository != after.repository
    assert before.product_home != after.product_home
    assert before.archive_path != after.archive_path


@then("all other workflow results and superseded evidence remain available")
def preserve_results(context) -> None:
    assert context.before[context.selected].revision == 1
    for workflow, result in context.before.items():
        if workflow != context.selected:
            assert context.results[workflow] is result
