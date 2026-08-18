from __future__ import annotations

import support
from behave import given, then, when


@given("a disposable Git worktree")
def disposable_worktree(context) -> None:
    context.env = support.environment()
    context.worktree = context.env.worktree()


@given("an established session")
@given("an established session and the packaged skill describing destructive authority")
def established_session(context) -> None:
    disposable_worktree(context)
    context.session = context.env.workspace_json("session", str(context.worktree))
    context.guidance = support.workspace_guidance()


@given("a released session")
def released_session(context) -> None:
    established_session(context)
    env = context.env
    env.workspace_json(
        "claim",
        "--space",
        context.session["space"],
        "--authority",
        context.session["authority"],
    )
    report = env.workspace_json("closure", "--space", context.session["space"])
    env.workspace_json(
        "permit",
        "--space",
        context.session["space"],
        "--fingerprint",
        report["fingerprint"],
    )
    env.workspace_json("release", "--space", context.session["space"])


@given("the public coordination command help is available")
def coordination_help(context) -> None:
    context.env = support.environment()
    context.help = context.env.workspace("--help")


@given("a registered topology with an established session and a held permit")
def session_with_permit(context) -> None:
    established_session(context)
    context.env.workspace_json(
        "claim",
        "--space",
        context.session["space"],
        "--authority",
        context.session["authority"],
    )
    report = context.env.workspace_json("closure", "--space", context.session["space"])
    context.env.workspace_json(
        "permit",
        "--space",
        context.session["space"],
        "--fingerprint",
        report["fingerprint"],
    )
    context.before = support.state_signature(context.env)


@given("two registered repositories with no declared relationship between them")
def two_repositories(context) -> None:
    context.env = support.environment()
    first = context.env.worktree("first")
    second = context.env.worktree("second")
    context.session = context.env.workspace_json("session", str(first))
    context.other = context.env.workspace_json("session", str(second))


@when("a caller establishes the session and acquires a permit through ZPP")
def full_permit_cycle(context) -> None:
    env = context.env
    context.session = env.workspace_json("session", str(context.worktree))
    context.results = [
        env.workspace(
            "claim",
            "--space",
            context.session["space"],
            "--authority",
            context.session["authority"],
        )
    ]
    report = env.workspace_json("closure", "--space", context.session["space"])
    context.results.append(
        env.workspace(
            "permit",
            "--space",
            context.session["space"],
            "--fingerprint",
            report["fingerprint"],
        )
    )
    context.results.append(
        env.workspace("release", "--space", context.session["space"])
    )


@when("a caller requests a coordination operation ZPP does not expose")
def unsupported_operation(context) -> None:
    context.result = context.env.workspace("space-create", "--space", "anything")


@when("a caller inspects status and closure")
def inspect_only(context) -> None:
    context.env.workspace_json("status")
    context.report = context.env.workspace_json(
        "closure", "--space", context.session["space"]
    )
    context.after = support.state_signature(context.env)


@when("a handoff disposition is requested without the explicit authority argument")
def handoff_without_authority(context) -> None:
    context.result = context.env.workspace(
        "handoff", "--space", context.session["space"], "--disposition", "integrated"
    )


@when("a handoff disposition is requested with the explicit authority argument")
def handoff_with_authority(context) -> None:
    context.result = context.env.workspace(
        "handoff",
        "--space",
        context.session["space"],
        "--disposition",
        "integrated",
        "--authorize",
        "owner-confirmed",
    )


@when("cleanup is requested with only that instruction behind it")
def cleanup_with_instruction_only(context) -> None:
    context.result = context.env.workspace(
        "cleanup",
        "--space",
        context.session["space"],
        "--repository",
        context.session["repository"],
    )


@when("a session for one claims the other")
def claim_unrelated(context) -> None:
    context.result = context.env.workspace(
        "claim",
        "--space",
        context.session["space"],
        "--repository",
        context.other["repository"],
    )


@then("every operation succeeds through the ZPP command surface")
def operations_succeed(context) -> None:
    for result in context.results:
        assert result.exit_code == 0, result.output


@then("the packaged workspace guidance names no provider executable")
def guidance_names_no_provider(context) -> None:
    guidance = support.workspace_guidance()
    assert not support.names_provider_executable(guidance)
    assert "zpp workspace" in guidance


@then("ZPP reports the operation as unavailable")
def operation_unavailable(context) -> None:
    assert context.result.exit_code != 0
    assert "No such command" in context.result.output


@then("the report does not direct the caller to the provider executable")
def report_avoids_provider(context) -> None:
    assert not support.names_provider_executable(context.result.output)


@then("the observed state is reported")
def state_reported(context) -> None:
    assert context.report["lockable"] is False or context.report["authorities"]


@then("the registered topology sessions and leases are unchanged")
def state_unchanged(context) -> None:
    assert context.after == context.before


@then("the operation is refused")
def operation_refused(context) -> None:
    assert context.result.exit_code != 0, context.result.output


@then("the refusal names the authority required")
def refusal_names_authority(context) -> None:
    assert "explicit authority" in context.result.output


@then("no disposition is recorded")
def no_disposition(context) -> None:
    spaces = context.env.state()["spaces"]
    assert all(item["handoff_disposition"] is None for item in spaces)


@then("exactly that operation is executed and the recorded disposition is reported")
def disposition_recorded(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    spaces = context.env.state()["spaces"]
    recorded = {item["identifier"]: item["handoff_disposition"] for item in spaces}
    assert recorded[context.session["space"]] == "integrated"


@then("the operation is refused because only the validated argument satisfies the gate")
def instruction_is_not_authority(context) -> None:
    assert context.result.exit_code != 0
    assert "explicit authority" in context.result.output
    assert "authority" in context.guidance


@then("the widened portion is refused")
def widened_refused(context) -> None:
    assert context.result.exit_code != 0, context.result.output


@then("the report names the additional target and what must be declared")
def widened_report(context) -> None:
    assert context.other["repository"] in context.result.output
    assert "relationship" in context.result.output
