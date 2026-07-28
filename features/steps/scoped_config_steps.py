from behave import given, then, when

from zpp.core import governance


@given("a self-governed monorepo with Rust policy at its root")
def step_root_policy(context):
    context.repo = context.tmp / "monorepo"
    (context.repo / "openspec").mkdir(parents=True)
    (context.repo / "zpp.toml").write_text(
        '[tdd]\nstack = "rust"\n[bdd]\nstack = "rust"\n'
    )


@given('the monorepo has Python policy under "{relative}"')
def step_python_policy(context, relative):
    scope = context.repo / relative
    scope.mkdir(parents=True)
    (scope / "zpp.toml").write_text(
        '[tdd]\nstack = "python"\n[bdd]\nstack = "python"\n'
    )
    (scope / "src").mkdir()


@when('I resolve config for the root, the Python subtree, and sibling "{sibling}"')
def step_resolve_three_targets(context, sibling):
    sibling_path = context.repo / sibling
    sibling_path.mkdir(parents=True)
    context.root_config = governance.resolve_config(context.repo)
    context.python_config = governance.resolve_config(context.repo / "sdk/python/src")
    context.sibling_config = governance.resolve_config(sibling_path)


@then("only the Python subtree resolves the Python BDD and TDD stacks")
def step_assert_scoped_stacks(context):
    assert context.root_config["effective"]["tdd"]["stack"] == "rust"
    assert context.root_config["effective"]["bdd"]["stack"] == "rust"
    assert context.sibling_config["effective"]["tdd"]["stack"] == "rust"
    assert context.sibling_config["effective"]["bdd"]["stack"] == "rust"
    assert context.python_config["effective"]["tdd"]["stack"] == "python"
    assert context.python_config["effective"]["bdd"]["stack"] == "python"


@given('"{relative}" declares nested governance and profiles')
def step_nested_authority(context, relative):
    config = context.repo / relative
    config.parent.mkdir(parents=True)
    config.write_text(
        '[governance]\nstore = "other"\n'
        '[profiles.default.tdd]\nstack = "python"\n'
        '[tdd]\nstack = "python"\n'
    )
    context.scoped_config = config.resolve()


@when('I resolve config for "{relative}"')
def step_resolve_scoped_config(context, relative):
    try:
        governance.resolve_config(context.repo / relative)
    except governance.ScopedConfigError as exc:
        context.config_error = exc
    else:
        context.config_error = None


@then("scoped resolution fails naming the file and both authority sections")
def step_assert_authority_failure(context):
    assert context.config_error is not None
    message = str(context.config_error)
    assert str(context.scoped_config) in message
    assert "[governance]" in message
    assert "[profiles]" in message


@then("governance resolution still reports the monorepo root")
def step_assert_governance_unchanged(context):
    resolved = governance.resolve(context.repo / "sdk/python")
    assert resolved["mode"] == "self-governed"
    assert resolved["root"] == str(context.repo.resolve())
