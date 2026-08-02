from __future__ import annotations

import json
from pathlib import Path

from behave import given, then, when

from zpp.utils.plugin_discovery import ActivePlugin

from zpp_steps import (
    git_init,
    initialize,
    invoke,
    parse_documents,
    snapshot,
    write_layer,
    write_trait,
)


def _plugin(
    context,
    agent: str,
    identity: str,
    *,
    version: str = "1.0.0",
    traits: dict[str, str] | None = None,
    triggers: list[dict] | None = None,
) -> ActivePlugin:
    root = context.sandbox / "plugins" / agent / identity / version
    (root / "traits").mkdir(parents=True, exist_ok=True)
    for name, body in (traits or {f"{agent}-active": f"{agent} active plugin\n"}).items():
        write_trait(root, name, body=body)
    (root / "trait.json").write_text(
        json.dumps(
            triggers
            if triggers is not None
            else [{"trait": next(iter(traits or {f"{agent}-active": ""}))}],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return ActivePlugin(agent, identity, version, root.resolve())


def _set_plugins(context, agent: str, plugins: tuple[ActivePlugin, ...]) -> None:
    if not hasattr(context, "active_plugins_by_agent"):
        context.active_plugins_by_agent = {}
    context.active_plugins_by_agent[agent] = plugins


def _names(context) -> list[str]:
    return [metadata["name"] for metadata, _ in parse_documents(context.result.stdout)]


@given("{agent} reports one active plugin with a valid trait source")
def active_plugin(context, agent):
    initialize(context)
    context.agent = agent
    plugin = _plugin(context, agent, f"active-{agent}")
    _set_plugins(context, agent, (plugin,))
    global_root = context.home / ".zpp" / "global"
    write_trait(global_root, "global-trait", body="global layer\n")
    (global_root / "trait.json").write_text(
        '[{"trait":"global-trait"}]\n', encoding="utf-8"
    )


@given("the other supported agents report different active plugins")
def other_agent_plugins(context):
    for agent in {"codex", "claude", "pi"} - {context.agent}:
        _set_plugins(context, agent, (_plugin(context, agent, f"other-{agent}"),))


@given("{agent} also contains available, disabled, orphaned, and stale plugin material")
def inactive_material(context, agent):
    for name in ("available", "disabled", "orphaned", "stale"):
        _plugin(context, agent, f"{name}-{agent}")


@when("the user runs zpp resolve --agent {agent} for the target")
def resolve_for_agent(context, agent):
    invoke(context, ["resolve", str(context.project), "--agent", agent])


@then("only {agent}'s active plugin trait source participates before global")
def only_active_before_global(context, agent):
    assert context.result.exit_code == 0, context.result.output
    assert _names(context) == [f"{agent}-active", "global-trait"]


@then("no other agent or inactive plugin material participates")
def no_inactive_material(context):
    output = context.result.stdout
    assert all(term not in output for term in ("other-", "available-", "disabled-", "orphaned-", "stale-"))


@given("every supported agent reports an active plugin trait source")
def every_agent_plugin(context):
    initialize(context)
    for agent in ("codex", "claude", "pi"):
        _set_plugins(context, agent, (_plugin(context, agent, f"active-{agent}"),))
    git_init(context.project)
    invoke(context, ["profile", "create", "work"])
    context.env["ZPP_PROFILE"] = "work"
    invoke(context, ["profile", "saved", "create", "bound", str(context.project)])
    roots = (
        context.home / ".zpp" / "global",
        context.home / ".zpp" / "profiles" / "work",
        context.home / ".zpp" / "saved" / "bound",
        context.project / ".zpp",
    )
    write_layer(roots[-1])
    for root, name in zip(roots, ("global", "profile", "saved", "repository"), strict=True):
        write_trait(root, name, body=f"{name} layer\n")
        (root / "trait.json").write_text(
            json.dumps([{"trait": name}]) + "\n", encoding="utf-8"
        )
    context.results.clear()


@when("the user runs zpp resolve for the target without --agent")
def direct_resolve(context):
    invoke(context, ["resolve", str(context.project)])


@then("no editor plugin trait source participates")
def no_editor_plugins(context):
    assert context.result.exit_code == 0, context.result.output
    assert "active-" not in context.result.stdout


@then("global, selected profile, saved, and repository layers retain their established order")
def user_layer_order(context):
    assert _names(context) == ["global", "profile", "saved", "repository"]


@given("an active plugin root contains trait.json and valid Markdown trait definitions")
def composable_plugin(context):
    initialize(context)
    context.agent = "codex"
    context.composed_plugin = _plugin(
        context,
        "codex",
        "composable",
        traits={
            "plugin-auto": "plugin auto body\n",
            "plugin-manual": "plugin manual body\n",
            "plugin-cleared": "plugin cleared body\n",
        },
        triggers=[
            {"trait": "plugin-auto", "workspace_contain": ["marker.txt"]},
            {"trait": "plugin-cleared"},
        ],
    )
    _set_plugins(context, "codex", (context.composed_plugin,))
    (context.project / "marker.txt").write_text("marker\n", encoding="utf-8")
    context.plugin_before = snapshot(context.composed_plugin.root)
    context.default_before = snapshot(context.home / ".zpp" / "profiles" / "default")


@given("its trait.json conditionally activates one definition")
def conditional_plugin_trigger(context):
    rules = json.loads((context.composed_plugin.root / "trait.json").read_text(encoding="utf-8"))
    assert rules[0] == {"trait": "plugin-auto", "workspace_contain": ["marker.txt"]}


@given("another plugin definition is omitted from its trigger list")
def omitted_plugin_definition(context):
    rules = json.loads((context.composed_plugin.root / "trait.json").read_text(encoding="utf-8"))
    assert "plugin-manual" not in {rule["trait"] for rule in rules}


@given("a later repository layer activates and configures the omitted definition")
def local_activates_plugin_definition(context):
    git_init(context.project)
    root = context.project / ".zpp"
    write_layer(
        root,
        triggers=[{"trait": "plugin-auto"}, {"trait": "plugin-manual"}],
        config={
            "trait_overwrites": True,
            "traitsConfig": {"plugin-manual": {"useThis": False}},
        },
    )
    write_trait(root, "plugin-auto", body="repository replacement\n")


@when("the user runs zpp resolve with that plugin's agent identity")
def resolve_composed_plugin(context):
    invoke(context, ["resolve", str(context.project), "--agent", context.agent])


@then("the plugin trigger participates before global")
def plugin_controls_first(context):
    assert context.result.exit_code == 0, context.result.output
    assert "plugin-cleared" not in _names(context)


@then("the repository activation uses the discovered omitted definition")
def repository_uses_omitted(context):
    documents = {metadata["name"]: (metadata, body) for metadata, body in parse_documents(context.result.stdout)}
    assert documents["plugin-manual"][1] == "plugin manual body\n"


@then("later replacement, configuration, and trigger-overwrite behavior remains authoritative")
def later_user_controls_win(context):
    documents = {metadata["name"]: (metadata, body) for metadata, body in parse_documents(context.result.stdout)}
    assert documents["plugin-auto"][1] == "repository replacement\n"
    assert documents["plugin-manual"][0]["config"]["useThis"] is False
    assert "plugin-cleared" not in documents


@then("the plugin source is byte-for-byte unchanged")
def plugin_unchanged(context):
    assert snapshot(context.composed_plugin.root) == context.plugin_before


@then("no plugin trait is copied into a user-owned profile")
def no_profile_copy(context):
    assert snapshot(context.home / ".zpp" / "profiles" / "default") == context.default_before


@given("one active plugin source has already produced independently cached traits")
def cached_plugin(context):
    initialize(context)
    context.agent = "codex"
    context.old_plugin = _plugin(
        context, "codex", "replaceable", version="1.0.0",
        traits={"changing": "old active body\n"},
    )
    _set_plugins(context, "codex", (context.old_plugin,))
    invoke(context, ["resolve", str(context.project), "--agent", "codex"])
    assert "old active body" in context.result.stdout
    context.old_cache = snapshot(context.home / ".zpp" / "cached" / "plugins")


@when("the invoking agent replaces that plugin with a new active version and root")
def replace_plugin(context):
    context.new_plugin = _plugin(
        context, "codex", "replaceable", version="2.0.0",
        traits={"changing": "new active body\n"},
    )
    _set_plugins(context, "codex", (context.new_plugin,))


@then("subsequent resolution uses only the new active source")
def resolve_new_plugin(context):
    invoke(context, ["resolve", str(context.project), "--agent", "codex"])
    assert context.result.exit_code == 0, context.result.output
    assert "new active body" in context.result.stdout
    assert "old active body" not in context.result.stdout


@when("the invoking agent disables or uninstalls the plugin")
def remove_plugin(context):
    _set_plugins(context, "codex", ())


@then("subsequent resolution excludes that source even while former files or cache state remain")
def resolve_without_plugin(context):
    invoke(context, ["resolve", str(context.project), "--agent", "codex"])
    assert context.result.exit_code == 0 and context.result.stdout == ""
    assert context.old_plugin.root.exists() and context.new_plugin.root.exists()
    assert snapshot(context.home / ".zpp" / "cached" / "plugins")


@given("active plugin sources are presented in arbitrary discovery order")
def arbitrary_plugin_order(context):
    initialize(context)
    context.agent = "codex"
    shared = {"shared": "shared identical body\n"}
    plugin_b = _plugin(
        context, "codex", "b-plugin",
        traits={**shared, "beta": "beta body\n"},
        triggers=[{"trait": "shared"}, {"trait": "beta"}],
    )
    plugin_a = _plugin(
        context, "codex", "a-plugin",
        traits={"alpha": "alpha body\n", **shared},
        triggers=[{"trait": "alpha"}, {"trait": "shared"}],
    )
    _set_plugins(context, "codex", (plugin_b, plugin_a))
    context.conflict_plugins = (plugin_a, plugin_b)


@when("ZPP composes their declared trait sources")
def compose_plugin_sources(context):
    invoke(context, ["resolve", str(context.project), "--agent", "codex"])


@then("sources are ordered by stable plugin identity")
def stable_plugin_order(context):
    assert context.result.exit_code == 0, context.result.output
    assert _names(context) == ["alpha", "shared", "beta"]


@then("byte-identical definitions with the same trait name participate once")
def identical_definition_once(context):
    assert _names(context).count("shared") == 1


@then("their valid triggers remain eligible through ordinary activation")
def plugin_triggers_eligible(context):
    assert set(_names(context)) == {"alpha", "shared", "beta"}


@then("different content for the same trait name fails complete resolution")
def make_plugin_conflict(context):
    write_trait(
        context.conflict_plugins[1].root,
        "shared",
        body="different shared body\n",
    )
    invoke(context, ["resolve", str(context.project), "--agent", "codex"])
    assert context.result.exit_code == 1


@then("the diagnostic identifies every conflicting plugin source")
def conflict_diagnostic_sources(context):
    assert all(plugin.identity in context.result.stderr for plugin in context.conflict_plugins)


@then("stdout contains no stale, partial, or fallback trait context")
def conflict_has_no_stdout(context):
    assert context.result.stdout == ""


@given("an active plugin declares trait.json and traits but one authored document is invalid")
def malformed_plugin(context):
    initialize(context)
    context.agent = "codex"
    plugin = _plugin(context, "codex", "malformed")
    (plugin.root / "traits" / "codex-active.md").write_text("not frontmatter\n", encoding="utf-8")
    _set_plugins(context, "codex", (plugin,))
    context.malformed_plugin = plugin


@then("resolution fails with a source-oriented diagnostic")
def malformed_source_diagnostic(context):
    assert context.result.exit_code == 1
    assert "malformed" in context.result.stderr
    assert "codex-active.md" in context.result.stderr


@then("no stale or partial trait context is returned")
def no_partial_plugin_context(context):
    assert context.result.stdout == ""
