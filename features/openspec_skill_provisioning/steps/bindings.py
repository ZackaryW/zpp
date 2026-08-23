from __future__ import annotations

import support
from behave import given, then, when

from zpp.cli import app


@given("the packaged companion inventory is loaded")
def companion_inventory(context) -> None:
    context.companions = support.companion_names()


@given("the grouped workflow lifecycle help is available")
def workflow_help(context) -> None:
    from typer.testing import CliRunner

    runner = CliRunner()
    context.help_outputs = {
        operation: runner.invoke(app, ["workflow", operation, "--help"])
        for operation in ("install", "update", "remove")
    }


@given("a disposable user home")
def disposable_home(context) -> None:
    context.home = support.Home()


@given("the codex agent is initialized")
def initialized(context) -> None:
    result = context.home.run("init", "--agent", "codex")
    assert result.exit_code == 0, result.output


@given("a generated OpenSpec skill has been modified locally")
def modify_generated(context) -> None:
    document = context.home.generated_document()
    context.packaged_text = document.read_text(encoding="utf-8")
    document.write_text("modified", encoding="utf-8")


@given("an unmanaged workflow skill occupies the codex surface")
def unmanaged_skill(context) -> None:
    path = context.home.skill_path("zpp-workflow") / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("unmanaged", encoding="utf-8")
    context.unmanaged = path


@when("a user initializes the codex agent")
def initialize(context) -> None:
    context.result = context.home.run("init", "--agent", "codex")
    assert context.result.exit_code == 0, context.result.output


@when("a user synchronizes the codex agent")
def synchronize(context) -> None:
    context.records = context.home.run_json("sync", "--agent", "codex", "--json")


@when("a user synchronizes the codex agent with force")
def synchronize_forced(context) -> None:
    context.records = context.home.run_json(
        "sync", "--agent", "codex", "--force", "--json"
    )


@when("a user confirms a complete reset")
def confirm_reset(context) -> None:
    context.result = context.home.run(
        "--path", str(context.home.product_home), "reset", "--yes"
    )
    assert context.result.exit_code == 0, context.result.output


@then("it contains the vendored zmem authoring and query skills")
def contains_zmem(context) -> None:
    assert {"zmem-author-commits", "zmem-query-memory"} <= set(context.companions)


@then("it contains no workspace-management skill")
def excludes_workspace_management(context) -> None:
    assert "zpp-workspace-management" not in context.companions


@then("it contains no withdrawn zmem extension skill")
def excludes_withdrawn(context) -> None:
    assert "zmem-design-extensions" not in context.companions


@then("no grouped workflow operation exposes an OpenSpec control")
def no_openspec_control(context) -> None:
    for operation, result in context.help_outputs.items():
        assert result.exit_code == 0, operation
        assert "openspec" not in result.stdout.casefold(), operation


@then("one lifecycle result is reported per projected asset")
def one_result_each(context) -> None:
    records = context.home.run_json("sync", "--agent", "codex", "--json")
    assert len(records) == support.expected_asset_count(), records


@then("every packaged companion skill is present on disk")
def companions_present(context) -> None:
    for name in support.companion_names():
        assert (context.home.skill_path(name) / "SKILL.md").is_file(), name


@then("each generated OpenSpec skill records ZPP as its generator")
def generator_recorded(context) -> None:
    assert context.home.provenance()["generator"] == "zpp"


@then("every projected asset reports current")
def all_current(context) -> None:
    decisions = {record["decision"] for record in context.records}
    assert decisions == {"current"}, context.records
    assert len(context.records) == support.expected_asset_count()


@then("the generated OpenSpec skill content is restored")
def generated_restored(context) -> None:
    restored = context.home.generated_document().read_text(encoding="utf-8")
    assert restored == context.packaged_text


@then("the generated OpenSpec skill is removed")
def generated_removed(context) -> None:
    assert not context.home.skill_path(support.GENERATED_SKILL).exists()


@then("managed Bundler state is replaced")
def state_replaced(context) -> None:
    assert (context.home.product_home / "bundler").is_dir()


@then("ZPP reports the agent as already initialized")
def already_initialized(context) -> None:
    assert "already initialized" in context.result.stdout


@then("forced synchronization preserves that unmanaged skill")
def unmanaged_preserved(context) -> None:
    records = context.home.run_json("sync", "--agent", "codex", "--force", "--json")
    decisions = {record["asset"]: record["decision"] for record in records}
    assert decisions["skill"] == "preserve", decisions
    assert context.unmanaged.read_text(encoding="utf-8") == "unmanaged"
