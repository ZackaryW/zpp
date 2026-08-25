from __future__ import annotations

import copy

import support
from agent_router import Agent
from behave import given, then, when


def _environment(context) -> support.Environment:
    environment = support.Environment()
    context.environment = environment
    return environment


def _start(context, workflow: str = "zpp-new-feature") -> dict:
    result = context.environment.start(workflow)
    context.result = result
    context.payload = support.result_json(result)
    return context.payload


@given("an isolated repository with no workflow reminder")
def isolated_repository(context) -> None:
    _environment(context)


@given("the packaged workflow and component contracts")
def packaged_contracts(context) -> None:
    _environment(context)


@given("a workflow contract containing an unknown field")
def invalid_contract(context) -> None:
    _environment(context)
    context.contract_payload = {
        "version": 1,
        "name": "zpp-new-feature",
        "mode": "reminder",
        "stages": [{"id": "clarify", "component": "zpps-clarify"}],
        "unknown": True,
    }


@given("an active zpp-new-feature reminder")
def active_new_feature(context) -> None:
    _environment(context)
    _start(context)


@given("an active reminder whose clarify stage is completed")
def completed_clarify(context) -> None:
    _environment(context)
    _start(context)
    context.result = context.environment.run(
        "record",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-clarify",
        "--result",
        "completed",
    )
    support.result_json(context.result)


@given("an active reminder with an inserted custom explore stage")
def inserted_explore_stage(context) -> None:
    active_new_feature(context)
    context.result = context.environment.run(
        "stage",
        "insert",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--id",
        "custom-explore",
        "--component",
        "zpps-explore",
        "--before",
        "clarify",
    )
    support.result_json(context.result)


@given("an adapter with a confirmed prompt-submission context event")
def supported_prompt_adapter(context) -> None:
    _environment(context)
    context.agent = Agent.CLAUDE


@given("an adapter without a confirmed prompt-submission context event")
def unsupported_prompt_adapter(context) -> None:
    _environment(context)
    context.agent = Agent.CODEX


@given("an active reminder under a confirmed prompt-submission adapter")
def supported_active_reminder(context) -> None:
    supported_prompt_adapter(context)
    _start(context)


@given("an eligible agent integration")
def eligible_agent_integration(context) -> None:
    supported_prompt_adapter(context)


@when("the packaged contract inventory is loaded")
def load_contract_inventory(context) -> None:
    context.workflows = support.packaged_contract_inventory()
    context.components = support.packaged_component_inventory()


@when("the malformed workflow contract is decoded")
def decode_malformed_contract(context) -> None:
    try:
        support.decode_workflow_contract(context.contract_payload)
    except Exception as error:  # public diagnostic is asserted below
        context.error = error


@when("the zpp-new-feature reminder starts")
def start_new_feature(context) -> None:
    _start(context)


@when("the same zpp-new-feature reminder starts again")
def resume_new_feature(context) -> None:
    context.before = copy.deepcopy(context.payload)
    _start(context)


@when("zpp-fix-bug is started for the same targets")
def start_different_workflow(context) -> None:
    context.result = context.environment.start("zpp-fix-bug")


@when("the kernel checks a declared playbook component without registration")
def check_unregistered_playbook(context) -> None:
    context.result = context.environment.run(
        "check",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--workflow",
        "zpp-new-feature",
        "--component",
        "zpps-clarify",
    )


@when("the kernel checks a standalone explore component")
def check_standalone_component(context) -> None:
    context.result = context.environment.run(
        "check",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-explore",
    )


@when("a valid custom explore stage is inserted before clarify")
def insert_custom_stage(context) -> None:
    context.result = context.environment.run(
        "stage",
        "insert",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--id",
        "custom-explore",
        "--component",
        "zpps-explore",
        "--before",
        "clarify",
    )


@when("the same custom stage is upserted twice")
def upsert_custom_stage_twice(context) -> None:
    arguments = (
        "stage",
        "upsert",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--id",
        "custom-explore",
        "--component",
        "zpps-explore",
        "--before",
        "clarify",
    )
    support.result_json(context.environment.run(*arguments))
    context.result = context.environment.run(*arguments)


@when("an edit would duplicate the custom stage identifier")
def duplicate_custom_stage(context) -> None:
    context.before = context.environment.state_snapshot()
    context.result = context.environment.run(
        "stage",
        "insert",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--id",
        "custom-explore",
        "--component",
        "zpps-explore",
        "--before",
        "clarify",
    )


@when("the active reminder is stopped")
def stop_reminder(context) -> None:
    context.result = context.environment.run(
        "stop",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
    )


@when("the kernel checks the pending clarify component")
def check_matching_component(context) -> None:
    context.result = context.environment.run(
        "check",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-clarify",
    )


@when("the kernel checks shape-bdd before clarify")
def check_mismatching_component(context) -> None:
    context.result = context.environment.run(
        "check",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-shape-bdd",
    )


@when("the prompt reminder hook runs")
def run_prompt_reminder(context) -> None:
    context.before = context.environment.state_snapshot()
    context.result = context.environment.run("remind", str(context.environment.root))
    context.after = context.environment.state_snapshot()


@when("the packaged reminder hook inventory is inspected")
def inspect_reminder_hook(context) -> None:
    context.hook = support.packaged_reminder_hook(context.agent)


@when("the project integration is installed")
def install_project_integration(context) -> None:
    context.result = context.environment.invoke(
        "workflow",
        "install",
        "--agent",
        context.agent.value,
        "--target",
        str(context.environment.root),
    )


@when("the pending clarify result is recorded as completed")
def record_completed_clarify(context) -> None:
    context.result = context.environment.run(
        "record",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-clarify",
        "--result",
        "completed",
    )


