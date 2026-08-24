from __future__ import annotations

from unittest.mock import patch

import support
from behave import given, then, when


@given("a temporary user environment")
def temporary_environment(context) -> None:
    context.env = support.Environment()


@given("the codex agent is already initialized")
def already_initialized(context) -> None:
    result = context.env.run("init", "--agent", "codex")
    assert result.exit_code == 0, result.output


@given("the codex agent carries current skills and intact former hook ownership")
def former_user_hook(context) -> None:
    context.env.replace_current_hook_with_former()


@given("one owned workflow skill has drifted from its packaged asset")
def drift_workflow_skill(context) -> None:
    document = context.env.workflow_skill_document()
    context.packaged_text = document.read_text(encoding="utf-8")
    document.write_text("drifted", encoding="utf-8")


@given("an obsolete workflow skill is owned by Agent Router")
def owned_obsolete_workflow(context) -> None:
    context.obsolete = context.env.install_owned_obsolete("zpp-workflow")


@given("only an owned obsolete workflow skill is installed")
def old_only_workflow(context) -> None:
    context.obsolete = context.env.install_owned_obsolete("zpp-workflow")


@given("an unowned obsolete OpenSpec identity exists")
def unowned_obsolete_openspec(context) -> None:
    context.unowned = context.env.create_unowned_obsolete("openspec-apply-change")


@when("a user opens an absent selected ZPP home")
def open_home(context) -> None:
    with patch("zpp.cli.open.open_directory") as opener:
        context.result = context.env.run("--path", str(context.env.zpp_home), "open")
    context.opener = opener


@when("a user runs reset without confirmation")
def reset_unconfirmed(context) -> None:
    context.result = context.env.run("--path", str(context.env.zpp_home), "reset")


@when("a user runs confirmed reset with and without JSON output")
def reset_confirmed(context) -> None:
    context.result = context.env.run(
        "--path", str(context.env.zpp_home), "reset", "--yes"
    )
    context.json_result = context.env.run(
        "--path", str(context.env.zpp_home), "reset", "--yes", "--json"
    )


@when("a user initializes the codex agent")
@when("a user initializes the codex agent again")
def initialize_codex(context) -> None:
    context.records = context.env.run_json("init", "--agent", "codex", "--json")


@when("a user synchronizes the codex agent")
def synchronize_codex(context) -> None:
    context.records = context.env.run_json("sync", "--agent", "codex", "--json")


@when("a user synchronizes the codex agent with force")
def synchronize_forced(context) -> None:
    context.records = context.env.run_json(
        "sync", "--agent", "codex", "--force", "--json"
    )


