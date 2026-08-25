from __future__ import annotations

import support
from behave import given, then, when


def _audit(context) -> support.Audit:
    context.audit = support.Audit()
    return context.audit


@given("one reusable mock base project")
def reusable_mock_base(context) -> None:
    _audit(context)


@when("the coordinator assigns the next workflow")
def assign_next_workflow(context) -> None:
    context.assignment = context.audit.assign_next()


@then("one fresh clone has exact Git and OpenSpec identities")
def exact_clone_identities(context) -> None:
    assignment = context.assignment
    assert assignment.repository != context.audit.base_repository
    assert (assignment.repository / ".git").is_dir()
    assert (assignment.repository / "openspec").is_dir()
    context.audit.assert_repository_scope(assignment.repository)


@then("the base was initialized only once")
def one_base_initialization(context) -> None:
    assert context.audit.base_initializations == 1


@when("one synthetic change follows its complete workflow sequence")
def run_one_complete_sequence(context) -> None:
    context.assignment = context.audit.assign_next()
    context.result = context.audit.run_active()


@then("every declared stage and required branch is observed")
def complete_stage_evidence(context) -> None:
    result = context.result
    assert result.recorded_stages == result.declared_stages
    assert all(event.input and event.result and event.decision for event in result.branches)
    assert {event.name for event in result.branches} == {
        "planning-operation",
        "sync",
        "repository-verification",
        "change-verification",
        "finalization",
        "archive",
    }


@then("its result and contamination status are checked before another assignment")
def review_before_advance(context) -> None:
    try:
        context.audit.assign_next()
    except RuntimeError as error:
        assert "review" in str(error)
    else:
        raise AssertionError("another workflow was assigned before result review")
    context.audit.review_active()
    assert context.audit.can_advance
    assert context.result.archive_path.is_dir()
    assert context.result.sentinels_unchanged


@when("one synthetic sequence encounters fixture gaps")
def reconcile_one_sequence(context) -> None:
    context.audit.assign_next()
    context.result = context.audit.run_active()


@then("every initial failure remains in a typed gap ledger")
def gap_ledger(context) -> None:
    assert context.result.gaps
    assert all(gap.kind and gap.observed for gap in context.result.gaps)


@then("fixture repairs are distinguished from unresolved source gaps")
def fixture_closeout(context) -> None:
    assert all(
        gap.closeout == "closed-in-fixture"
        for gap in context.result.gaps
        if gap.kind == "fixture-gap"
    )


@given("one completed workflow result with accepted feedback")
def completed_result_with_feedback(context) -> None:
    audit = _audit(context)
    audit.assign_next()
    context.before = audit.run_active()
    audit.review_active()
    audit.accept_feedback("verification-drift")


@when("the coordinator re-enters the full phases and reruns it")
def rerun_after_full_phases(context) -> None:
    context.after = context.audit.rerun_active()


@then("the same workflow uses a fresh clone and product home")
def fresh_same_workflow_rerun(context) -> None:
    assert context.before.workflow == context.after.workflow
    assert context.before.repository != context.after.repository
    assert context.before.product_home != context.after.product_home
    assert context.after.full_phase_reentry == (
        "planning",
        "shape-bdd",
        "plan-utilities",
        "mature-utilities",
        "wire",
        "form-specs",
        "verify-repository",
        "verify-change",
    )


@then("no later workflow is assigned before its feedback closes")
def no_later_assignment(context) -> None:
    assert set(context.audit.assigned_workflows) == {context.before.workflow}
    assert context.audit.awaiting_review