@when("a fresh CLI process inspects workflow status")
def inspect_fresh_status(context) -> None:
    context.environment.runner = support.CliRunner()
    context.result = context.environment.status()


@when("read-only exploration is reported while the reminder is active")
def report_exploration(context) -> None:
    context.before = context.environment.state_snapshot()
    context.result = context.environment.run(
        "record",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-explore",
        "--result",
        "completed",
    )


@when("the workflow reminder starts before lease acquisition")
def start_before_lease(context) -> None:
    _start(context)


@when("an observed bundle is associated with the active reminder")
def associate_bundle(context) -> None:
    context.before = context.environment.state_snapshot()
    context.result = context.environment.run(
        "record",
        "--root",
        str(context.environment.root),
        "--change",
        "sample-change",
        "--component",
        "zpps-clarify",
        "--result",
        "completed",
        "--bundle",
        "00000000-0000-0000-0000-000000000001",
    )


@then("every complete playbook and component has one valid cross-referenced contract")
def complete_contract_inventory(context) -> None:
    assert {item.name for item in context.workflows}
    assert {item.name for item in context.components}
    component_names = {item.name for item in context.components}
    assert all(
        stage.component in component_names
        for workflow in context.workflows
        for stage in workflow.stages
    )


@then("decoding is rejected with the exact source and unknown field")
def malformed_contract_rejected(context) -> None:
    assert "bdd-invalid-workflow.json" in str(context.error)
    assert "unknown" in str(context.error)


@then("the persisted checklist reports clarify as its first pending stage")
def clarify_is_first(context) -> None:
    payload = support.result_json(context.result)
    assert payload["next_stage"]["id"] == "clarify", payload


@then("the completed clarify result remains completed")
def clarify_remains_completed(context) -> None:
    payload = support.result_json(context.result)
    clarify = next(item for item in payload["stages"] if item["id"] == "clarify")
    assert clarify["status"] == "completed", payload


@then("the existing workflow is reported without replacement")
def different_workflow_preserved(context) -> None:
    assert context.result.exit_code != 0
    assert "zpp-new-feature" in context.result.output


@then("workflow-start-required is returned without progress")
def workflow_start_required(context) -> None:
    payload = support.result_json(context.result)
    assert payload["status"] == "workflow-start-required", payload


@then("the component is allowed and reported as untracked")
def standalone_is_untracked(context) -> None:
    payload = support.result_json(context.result)
    assert payload["allowed"] is True
    assert payload["tracking"] == "untracked"


@then("status reports the custom stage before clarify")
def custom_stage_precedes_clarify(context) -> None:
    support.result_json(context.result)
    payload = support.result_json(context.environment.status())
    ids = [item["id"] for item in payload["stages"]]
    assert ids.index("custom-explore") < ids.index("clarify"), payload


@then("exactly one custom stage remains")
def one_custom_stage(context) -> None:
    support.result_json(context.result)
    payload = support.result_json(context.environment.status())
    assert [item["id"] for item in payload["stages"]].count("custom-explore") == 1


@then("the invalid edit is rejected without state change")
def invalid_edit_preserves_state(context) -> None:
    assert context.result.exit_code != 0
    assert context.environment.state_snapshot() == context.before


@then("workflow status is absent while Bundler state is unchanged")
def stopped_without_lease_change(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    status = context.environment.status()
    assert status.exit_code != 0
    assert not (context.environment.home / "bundler").exists()


@then("the result is an allowed sequence match")
def sequence_matches(context) -> None:
    payload = support.result_json(context.result)
    assert payload["allowed"] is True
    assert payload["sequence_match"] is True


@then("the result is an allowed warning naming clarify and all unfinished stages")
def sequence_warning(context) -> None:
    payload = support.result_json(context.result)
    assert payload["allowed"] is True
    assert payload["sequence_match"] is False
    assert payload["expected_stage"]["id"] == "clarify"
    assert payload["unfinished_stages"]


@then("compact active status is emitted without state change")
def compact_status_without_change(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "zpp-new-feature" in context.result.stdout
    assert "clarify" in context.result.stdout
    assert context.after == context.before


@then("no prompt text or product state is created")
def inactive_hook_is_silent(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert context.result.stdout == ""
    assert context.after == context.before == {}


@then("no reminder hook is packaged for that adapter")
def unsupported_hook_omitted(context) -> None:
    assert context.hook is None


@then("Agent Router owns both zpp-traits and zpp-workflow-reminder")
def lifecycle_owns_both_hooks(context) -> None:
    assert context.result.exit_code == 0, context.result.output
    assert "zpp-traits" in context.result.stdout
    assert "zpp-workflow-reminder" in context.result.stdout


@then("shape-bdd becomes the next pending stage")
def shape_bdd_is_next(context) -> None:
    payload = support.result_json(context.result)
    assert payload["next_stage"]["component"] == "zpps-shape-bdd", payload


@then("the persisted next stage remains shape-bdd")
def persisted_shape_bdd(context) -> None:
    payload = support.result_json(context.result)
    assert payload["next_stage"]["component"] == "zpps-shape-bdd", payload


@then("the clarify stage remains pending")
def clarify_remains_pending(context) -> None:
    payload = support.result_json(context.environment.status())
    clarify = next(item for item in payload["stages"] if item["id"] == "clarify")
    assert clarify["status"] == "pending", payload


@then("no Bundler state exists")
def no_bundler_state(context) -> None:
    assert not (context.environment.home / "bundler").exists()


@then("the bundle reference is visible without changing Bundler members")
def bundle_reference_only(context) -> None:
    payload = support.result_json(context.result)
    assert payload["bundle"] == "00000000-0000-0000-0000-000000000001"
    assert not (context.environment.home / "bundler").exists()
