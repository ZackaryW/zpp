import json

from behave import given, then

from environment import make_claude_plugin
from trait_steps import run_cli


@given('a claude plugin "{plugin}" shipping trait "{name}" with content "{content}"')
def step_claude_plugin_trait(context, plugin, name, content):
    make_claude_plugin(context, plugin, traits={name: content})


@given('a claude plugin "{plugin}" shipping only a skill')
def step_claude_plugin_skill_only(context, plugin):
    make_claude_plugin(context, plugin, skill=True)


@given('a claude plugin "{plugin}" shipping trait "{name}" and also skills and a manifest')
def step_claude_plugin_mixed(context, plugin, name):
    make_claude_plugin(context, plugin, traits={name: "GOOD RULE"}, skill=True, manifest=True)


@given('a claude plugins override directory holding plugin "{plugin}" with trait "{name}"')
def step_claude_override(context, plugin, name):
    override = context.tmp / "override-claude"
    make_claude_plugin(context, plugin, traits={name: "OVERRIDE RULE"}, base=override)
    repo = context.tmp / "repo"
    repo.mkdir(exist_ok=True)
    (repo / "zpp.toml").write_text(f'[traits.plugins]\nclaude = "{override}"\n')
    context.repo = repo


def _current_rows(context) -> list[dict]:
    """The rows the scenario's own command already produced (tool-aware)."""
    return json.loads(context.result.output)


@then('the listing includes "{name}" with source "{source}"')
def step_listing_includes(context, name, source):
    rows = [r for r in _current_rows(context)
            if r["name"] == name and not r.get("shadowed")]
    assert rows and rows[0]["source"] == source, _current_rows(context)


@then('no trait named "{name}" is listed')
def step_no_trait(context, name):
    names = {r["name"] for r in _current_rows(context)}
    assert name not in names, names


@then('the plugin trait "{name}" reports provenance tool "{tool}" plugin "{plugin}"')
def step_provenance(context, name, tool, plugin):
    rows = [r for r in _current_rows(context) if r["name"] == name]
    assert rows and rows[0].get("tool") == tool and rows[0].get("plugin") == plugin, rows


@then('the plugin copy of "{name}" is listed as shadowed under tool "{tool}"')
def step_plugin_shadowed(context, name, tool):
    run_cli(context, ["trait", "list", "--tool", tool, "--json"])
    rows = [r for r in json.loads(context.result.output)
            if r["name"] == name and r["source"] == "plugin"]
    assert rows and rows[0]["shadowed"], rows
