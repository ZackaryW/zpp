from __future__ import annotations

import support
from behave import given, then, when


def _environment(context) -> support.Environment:
    environment = support.Environment()
    context.environment = environment
    return environment


@given("a child command that reports ZPP bypass state")
def bypass_reporting_child(context) -> None:
    environment = _environment(context)
    context.child_command = environment.bypass_state_command()


@given("a child command that would leave an execution marker")
def marker_child(context) -> None:
    environment = _environment(context)
    context.child_command = environment.marker_command()


@given("a governed mutation child command")
def governed_mutation_child(context) -> None:
    environment = _environment(context)
    context.child_command = environment.governed_mutation_command()


@when("the owner runs it through an acknowledged ZPP bypass with a reason")
def acknowledged_bypass(context) -> None:
    context.result = context.environment.invoke_bypass(
        context.child_command,
        acknowledge=True,
        reason="owner approved emergency command",
    )


@when("bypass acknowledgement is omitted")
def omitted_acknowledgement(context) -> None:
    context.result = context.environment.invoke_bypass(
        context.child_command,
        acknowledge=False,
    )


@then("the child reports active bypass")
def child_reports_bypass(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "child-bypass=True" in context.result.stdout


@then("ZPP warns before reporting structured bypass state")
def warning_precedes_structured_state(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "WARNING" in context.result.stderr
    assert "owner approved emergency command" in context.result.stderr
    assert '"coordination": "bypassed"' in context.result.stdout


@then("the bypass marker is absent from a later ordinary command")
def bypass_is_not_persistent(context) -> None:
    assert context.environment.ordinary_bypass_state() is False


@then("ZPP refuses to run the child and identifies the missing acknowledgement")
def missing_acknowledgement_rejected(context) -> None:
    assert context.result.exit_code != 0
    assert "acknowledge" in context.result.output.lower()


@then("the child execution marker remains absent")
def marker_is_absent(context) -> None:
    assert not context.environment.marker.exists()