@then("ZPP creates and natively opens that exact home")
def home_opened(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    context.opener.assert_called_once_with(context.env.zpp_home)
    assert context.env.zpp_home.is_dir()


@then("it does not initialize the bundler child")
def bundler_absent(context) -> None:
    assert not (context.env.zpp_home / "bundler").exists()


@then("ZPP rejects the command and names the required confirmation")
def reset_rejected(context) -> None:
    assert context.result.exit_code == 2
    assert "--yes" in context.result.output


@then("the default reset result is one concise line")
def reset_concise(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert len(context.result.stdout.splitlines()) == 1
    assert context.result.stdout.startswith("Reset complete:")


@then("the JSON reset result reports the replaced state")
def reset_json(context) -> None:
    import json

    assert context.json_result.exit_code == 0, context.json_result.output
    assert json.loads(context.json_result.stdout)["state"] == "replaced"


@then("every current packaged integration entry is installed")
def every_entry_installed(context) -> None:
    statuses = [
        record["status"]
        for record in context.records
        if not record.get("asset", "").startswith("obsolete-skill:")
        and record.get("asset") != "migration"
    ]
    assert len(statuses) == support.expected_entry_count(), statuses
    assert set(statuses) == {"installed"}, statuses


@then("ZPP reports it as already initialized and directs the caller to sync")
def rejected_as_initialized(context) -> None:
    assert [record["status"] for record in context.records] == ["already-initialized"]
    assert "zpp sync" in context.records[0]["action"]


@then("no integration entry is reprojected")
def nothing_reprojected(context) -> None:
    assert all(record["asset"] == "-" for record in context.records)


@then("synchronization reprojects nothing and reports every entry as current")
def sync_all_current(context) -> None:
    decisions = [record["decision"] for record in context.records]
    assert len(decisions) == support.expected_entry_count(), decisions
    assert set(decisions) == {"current"}, decisions


@then("current user hook ownership replaces the former identity")
def user_hook_migrated(context) -> None:
    assert context.env.hook_ownership_states() == ("current", "unmanaged")


@then("synchronization reports the modified entry and leaves its content unchanged")
def sync_reports_conflict(context) -> None:
    conflicted = [
        record for record in context.records if record["decision"] == "conflict"
    ]
    assert [record["asset"] for record in conflicted] == ["skill:zpp-auto"], (
        context.records
    )
    unchanged = context.env.workflow_skill_document().read_text(encoding="utf-8")
    assert unchanged == "drifted"


@then("synchronization repairs the modified entry and restores its packaged content")
def sync_repairs_conflict(context) -> None:
    repaired = [
        record for record in context.records if record["decision"] == "reproject"
    ]
    assert [record["asset"] for record in repaired] == ["skill:zpp-auto"], (
        context.records
    )
    restored = context.env.workflow_skill_document().read_text(encoding="utf-8")
    assert restored == context.packaged_text, (restored, context.packaged_text)


@then("synchronization reprojects every owned entry despite no observed drift")
def sync_forced(context) -> None:
    decisions = [record["decision"] for record in context.records]
    assert len(decisions) == support.expected_entry_count(), decisions
    assert set(decisions) == {"project"}, decisions


@then("synchronization reports the agent as uninitialized and projects nothing")
def sync_uninitialized(context) -> None:
    assert [record["status"] for record in context.records] == ["uninitialized"]
    assert context.records[0]["decision"] == "skip"


@then("synchronization removes the owned obsolete workflow skill")
def owned_obsolete_removed(context) -> None:
    matching = [
        record
        for record in context.records
        if record["asset"] == "obsolete-skill:zpp-workflow"
    ]
    assert len(matching) == 1, context.records
    assert matching[0]["decision"] == "remove"
    assert matching[0]["status"] == "removed"
    assert not context.obsolete.exists()


@then("the owned obsolete workflow skill is retired after current verification")
def old_only_obsolete_retired(context) -> None:
    matching = [
        record
        for record in context.records
        if record["asset"] == "obsolete-skill:zpp-workflow"
    ]
    assert len(matching) == 1, context.records
    assert matching[0]["decision"] == "remove"
    assert matching[0]["status"] == "removed"
    assert not context.obsolete.exists()


def _assert_complete_old_only_migration(context) -> None:
    migrations = [
        record for record in context.records if record.get("asset") == "migration"
    ]
    assert len(migrations) == 1, context.records
    assert migrations[0]["status"] == "complete"
    assert migrations[0]["origin"] == "old-only"
    assert len(migrations[0]["current"]) == support.expected_entry_count()
    assert migrations[0]["surviving_obsolete"] == []


@then("initialization identifies the old-only migration as complete")
def initialized_migration_identified(context) -> None:
    _assert_complete_old_only_migration(context)


@then("synchronization identifies the old-only migration as complete")
def synchronized_migration_identified(context) -> None:
    _assert_complete_old_only_migration(context)


@then("initialization reports an obsolete migration conflict")
def initialization_conflict(context) -> None:
    migrations = [
        record for record in context.records if record.get("asset") == "migration"
    ]
    assert len(migrations) == 1, context.records
    assert migrations[0]["status"] == "conflict"
    assert migrations[0]["origin"] == "obsolete-conflict"
    assert migrations[0]["current"] == []
    assert migrations[0]["surviving_obsolete"] == [
        "obsolete-skill:openspec-apply-change"
    ]


@then("no current packaged integration entry is projected")
def no_current_projection(context) -> None:
    assert not context.env.workflow_skill_document().exists()


@then("the current packaged inventory remains installed")
def current_inventory_installed(context) -> None:
    current = [record for record in context.records if record["decision"] == "current"]
    assert len(current) == support.expected_entry_count(), context.records


@then("synchronization reports the obsolete identity as preserved")
def obsolete_preserved(context) -> None:
    matching = [
        record
        for record in context.records
        if record["asset"] == "obsolete-skill:openspec-apply-change"
    ]
    assert len(matching) == 1, context.records
    assert matching[0]["decision"] == "preserve"
    assert matching[0]["status"] == "unmanaged"


@then("the unowned obsolete identity remains unchanged")
def unowned_obsolete_unchanged(context) -> None:
    assert context.unowned.read_text(encoding="utf-8") == "unowned obsolete"


@given("a disposable Git worktree and an absent ZPP home")
def worktree_and_absent_home(context) -> None:
    context.worktree = context.env.configure_store()
    assert not context.env.zpp_home.exists()


@when("ZPP automatically acquires a store change bundle")
def acquire_store_bundle(context) -> None:
    context.result = context.env.run(
        "--path",
        str(context.env.zpp_home),
        "lease",
        "acquire",
        "--owner",
        "workflow:home-test",
        "--member",
        f"{support.STORE_UUID}:home-change",
    )
    assert context.result.exit_code == 0, context.result.output


@then("the selected home and its bundler child exist")
def home_and_state_exist(context) -> None:
    assert context.env.zpp_home.is_dir()
    assert (context.env.zpp_home / "bundler" / "state.json").is_file()


@then("no legacy OpenLease state is created or changed")
def legacy_state_absent(context) -> None:
    assert not (context.env.zpp_home / "openlease").exists()
