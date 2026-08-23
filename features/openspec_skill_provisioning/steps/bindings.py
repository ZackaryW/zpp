from __future__ import annotations

from unittest.mock import patch

import support
from behave import given, then, when

EXACT_FAMILY_STEP = (
    "all current workflow entries, stages, adapters, and repository verifier "
    "are present"
)


@given("a disposable user home")
def disposable_home(context) -> None:
    context.home = support.Home()


@given("a disposable uv tool environment")
def disposable_tool_environment(context) -> None:
    context.tool_environment = support.ToolEnvironment()


@given("the codex agent is initialized")
def initialized(context) -> None:
    result = context.home.run("init", "--agent", "codex")
    assert result.exit_code == 0, result.output


@when("ZPP prepares its packaged workflow family")
def prepare_family(context) -> None:
    context.workflow_names = support.workflow_names()


@when("a user initializes the codex agent")
def initialize(context) -> None:
    context.records = context.home.run_json("init", "--agent", "codex", "--json")


@when("a user synchronizes the codex agent")
def synchronize(context) -> None:
    context.records = context.home.run_json("sync", "--agent", "codex", "--json")


@when("a user installs the built ZPP wheel as a tool")
def install_distribution(context) -> None:
    context.distribution = context.tool_environment.install()


@when("a user initializes synchronizes and resets the codex integration")
def lifecycle_without_openspec(context) -> None:
    openspec_calls: list[tuple[object, ...]] = []

    def reject_openspec(*args, **kwargs):
        command = args[0] if args else kwargs.get("args", ())
        if command and str(command[0]).casefold() == "openspec":
            openspec_calls.append(tuple(command))
            raise AssertionError("lifecycle invoked OpenSpec")
        raise AssertionError(f"unexpected subprocess invocation: {command!r}")

    with patch("subprocess.run", side_effect=reject_openspec):
        context.lifecycle_results = (
            context.home.run("init", "--agent", "codex"),
            context.home.run("sync", "--agent", "codex"),
            context.home.run(
                "--path", str(context.home.product_home), "reset", "--yes"
            ),
        )
    context.openspec_calls = openspec_calls


@then(EXACT_FAMILY_STEP)
def exact_family_present(context) -> None:
    assert tuple(context.workflow_names) == support.WORKFLOW_SKILL_NAMES
    assert set(support.OPENSPEC_ADAPTER_SKILL_NAMES) <= set(context.workflow_names)
    assert support.REPOSITORY_EVIDENCE_SKILL_NAME in context.workflow_names


@then("onboarding and removed workflow identities are absent")
def removed_family_absent(context) -> None:
    names = set(context.workflow_names)
    assert "zpps-onboard" not in names
    assert "zpp-workflow" not in names
    assert not names.intersection(support.OBSOLETE_WORKFLOW_SKILL_NAMES)


@then("one lifecycle result is reported per current packaged asset")
def one_result_each(context) -> None:
    assert len(context.records) == support.expected_asset_count(), context.records


@then("every current packaged skill is present on disk")
def packaged_skills_present(context) -> None:
    for name in support.packaged_skill_names():
        assert (context.home.skill_path(name) / "SKILL.md").is_file(), name


@then("no generated OpenSpec skill or provenance is present")
def generated_assets_absent(context) -> None:
    for name in support.OBSOLETE_WORKFLOW_SKILL_NAMES:
        assert not context.home.skill_path(name).exists(), name
    assert not tuple(context.home.user_home.rglob(".zpp-openspec.json"))


@then("every lifecycle command succeeds without an OpenSpec process")
def lifecycle_succeeds(context) -> None:
    assert context.openspec_calls == []
    for result in context.lifecycle_results:
        assert result.exit_code == 0, result.output


@then("every current packaged asset reports current")
def all_current(context) -> None:
    assert len(context.records) == support.expected_asset_count(), context.records
    assert {record["decision"] for record in context.records} == {"current"}


@then("zpp is the only installed tool command")
def only_zpp_tool(context) -> None:
    evidence = context.distribution
    assert evidence.command_names == ("zpp",), evidence.command_names
    assert evidence.tool_list.splitlines() == [
        f"zpp v{evidence.project_version}",
        "- zpp",
    ]


@then("the distribution module and CLI versions agree")
def distribution_versions_agree(context) -> None:
    evidence = context.distribution
    assert evidence.wheel_version == evidence.project_version
    assert evidence.module_version == evidence.project_version
    assert evidence.cli_output == f"ZPP version {evidence.project_version}"


@then("OpenSpec Bundler is present only as a ZPP dependency")
def bundler_is_dependency_only(context) -> None:
    evidence = context.distribution
    assert "openspec-bundler" in evidence.installed_packages
    assert "openspec-bundler" not in evidence.command_names
    assert "openspec-bundler" not in evidence.tool_list.casefold()
    assert evidence.bundler_console_commands == ()
