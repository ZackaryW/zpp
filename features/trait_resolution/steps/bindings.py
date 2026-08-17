from __future__ import annotations

import support
from behave import given, then, when


@given("a repository carrying an automatic and a manual trait family")
def workspace(context) -> None:
    context.workspace = support.Workspace()
    context.workspace.write_trait("automatic-policy", support.AUTOMATIC_DOCUMENT)
    context.workspace.write_trait("manual-policy", support.MANUAL_DOCUMENT)


@when("a caller resolves the repository for Python")
def resolve_python(context) -> None:
    context.result = context.workspace.resolve("--facet", "language=python")


@when("a caller resolves only the manual family for Python")
def resolve_manual(context) -> None:
    context.result = context.workspace.resolve(
        "--trait", "manual-policy", "--facet", "language=python"
    )


@when("a caller resolves an unknown named family")
def resolve_unknown(context) -> None:
    context.result = context.workspace.resolve(
        "--trait", "no-such-family", "--facet", "language=python"
    )


@when("a caller resolves the repository for Python with explanation")
def resolve_explained(context) -> None:
    context.result = context.workspace.resolve(
        "--facet", "language=python", "--explain"
    )


@when("a caller resolves the repository for an unmatched language")
def resolve_unmatched(context) -> None:
    context.result = context.workspace.resolve("--facet", "language=cobol")


@then("the automatic family's complete body is rendered")
def automatic_rendered(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "automatic policy" in context.result.stdout


@then("the manual family's complete body is rendered")
def manual_rendered(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "manual policy" in context.result.stdout


@then("the manual family's body is not rendered")
def manual_absent(context) -> None:
    assert "manual policy" not in context.result.stdout


@then("no structured diagnostics are rendered")
def no_diagnostics(context) -> None:
    assert not context.result.stdout.lstrip().startswith("{")


@then("structured selection diagnostics are rendered")
def diagnostics_rendered(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout.strip(), "no diagnostics were rendered"
    assert (
        context.result.stdout
        != context.workspace.resolve("--facet", "language=python").stdout
    )


@then("resolution is rejected and identifies the unknown family")
def unknown_rejected(context) -> None:
    assert context.result.exit_code != 0
    assert "no-such-family" in context.result.output


@then("no trait body is rendered")
def nothing_rendered(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "automatic policy" not in context.result.stdout
    assert "manual policy" not in context.result.stdout
