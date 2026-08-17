from __future__ import annotations

import support
from behave import given, then, when

from zpp.core.models import ActivationMode, SourceKind


@given("a bdd trait document with ordered python, python-uv, and flutter flavors")
def ordered_document(context) -> None:
    context.values = support.document(
        support.flavor("python body", language="python"),
        support.flavor("python uv body", language="python", build_tool="uv"),
        support.flavor("flutter body", language="flutter"),
    )


@given("a trait document that omits activation metadata")
def document_without_activation(context) -> None:
    context.values = support.document(support.flavor("body"))


@given("a trait document that declares manual activation")
def document_with_manual_activation(context) -> None:
    context.values = support.document(support.flavor("body"), activation="manual")


@given("a trait document that declares an unsupported activation mode")
def document_with_bad_activation(context) -> None:
    context.values = support.document(support.flavor("body"), activation="whenever")


@given("a trait document whose second flavor has no content body")
def document_missing_body(context) -> None:
    context.values = support.document(
        support.flavor("body"),
        {"facet": {"language": "python"}},
    )


@given("a trait document with an unsupported selection policy")
def document_bad_selection(context) -> None:
    context.values = support.document(support.flavor("body"), selection="sometimes")


@given("a trait document whose flavor declares a non-string categorical facet")
def document_bad_facet(context) -> None:
    context.values = {
        "meta": {"selection": "extend"},
        "trait": [{"facet": {"language": 7}, "content": {"body": "body"}}],
    }


@given("repository space and global sources contribute ordered bdd documents")
def layered_sources(context) -> None:
    context.decoded = (
        support.decode(
            support.document(
                support.flavor("global one"), support.flavor("global two")
            ),
            kind=SourceKind.GLOBAL,
            identifier="global",
        ),
        support.decode(
            support.document(support.flavor("space one")),
            kind=SourceKind.SPACE,
            identifier="space",
        ),
        support.decode(
            support.document(support.flavor("repository one"), activation="manual"),
            kind=SourceKind.REPOSITORY,
            identifier="repository",
        ),
    )


@given("the repository bdd document declares repository-overwrite mode")
def overwrite_sources(context) -> None:
    context.decoded = (
        support.decode(
            support.document(support.flavor("global one")),
            kind=SourceKind.GLOBAL,
            identifier="global",
        ),
        support.decode(
            support.document(support.flavor("space one")),
            kind=SourceKind.SPACE,
            identifier="space",
        ),
        support.decode(
            support.document(
                support.flavor("repository one"),
                selection="first-win",
                mode="repository-overwrite",
            ),
            kind=SourceKind.REPOSITORY,
            identifier="repository",
        ),
    )


@given("a global trait document declares repository-overwrite mode")
def global_overwrite(context) -> None:
    context.values = support.document(
        support.flavor("body"), mode="repository-overwrite"
    )
    context.kind = SourceKind.GLOBAL


@when("ZPP loads the trait document")
def load_document(context) -> None:
    context.decoded_document = support.decode(context.values)


@when("ZPP validates the document")
def validate_document(context) -> None:
    kind = getattr(context, "kind", SourceKind.REPOSITORY)
    try:
        support.decode(context.values, kind=kind)
    except Exception as error:
        context.error = error
    else:
        context.error = None


@when("ZPP composes the effective bdd family")
def compose_family(context) -> None:
    context.composed = support.compose(*context.decoded)


@then("the document basename identifies the bdd family")
def family_named(context) -> None:
    assert context.decoded_document.family == "bdd"


@then("the flavors retain their authored order and complete bodies")
def flavors_ordered(context) -> None:
    assert [item.content.body for item in context.decoded_document.flavors] == [
        "python body",
        "python uv body",
        "flutter body",
    ]


@then("no flavor body is assembled from another flavor")
def flavors_independent(context) -> None:
    bodies = [item.content.body for item in context.decoded_document.flavors]
    assert len(set(bodies)) == len(bodies)
    assert all(bodies.count(body) == 1 for body in bodies)


@then("the family activation is automatic")
def activation_automatic(context) -> None:
    assert context.decoded_document.activation is ActivationMode.AUTOMATIC


@then("the family activation is manual")
def activation_manual(context) -> None:
    assert context.decoded_document.activation is ActivationMode.MANUAL


@then("the complete document is rejected")
def document_rejected(context) -> None:
    assert context.error is not None, "document was accepted"


@then('the failure identifies "{fragment}"')
def failure_identifies(context, fragment: str) -> None:
    assert fragment in str(context.error), str(context.error)


@then("the failure is a trait validation error rather than a stack trace")
def failure_is_typed(context) -> None:
    assert type(context.error).__name__ == "TraitValidationError"


@then("repository flavors precede space flavors which precede global flavors")
def layered_order(context) -> None:
    assert support.bodies(context.composed) == [
        "repository one",
        "space one",
        "global one",
        "global two",
    ]


@then("the repository document supplies the effective activation policy")
def repository_activation(context) -> None:
    assert context.composed.activation is ActivationMode.MANUAL


@then("only repository flavors remain eligible for selection")
def only_repository(context) -> None:
    assert support.bodies(context.composed) == ["repository one"]


@when("ZPP composes that source contribution")
def compose_contribution(context) -> None:
    decoded = support.decode(context.values, kind=context.kind)
    try:
        support.compose(decoded)
    except Exception as error:
        context.error = error
    else:
        context.error = None


@then("the contribution is rejected as valid only for repository sources")
def contribution_rejected(context) -> None:
    assert context.error is not None, "contribution was accepted"
    assert type(context.error).__name__ == "CompositionError"
    assert "repository-overwrite" in str(context.error)
