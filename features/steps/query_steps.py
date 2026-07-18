import json

from behave import given, then


@given('a self-governed repo whose store tier applies "{store_trait}" and whose repo tier applies "{repo_trait}"')
def step_self_governed_tiers(context, store_trait, repo_trait):
    repo = context.tmp / "selfgov"
    (repo / "openspec").mkdir(parents=True, exist_ok=True)
    # one file: the store tier is the published default PROFILE, the repo tier
    # is the top-level config (no zpp.default.toml - default is a profile)
    (repo / "zpp.toml").write_text(
        f'[traits]\napply = ["{repo_trait}"]\n'
        f'[profiles.default.traits]\napply = ["{store_trait}"]\n'
    )
    context.repo = repo


@then('the error output contains "{text}"')
def step_error_contains(context, text):
    err = getattr(context.result, "stderr", "") or ""
    combined = context.result.output + err
    assert text in combined, combined


@then('trait "{first}" appears before trait "{second}" in the output')
def step_order(context, first, second):
    out = context.result.output
    marker_first = f"<!-- trait: {first}"
    marker_second = f"<!-- trait: {second}"
    assert marker_first in out and marker_second in out, out
    assert out.index(marker_first) < out.index(marker_second), out


@then('the effective JSON attributes "{first}" to tier "{first_tier}" and "{second}" to tier "{second_tier}"')
def step_json_tiers(context, first, first_tier, second, second_tier):
    payload = json.loads(context.result.output)
    tiers = {item["name"]: item["tier"] for item in payload["applied"]}
    assert tiers.get(first) == first_tier, tiers
    assert tiers.get(second) == second_tier, tiers
