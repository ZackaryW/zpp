from __future__ import annotations

import support
from behave import given, then, when


@given("a committed repository")
def committed_repository(context) -> None:
    context.repository = support.Repository()


@given("a committed repository with a declared behavior mapping")
def declared_mapping(context) -> None:
    context.repository = support.Repository()
    initialized = context.repository.behave("init")
    assert initialized.exit_code == 0, initialized.output
    context.repository.declare_mapping()
    context.authored = (context.repository.root / "zpp.behave.yaml").read_text(
        encoding="utf-8"
    )


@given("a change under one declared target's paths")
def change_target(context) -> None:
    context.repository.change("src/core/module.py")


@when("the caller initializes behavior verification")
@when("the caller initializes behavior verification again")
def initialize_behavior(context) -> None:
    context.result = context.repository.behave("init")


@when("the caller runs the declared bdd command")
def run_bdd(context) -> None:
    context.result = context.repository.behave("bdd")


@when("the caller runs the declared bdd command for every target")
def run_complete(context) -> None:
    context.result = context.repository.behave("bdd", "--all")


@when("the caller runs the declared bdd command for one target twice")
def run_repeated_target(context) -> None:
    context.result = context.repository.behave(
        "bdd", "--target", "workflow", "--target", "workflow"
    )


@when("the caller runs the declared bdd command for the zpp-workflow gate")
def run_gate(context) -> None:
    context.result = context.repository.behave("bdd", "--gate", "zpp-workflow")


@when("the caller combines complete and explicit target selection")
def run_ambiguous(context) -> None:
    context.result = context.repository.behave("bdd", "--all", "--target", "core")


@then("a version-one behavior mapping exists")
def mapping_exists(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    mapping = context.repository.root / "zpp.behave.yaml"
    assert mapping.is_file()
    assert "version: 1" in mapping.read_text(encoding="utf-8")


@then("no session or lease state is created")
def no_lease_state(context) -> None:
    assert not context.repository.has_lease_state()


@then("the mapping is reported as validated")
def mapping_validated(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "Behavior mapping validated" in context.result.stdout


@then("the authored mapping content is unchanged")
def mapping_unchanged(context) -> None:
    current = (context.repository.root / "zpp.behave.yaml").read_text(encoding="utf-8")
    assert current == context.authored


@then("no targets are reported as affected")
def no_targets(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "No targets are affected" in context.result.stdout


@then("the provider receives only that target")
def provider_single_target(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout == "features/core\n"


@then("the provider receives every declared target")
def provider_every_target(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout == "features/core|features/workflow\n"


@then("the provider receives that target once")
def provider_deduplicated(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout == "features/workflow\n"


@then("the provider receives the gate's declared target set")
def provider_gate_targets(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout == "features/core|features/workflow\n"


@then("the invocation is rejected as mutually exclusive")
def rejected_ambiguous(context) -> None:
    assert context.result.exit_code == 2
    assert "mutually exclusive" in context.result.output
