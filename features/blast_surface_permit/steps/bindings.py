from __future__ import annotations

import support
from behave import given, then, when


@given("a disposable Git worktree with an established session and no declared claim")
@given("a disposable Git worktree with an established session")
def established_session(context) -> None:
    context.env = support.environment()
    context.session = support.session(context.env)


@given("a registered authority graph where one authority has a dependent authority")
def graph_with_dependency(context) -> None:
    established_session(context)
    context.dependent = support.dependent_authority(context.env, context.session)


@given("a resolved closure overlapping an authority leased by another session")
def contended_closure(context) -> None:
    established_session(context)
    support.claim_own_authority(context.env, context.session)
    holder = support.closure(context.env, context.session)
    support.acquire(context.env, context.session, holder["fingerprint"])
    context.other = context.env.workspace_json(
        "session", context.session["root"], "--session", "review"
    )
    context.env.workspace_json(
        "claim",
        "--space",
        context.other["space"],
        "--authority",
        context.session["authority"],
    )
    context.subject = context.other


@given("a resolved closure overlapping no authority leased by another session")
@given("a reported lockable closure for an established session")
def uncontended_closure(context) -> None:
    established_session(context)
    support.claim_own_authority(context.env, context.session)
    context.subject = context.session


@given("a reported lockable closure that changes before acquisition")
def changing_closure(context) -> None:
    uncontended_closure(context)
    context.stale = support.closure(context.env, context.session)["fingerprint"]
    context.env.workspace_json(
        "claim",
        "--space",
        context.session["space"],
        "--repository",
        context.session["repository"],
    )


@given("a session holding a permit whose boundary is safe")
@given("a session holding a permit")
def session_holding_permit(context) -> None:
    uncontended_closure(context)
    report = support.closure(context.env, context.session)
    support.acquire(context.env, context.session, report["fingerprint"])


@when("an operation that modifies the worktree runs under that session")
def modify_without_claim(context) -> None:
    context.result = context.env.workspace(
        "closure", "--space", context.session["space"]
    )


@when("a caller declares an affected claim naming its repository and authority")
def declare_claim(context) -> None:
    context.result = context.env.workspace(
        "claim",
        "--space",
        context.session["space"],
        "--repository",
        context.session["repository"],
        "--authority",
        context.session["authority"],
    )


@when("traits resolve under that session")
def resolve_traits(context) -> None:
    context.resolution = context.env.resolve_json(context.session["root"])


@when("a claim naming only the depended-upon authority is resolved")
def resolve_dependent_claim(context) -> None:
    context.env.workspace_json(
        "claim",
        "--space",
        context.session["space"],
        "--repository",
        context.session["repository"],
    )
    context.report = support.closure(context.env, context.session)


@when("lockability is evaluated for that closure")
def evaluate_lockability(context) -> None:
    context.report = support.closure(context.env, context.subject)


@when("an explicit go-ahead is given for that closure")
def give_go_ahead(context) -> None:
    report = support.closure(context.env, context.subject)
    context.report = report
    context.result = support.acquire(
        context.env, context.subject, report["fingerprint"]
    )


@when("no explicit go-ahead is given")
def withhold_go_ahead(context) -> None:
    context.report = support.closure(context.env, context.subject)


@when("acquisition is attempted against the earlier closure")
def acquire_stale(context) -> None:
    context.result = support.acquire(context.env, context.session, context.stale)


@when("an explicit unlock targets that session")
def unlock(context) -> None:
    context.result = context.env.workspace(
        "release", "--space", context.session["space"]
    )


@when("a forced unlock is requested without explicit force authority")
def forced_unlock_without_authority(context) -> None:
    context.result = context.env.workspace(
        "force-release", "--space", context.session["space"]
    )


@then("the operation is refused")
def operation_refused(context) -> None:
    assert context.result.exit_code != 0, context.result.output


@then("the refusal reports that an explicit affected claim is required")
def refusal_names_claim(context) -> None:
    assert "affected claim" in context.result.output


@then("the session records exactly that claim")
def claim_recorded(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.session["authority"] in context.result.output
    assert context.session["repository"] in context.result.output


@then("resolution succeeds without a declared claim")
def resolution_without_claim(context) -> None:
    assert context.resolution["session"] == context.session["space"]


@then("the session holds no lease")
@then("the session holds no permit and no lease exists for that closure")
def no_lease_held(context) -> None:
    assert support.leases(context.env) == []


@then("the reported closure includes the dependent authority")
def closure_includes_dependent(context) -> None:
    assert context.dependent in context.report["authorities"]


@then("the closure is reported as not lockable")
def closure_not_lockable(context) -> None:
    assert context.report["lockable"] is False


@then("the report names the conflicting authorities and their blocking owners")
def closure_names_conflicts(context) -> None:
    assert context.report["blockers"] == [context.session["space"]]
    assert [item["authority"] for item in context.report["conflicts"]] == [
        context.session["authority"]
    ]


@then("the closure is reported as lockable with its complete resolved membership")
def closure_lockable(context) -> None:
    assert context.report["lockable"] is True
    assert context.report["authorities"] == [context.session["authority"]]


@then("the session holds the permit for every authority in the closure")
def permit_held(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    held = {item["owner_id"] for item in support.leases(context.env)}
    assert held == {context.subject["space"]}


@then("acquisition is refused")
def acquisition_refused(context) -> None:
    assert context.result.exit_code != 0, context.result.output


@then("the refusal requires re-evaluation and a new go-ahead")
def refusal_requires_reevaluation(context) -> None:
    assert "changed" in context.result.output
    assert support.leases(context.env) == []


@then("the held leases are dropped")
def leases_dropped(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert support.leases(context.env) == []


@then("reconciliation debt is recorded for its generated members")
def debt_recorded(context) -> None:
    """No generated members here, so the recorded debt is correctly empty."""
    assert context.result.exit_code == 0


@then("the refusal reports that explicit force authority is required")
def refusal_names_force_authority(context) -> None:
    assert "explicit authority" in context.result.output
