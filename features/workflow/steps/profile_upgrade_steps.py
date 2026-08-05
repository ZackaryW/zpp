from __future__ import annotations

import json

from behave import given, then, when

from features.support import zpp_support as support


def _default_root(context):
    return context.home / ".zpp" / "profiles" / "default"


def _assert_recorded_entries(context) -> None:
    after = support.snapshot(_default_root(context))
    for path, value in context.default_profile_recorded.items():
        assert after[path] == value, path


@given("the valid persistent default profile is missing newly packaged standard entries")
def step_default_missing_new_entries(context):
    support.initialize(context)
    root = _default_root(context)
    for name in (
        "bdd-structure-python",
        "bdd-structure-ts",
        "bdd-structure-flutter",
    ):
        (root / "traits" / f"{name}.md").unlink()


@given("its existing authored files, triggers, configuration, and custom traits are recorded")
def step_record_existing_default(context):
    root = _default_root(context)
    custom = root / "traits" / "custom.md"
    custom.write_text(
        "---\nname: custom\ndescription: custom guidance\norder: null\n"
        "config: {}\nskill_lookup: []\n---\ncustom body\n",
        encoding="utf-8",
    )
    context.default_profile_recorded = support.snapshot(root)


@then("only the missing packaged standard entries are added to the persistent default profile")
def step_missing_default_entries_added(context):
    root = _default_root(context)
    assert all(
        (root / "traits" / f"{name}.md").is_file()
        for name in (
            "bdd-structure-python",
            "bdd-structure-ts",
            "bdd-structure-flutter",
        )
    )


@then("every recorded authored profile entry is unchanged")
def step_recorded_default_unchanged(context):
    _assert_recorded_entries(context)


@given("the persistent default profile already contains every packaged standard entry")
def step_complete_default_profile(context):
    support.initialize(context)
    context.complete_default_before = support.snapshot(_default_root(context))


@then("the persistent default profile is byte-for-byte unchanged")
def step_default_byte_unchanged(context):
    expected = getattr(
        context,
        "default_before_local_operation",
        getattr(context, "complete_default_before", None),
    )
    assert expected is not None
    assert support.snapshot(_default_root(context)) == expected


@given("the persistent default profile is malformed")
def step_malformed_default(context):
    support.initialize(context)
    root = _default_root(context)
    (root / "config.json").write_text("malformed\n", encoding="utf-8")
    context.malformed_default_before = support.snapshot(root)


@when("the user runs zpp workflow install with agent Pi")
def step_install_pi_global(context):
    support.invoke(context, ["workflow", "install", "--agent", "pi"])


@then("the malformed persistent default profile is unchanged")
def step_malformed_default_unchanged(context):
    assert support.snapshot(_default_root(context)) == context.malformed_default_before


@given("the valid persistent default profile is missing one packaged BDD-structure trait")
def step_default_missing_one_bdd_trait(context):
    support.initialize(context)
    root = _default_root(context)
    (root / "traits" / "bdd-structure-python.md").unlink()


@given("a same-name packaged trait and existing trigger have user-authored content")
def step_user_owned_default_conflicts(context):
    root = _default_root(context)
    automatic = root / "traits" / "automatic-workflow.md"
    automatic.write_text(
        automatic.read_text(encoding="utf-8") + "\nUser-owned marker.\n",
        encoding="utf-8",
    )
    triggers = json.loads((root / "trait.json").read_text(encoding="utf-8"))
    triggers[0]["which"] = "user-owned-tool"
    (root / "trait.json").write_text(
        json.dumps(triggers, indent=2) + "\n", encoding="utf-8"
    )
    context.default_profile_recorded = support.snapshot(root)


@then("only the absent packaged trait is added to the persistent default profile")
def step_only_absent_trait_added(context):
    assert (_default_root(context) / "traits" / "bdd-structure-python.md").is_file()


@then("the same-name user file, existing trigger, configuration, and custom traits are unchanged")
def step_user_default_values_preserved(context):
    _assert_recorded_entries(context)
    context.default_before_local_operation = support.snapshot(_default_root(context))


@given("the managed workflow bundle is installed")
def step_managed_workflow_installed(context):
    support.initialize(context)
    support.invoke(context, ["workflow", "install", "--agent", "codex"])
    assert context.result.exit_code == 0, context.result.output


@when("the user explicitly invokes zpp-configure-behavior for a repository")
def step_invoke_behavior_skill(context):
    context.behavior_skill = (
        support.workflow_skill_root(context, "codex", scope="global")
        / "zpp-configure-behavior"
        / "SKILL.md"
    ).read_text(encoding="utf-8")


@then("the skill inspects the established verification structure and initializes zpp.behave.yaml through ZPP")
def step_behavior_skill_inspects(context):
    assert "inspect its established test runners" in context.behavior_skill
    assert "zpp behave init" in context.behavior_skill


@then("it proposes only declarative target and impact relationships")
def step_behavior_skill_declarative(context):
    assert "closed target sets" in context.behavior_skill
    assert "repository-relative impact" in context.behavior_skill


@then("it validates the mapping and runs its configured complete audit through ZPP")
def step_behavior_skill_validates(context):
    assert "zpp behave init" in context.behavior_skill
    assert "audit command with `--all`" in context.behavior_skill


@then("it does not supply runtime executable text, manage Nx plugins, or own filtering and execution")
def step_behavior_skill_authority(context):
    source = " ".join(context.behavior_skill.split())
    assert "Never obtain runtime executable text" in source
    assert "never install" in source
    assert "execution in ZPP core" in source
