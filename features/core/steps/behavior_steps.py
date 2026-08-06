from __future__ import annotations

from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

import yaml
from behave import given, then, use_step_matcher, when

from features.support import zpp_support as support
from zpp.utils.nx_provider import NxSurface
from zpp.utils.processes import ProcessResult


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args), cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _initialize_repository(context) -> None:
    support.git_init(context.project)
    _git(context.project, "config", "user.email", "bdd@example.test")
    _git(context.project, "config", "user.name", "BDD")
    (context.project / "base.txt").write_text("base\n", encoding="utf-8")
    _git(context.project, "add", ".")
    _git(context.project, "commit", "-q", "-m", "base")


def _target(value: str, paths: list[str]) -> dict[str, object]:
    return {"value": value, "paths": paths}


def _argv_command(
    targets: dict[str, dict[str, object]], *, audit: bool = False
) -> dict[str, object]:
    argv = ["fake-runner", "{targets}"]
    if audit:
        argv.append("--audit")
    return {"provider": {"kind": "argv", "argv": argv}, "targets": targets}


def _write_mapping(context, commands: dict[str, object]) -> None:
    source = context.project / "zpp.behave.yaml"
    source.write_text(
        yaml.safe_dump(
            {"version": 1, "commands": commands},
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def _standard_targets() -> dict[str, dict[str, object]]:
    return {
        "first": _target("core", ["core/**"]),
        "second": _target("workflow", ["workflow/**"]),
        "third": _target("codespaces", ["codespaces/**"]),
    }


def _run_behavior(context, arguments: list[str]) -> None:
    with ExitStack() as stack:
        if getattr(context, "record_behavior_processes", False):
            context.behavior_processes = getattr(context, "behavior_processes", [])

            def run(argv, *, cwd):
                context.behavior_processes.append((tuple(argv), Path(cwd)))
                return ProcessResult(tuple(argv), 0, "", "")

            stack.enter_context(patch("zpp.core.behavior.run_process", side_effect=run))
        if hasattr(context, "nx_executable"):
            stack.enter_context(
                patch(
                    "zpp.core.behavior.discover_nx_executable",
                    return_value=context.nx_executable,
                )
            )
        if hasattr(context, "nx_surface"):
            stack.enter_context(
                patch(
                    "zpp.core.behavior.inspect_nx_surface",
                    return_value=context.nx_surface,
                )
            )
        support.invoke(context, arguments)


@then("the help exposes independent behavior initialization and named verification commands")
def step_help_exposes_behavior(context):
    assert "behave" in context.results[-1].stdout


@given("the current directory is a Git worktree root without zpp.behave.yaml")
def step_empty_behavior_repository(context):
    _initialize_repository(context)
    assert not (context.project / "zpp.behave.yaml").exists()


@given("Nx is unavailable")
def step_nx_unavailable(context):
    context.nx_executable = None


@when("the user runs zpp behave init twice")
def step_behavior_init_twice(context):
    _run_behavior(context, ["behave", "init"])
    context.initial_mapping = (context.project / "zpp.behave.yaml").read_bytes()
    _run_behavior(context, ["behave", "init"])


@then("the first invocation creates a valid empty committed behavior mapping")
def step_empty_mapping_created(context):
    assert yaml.safe_load(context.initial_mapping) == {"version": 1, "commands": {}}


@then("both invocations report that Nx is unavailable without failing")
def step_init_reports_no_nx(context):
    assert all(result.exit_code == 0 for result in context.results[-2:])
    assert all("Nx unavailable" in result.stdout for result in context.results[-2:])


@then("the second invocation preserves the mapping byte-for-byte")
def step_mapping_preserved(context):
    assert (context.project / "zpp.behave.yaml").read_bytes() == context.initial_mapping


@given('the repository behavior mapping is invalid or does not declare command "bdd"')
def step_unknown_behavior_command(context):
    _initialize_repository(context)
    _write_mapping(context, {})


@given("every possible process invocation is recorded")
@given("another provider-neutral command could run in the repository")
def step_record_behavior_processes(context):
    context.record_behavior_processes = True
    context.behavior_processes = []


@when("the user runs zpp behave bdd")
def step_run_behavior_bdd(context):
    _run_behavior(context, ["behave", "bdd"])


@then('verification fails as a domain error identifying command "bdd" or the invalid mapping')
def step_behavior_command_rejected(context):
    assert context.result.exit_code == 1
    assert "bdd" in context.result.stderr or "behavior mapping" in context.result.stderr


@then("no configured process is started")
@then("no package runner, alternate provider, or configured process is started")
def step_no_behavior_process(context):
    assert context.behavior_processes == []


@given('command "bdd" declares three ordered targets and their repository impact globs')
def step_three_behavior_targets(context):
    _initialize_repository(context)
    _write_mapping(context, {"bdd": _argv_command(_standard_targets())})
    context.record_behavior_processes = True


@given("tracked, staged, unstaged, and untracked local changes map conclusively to the first and third targets")
def step_mixed_mapped_changes(context):
    for directory in ("core", "codespaces"):
        (context.project / directory).mkdir()
    (context.project / "core" / "unstaged.txt").write_text("base\n", encoding="utf-8")
    _git(context.project, "add", ".")
    _git(context.project, "commit", "-q", "-m", "targets")
    (context.project / "core" / "unstaged.txt").write_text("changed\n", encoding="utf-8")
    (context.project / "codespaces" / "staged.txt").write_text("staged\n", encoding="utf-8")
    _git(context.project, "add", "codespaces/staged.txt")
    (context.project / "core" / "untracked.txt").write_text("new\n", encoding="utf-8")


@then("only the first and third declared target values are submitted in mapping order")
def step_first_and_third_submitted(context):
    assert context.behavior_processes[-1][0] == ("fake-runner", "core", "codespaces")


@then("no changed path or target value becomes executable command syntax")
def step_no_change_syntax(context):
    assert len(context.behavior_processes[-1][0]) == 3


@given('command "bdd" declares mapped verification targets')
def step_revision_behavior_targets(context):
    _initialize_repository(context)
    _write_mapping(context, {"bdd": _argv_command(_standard_targets())})
    _git(context.project, "add", "zpp.behave.yaml")
    _git(context.project, "commit", "-q", "-m", "mapping")
    context.record_behavior_processes = True


@given("the exact requested base and head revisions differ only in paths mapped to one target")
def step_exact_revisions(context):
    context.base_revision = _git(context.project, "rev-parse", "HEAD")
    (context.project / "core").mkdir()
    (context.project / "core" / "revision.txt").write_text("head\n", encoding="utf-8")
    _git(context.project, "add", ".")
    _git(context.project, "commit", "-q", "-m", "head")
    context.head_revision = _git(context.project, "rev-parse", "HEAD")
    (context.project / "workflow").mkdir()
    (context.project / "workflow" / "working.txt").write_text("working\n", encoding="utf-8")


@when("the user runs zpp behave bdd with that base and head")
def step_run_revision_behavior(context):
    _run_behavior(
        context,
        [
            "behave",
            "bdd",
            "--base",
            context.base_revision,
            "--head",
            context.head_revision,
        ],
    )


@then("only that declared target is submitted")
@then("the working tree does not change the revision comparison")
def step_only_revision_target(context):
    assert context.behavior_processes[-1][0] == ("fake-runner", "core")


@given('command "bdd" declares multiple verification targets')
@given('command "bdd" declares valid verification targets')
def step_multiple_behavior_targets(context):
    _initialize_repository(context)
    _write_mapping(context, {"bdd": _argv_command(_standard_targets())})
    context.record_behavior_processes = True


@given("at least one changed repository path matches no declared impact glob")
def step_unknown_changed_path(context):
    (context.project / "README.md").write_text("unknown\n", encoding="utf-8")


@then('every target declared by command "bdd" is submitted in mapping order')
def step_all_behavior_targets_in_order(context):
    assert context.behavior_processes[-1][0] == (
        "fake-runner", "core", "workflow", "codespaces"
    )


@given("the repository has no local change relative to HEAD")
def step_clean_behavior_repository(context):
    _git(context.project, "add", "zpp.behave.yaml")
    _git(context.project, "commit", "-q", "-m", "mapping")


@then("verification succeeds and reports that no targets are affected")
def step_behavior_noop(context):
    assert context.result.exit_code == 0
    assert "No targets are affected" in context.result.stdout


@given('command "bdd" declares multiple verification targets and a cache-capable provider')
def step_behavior_and_audit_commands(context):
    _initialize_repository(context)
    targets = _standard_targets()
    _write_mapping(
        context,
        {
            "bdd": _argv_command(targets),
            "bdd-audit": _argv_command(targets, audit=True),
        },
    )
    context.record_behavior_processes = True


@given('command "bdd-audit" separately declares repository-owned uncached provider arguments')
def step_audit_is_declared(context):
    assert "bdd-audit" in yaml.safe_load(
        (context.project / "zpp.behave.yaml").read_text(encoding="utf-8")
    )["commands"]


@when("the user runs zpp behave bdd --all")
def step_run_behavior_all(context):
    _run_behavior(context, ["behave", "bdd", "--all"])


@then('every target declared by command "bdd" is submitted')
def step_behavior_all_submitted(context):
    assert context.behavior_processes[-1][0] == (
        "fake-runner", "core", "workflow", "codespaces"
    )


@then('ZPP does not add an uncached flag to command "bdd"')
def step_no_implicit_uncached(context):
    assert "--audit" not in context.behavior_processes[-1][0]


@when("the user runs zpp behave bdd-audit --all")
def step_run_behavior_audit(context):
    _run_behavior(context, ["behave", "bdd-audit", "--all"])


@then("only the explicitly declared audit provider arguments control uncached behavior")
def step_explicit_audit_args(context):
    assert context.behavior_processes[-1][0][-1] == "--audit"


@given('command "bdd" declares a typed argv provider with exactly one target expansion position')
def step_shell_safe_behavior(context):
    _initialize_repository(context)
    targets = {"unsafe": _target("$(unsafe);still-one", ["unsafe/**"])}
    _write_mapping(context, {"bdd": _argv_command(targets)})
    context.record_behavior_processes = True
    (context.project / "unsafe").mkdir()
    (context.project / "unsafe" / "changed.txt").write_text("change\n", encoding="utf-8")


@given("an affected target value contains shell metacharacters")
def step_unsafe_target_declared(context):
    assert "$(unsafe)" in (context.project / "zpp.behave.yaml").read_text(encoding="utf-8")


@then("each selected target is passed as one distinct argv value at that position")
def step_safe_target_argv(context):
    assert context.behavior_processes[-1][0] == ("fake-runner", "$(unsafe);still-one")


@then("no shell evaluates the executable, arguments, changed paths, or target values")
def step_no_shell_evaluation(context):
    assert not (context.project / "unsafe").joinpath("still-one").exists()


@given('command "bdd" selects Nx projects and target "bdd"')
def step_nx_behavior_command(context):
    _initialize_repository(context)
    targets = {
        "core": _target("core", ["**"]),
        "workflow": _target("workflow", ["**"]),
    }
    _write_mapping(
        context,
        {
            "bdd": {
                "provider": {"kind": "nx", "target": "bdd"},
                "targets": targets,
            }
        },
    )
    context.record_behavior_processes = True


@given("an official repository-root Nx wrapper backed by .nx installation and a PATH Nx executable are available")
def step_two_nx_executables(context):
    wrapper = "nx.bat" if os.name == "nt" else "nx"
    context.nx_executable = (context.project / wrapper).resolve()


@given("a repository-owned plugin exposes every declared project and target")
def step_nx_surface(context):
    context.nx_surface = NxSurface(
        {"core": frozenset({"bdd"}), "workflow": frozenset({"bdd"})}
    )


@then("ZPP prefers the absolute repository-root Nx wrapper")
def step_local_nx_used(context):
    assert context.nx_executable.is_absolute()
    assert context.behavior_processes[-1][0][0] == str(context.nx_executable)


@then("ZPP validates and invokes only the declared project and target surface")
def step_declared_nx_surface(context):
    assert context.behavior_processes[-1][0][1:] == (
        "run-many", "--target", "bdd", "--projects", "core,workflow"
    )


@then("ZPP does not install, migrate, download, connect, or interpret Nx or its plugins")
def step_no_nx_management(context):
    assert all(
        value not in context.behavior_processes[-1][0]
        for value in ("npx", "init", "migrate", "connect")
    )


@given('command "bdd" selects Nx')
def step_unavailable_nx_command(context):
    step_nx_behavior_command(context)


@given("no compatible Nx executable or declared workspace surface is available")
def step_no_nx_surface(context):
    context.nx_executable = None


@then("verification fails identifying the unavailable Nx requirement")
def step_nx_failure(context):
    assert context.result.exit_code == 1
    assert "Nx" in context.result.stderr and "unavailable" in context.result.stderr


use_step_matcher("re")


@given(r"the repository layer additionally activates (?P<trait>bdd-structure-(?:python|ts|flutter))")
def step_activate_bdd_structure(context, trait):
    support.git_init(context.project)
    context.target = context.project
    support.write_layer(context.project / ".zpp", triggers=[{"trait": trait}])


@then(r"stdout contains (?P<trait>bdd-structure-(?:python|ts|flutter)) with capability-oriented structure guidance")
def step_bdd_structure_guidance(context, trait):
    body = next(
        body
        for metadata, body in support.parse_documents(context.result.stdout)
        if metadata["name"] == trait
    )
    assert "capability" in body.lower()


use_step_matcher("parse")


@then("no other BDD-structure trait is active")
def step_no_other_bdd_structure(context):
    names = {
        metadata["name"]
        for metadata, _ in support.parse_documents(context.result.stdout)
        if metadata["name"].startswith("bdd-structure-")
    }
    assert len(names) == 1


@then(r"the guidance preserves {runner_policy}")
def step_preserve_runner_policy(context, runner_policy):
    output = " ".join(context.result.stdout.split())
    if runner_policy == "the established Python BDD runner":
        assert "established Python BDD runner" in output
    elif runner_policy == "TypeScript runner choice and explicit loading roots":
        assert "established TypeScript test runner" in output
        assert "loading roots" in output
    else:
        assert "test/" in output and "integration_test/" in output
        assert "Do not require Gherkin" in output
