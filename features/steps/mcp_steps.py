from behave import given, then, when

from zpp.core import adapter
from zpp_mcp import prompt


@given('a self-governed repo applying trait "{trait}"')
def step_self_governed(context, trait):
    """A local openspec/ root (rule 1) whose zpp.toml publishes a default
    profile applying the trait - no store registry needed, no warnings."""
    repo = context.tmp / "repo"
    (repo / "openspec").mkdir(parents=True)
    (repo / "zpp.toml").write_text(
        f'[profiles.default.traits]\napply = ["{trait}"]\n')
    context.target = repo


@given('an ungoverned directory with a reachable store registry')
def step_ungoverned_clean(context):
    """Plain dir; patch the registry read to succeed (empty) so the only
    reason for a block - a degradation warning - is absent."""
    adapter.store_list = lambda: {}
    plain = context.tmp / "plain"
    plain.mkdir()
    context.target = plain


@given('a repo bound to a store with the store registry unavailable')
def step_degraded(context):
    """Committed binding (rule 2) while the registry read raises, so resolve
    classifies but records a warning - the mount's degraded path."""
    def boom():
        raise adapter.OpenspecError("openspec CLI unavailable")
    adapter.store_list = boom
    repo = context.tmp / "repo"
    repo.mkdir()
    (repo / "zpp.toml").write_text('[governance]\nstore = "ghost"\n')
    context.target = repo


@when('I request the zpp-governance prompt for it')
def step_request_prompt(context):
    context.block = prompt.governance_block(str(context.target))


@then('the prompt output opens a "{tag}" block')
def step_opens_block(context, tag):
    assert context.block.startswith(f"<{tag}>"), context.block
    assert context.block.rstrip().endswith(f"</{tag}>"), context.block


@then('the prompt output contains "{text}"')
def step_contains(context, text):
    assert text in context.block, context.block


@then('the prompt output contains the trait "{name}"')
def step_contains_trait(context, name):
    assert f"trait: {name}" in context.block, context.block


@then('the prompt output has no doctor report')
def step_no_doctor(context):
    assert "doctor report" not in context.block, context.block


@then('the prompt output is empty')
def step_empty(context):
    assert context.block == "", repr(context.block)
