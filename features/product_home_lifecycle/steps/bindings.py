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


@given("one owned workflow skill has drifted from its packaged asset")
def drift_workflow_skill(context) -> None:
    document = context.env.workflow_skill_document()
    context.packaged_text = document.read_text(encoding="utf-8")
    document.write_text("drifted", encoding="utf-8")


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


@then("it does not initialize the openlease child")
def openlease_absent(context) -> None:
    assert not (context.env.zpp_home / "openlease").exists()


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


@then("every packaged and generated integration entry is installed")
def every_entry_installed(context) -> None:
    statuses = [record["status"] for record in context.records]
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


@then("synchronization reports the modified entry and leaves its content unchanged")
def sync_reports_conflict(context) -> None:
    conflicted = [
        record for record in context.records if record["decision"] == "conflict"
    ]
    assert [record["asset"] for record in conflicted] == ["skill"], context.records
    unchanged = context.env.workflow_skill_document().read_text(encoding="utf-8")
    assert unchanged == "drifted"


@then("synchronization repairs the modified entry and restores its packaged content")
def sync_repairs_conflict(context) -> None:
    repaired = [
        record for record in context.records if record["decision"] == "reproject"
    ]
    assert [record["asset"] for record in repaired] == ["skill"], context.records
    restored = context.env.workflow_skill_document().read_text(encoding="utf-8")
    assert restored == context.packaged_text


@then("synchronization reprojects every owned entry despite no observed drift")
def sync_forced(context) -> None:
    decisions = [record["decision"] for record in context.records]
    assert len(decisions) == support.expected_entry_count(), decisions
    assert set(decisions) == {"project"}, decisions


@then("synchronization reports the agent as uninitialized and projects nothing")
def sync_uninitialized(context) -> None:
    assert [record["status"] for record in context.records] == ["uninitialized"]
    assert context.records[0]["decision"] == "skip"
