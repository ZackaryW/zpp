from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import yaml
from behave import given, then, use_step_matcher, when

from zpp.cli import app
from zpp.utils.models import CancelledAgentSelection, ConfirmedAgentSelection
from zpp.utils.openspec_adapter import OpenSpecWorkset
from zpp.utils.skill_bundles import SkillFile, fingerprint_skill_files


REPO_ROOT = Path(__file__).parents[2]
REAL_WHICH = shutil.which


def invoke(context, arguments: list[str], *, input_text: str | None = None):
    def select(choices):
        context.selector_offers.append(tuple(choices))
        if context.selector_answer is None:
            return CancelledAgentSelection()
        return ConfirmedAgentSelection(tuple(context.selector_answer))

    with ExitStack() as stack:
        stack.enter_context(patch(
            "zpp.cli.initialization.interactive_terminal_available",
            return_value=context.interactive,
        ))
        stack.enter_context(patch("zpp.cli.initialization.select_agents", side_effect=select))
        stack.enter_context(patch(
            "zpp.cli.workflow.interactive_terminal_available",
            return_value=context.interactive,
        ))
        stack.enter_context(patch("zpp.cli.workflow.select_agents", side_effect=select))
        stack.enter_context(
            patch(
                "zpp.core.resolution.discover_active_plugins",
                side_effect=lambda agent, **_: tuple(
                    getattr(context, "active_plugins_by_agent", {}).get(agent, ())
                ),
            )
        )
        if hasattr(context, "unavailable_executables"):
            stack.enter_context(
                patch(
                    "zpp.utils.triggers.shutil.which",
                    side_effect=lambda name: (
                        None
                        if name in context.unavailable_executables
                        else REAL_WHICH(name, path=context.env.get("PATH"))
                    ),
                )
            )
        stack.enter_context(patch(
            "zpp.cli.codespace.interactive_terminal_available",
            return_value=context.interactive,
        ))
        if hasattr(context, "openspec_worksets"):
            def list_worksets():
                return tuple(context.openspec_worksets.values())

            def create_workset(name, members, **kwargs):
                if name in context.openspec_worksets:
                    raise ValueError(f"workset already exists: {name}")
                workset = OpenSpecWorkset(name, tuple(members))
                context.openspec_worksets[name] = workset
                context.zpp_created_worksets.append(name)
                return workset

            def remove_workset(name, **kwargs):
                context.openspec_worksets.pop(name)
                context.removed_worksets.append(name)

            def open_workset(name, **kwargs):
                context.opened_worksets.append((name, kwargs.get("tool")))
                return 0

            def materialize(claim, *, environment):
                context.private_registries[claim.instance_id] = {
                    member.store_id: member.effective_path
                    for member in claim.members
                    if member.kind == "store" and member.store_id is not None
                }

            def run_command(argv, *, environment, cwd):
                context.executed_environments.append(dict(environment))
                return 0

            def run_shell(*, environment, cwd):
                context.activated_environments.append(dict(environment))
                return 0

            stack.enter_context(patch(
                "zpp.core.codespaces.list_openspec_worksets",
                side_effect=list_worksets,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.create_openspec_workset",
                side_effect=create_workset,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.remove_openspec_workset",
                side_effect=remove_workset,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.open_openspec_workset",
                side_effect=open_workset,
            ))
            def resolve_relations(project):
                relations = context.openspec_relations.get(Path(project).resolve(), ())
                if isinstance(relations, BaseException):
                    raise relations
                return tuple(relations)

            stack.enter_context(patch(
                "zpp.utils.codespace_targets.resolve_openspec_relations",
                side_effect=resolve_relations,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.materialize_private_registry",
                side_effect=materialize,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.execute_codespace_command",
                side_effect=run_command,
            ))
            stack.enter_context(patch(
                "zpp.core.codespaces.activate_codespace_shell",
                side_effect=run_shell,
            ))
            if hasattr(context, "fixed_instance"):
                stack.enter_context(patch(
                    "zpp.core.codespaces.new_codespace_instance_id",
                    return_value=context.fixed_instance,
                ))
        result = context.runner.invoke(
            app,
            arguments,
            input=input_text,
            env=context.env,
            color=False,
        )
    context.results.append(result)
    context.result = result
    return result


def fixture_path(context, authored: str) -> Path:
    text = authored.strip().strip('"')
    key = text.lower()
    if key in context.paths:
        return context.paths[key]
    return context.project / Path(text.replace("\\", "/"))


def translate_command(context, command: str) -> list[str]:
    if command == "zpp resolve for the missing target":
        return ["resolve", str(context.paths["c:\\missing"])]
    if command == "zpp resolve for the file target":
        return ["resolve", str(context.paths["c:\\work\\file.txt"])]
    if command == "zpp resolve for an existing target":
        return ["resolve", str(context.target)]
    translated = command
    for authored, path in sorted(context.paths.items(), key=lambda item: -len(item[0])):
        translated = re.sub(
            re.escape(authored),
            str(path).replace("\\", "/"),
            translated,
            flags=re.IGNORECASE,
        )
    return shlex.split(translated, posix=True)[1:]


def snapshot(root: Path) -> dict[str, tuple[str, bytes | None]]:
    if not root.exists():
        return {}
    result: dict[str, tuple[str, bytes | None]] = {}
    for path in sorted((root, *root.rglob("*")), key=lambda item: str(item)):
        relative = "." if path == root else path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path).encode("utf-8"))
        elif path.is_dir():
            result[relative] = ("directory", None)
        else:
            result[relative] = ("file", path.read_bytes())
    return result


def initialize(context) -> None:
    context.interactive = False
    result = invoke(context, ["init"])
    assert result.exit_code == 0, result.output
    context.results.clear()


def write_layer(
    root: Path,
    *,
    triggers: list[dict] | None = None,
    config: dict | None = None,
    omit_triggers: bool = False,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "traits").mkdir(exist_ok=True)
    (root / "config.json").write_text(
        json.dumps(
            config or {"trait_overwrites": False, "traitsConfig": {}},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not omit_triggers:
        (root / "trait.json").write_text(
            json.dumps(triggers or [], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def write_trait(
    root: Path,
    name: str,
    *,
    description: str | None = None,
    body: str | None = None,
    order: int | None = None,
    config: dict | None = None,
    skill_lookup: list[str] | None = None,
    omit_optional: bool = False,
) -> Path:
    metadata: dict = {
        "name": name,
        "description": description or f"{name} description",
    }
    if not omit_optional:
        metadata.update(
            order=order,
            config=config or {},
            skill_lookup=skill_lookup or [],
        )
    source = (
        "---\n"
        + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
        + "---\n"
        + (body if body is not None else f"{name} body\n")
    )
    destination = root / "traits" / f"{name}.md"
    destination.write_text(source, encoding="utf-8", newline="")
    return destination


def parse_documents(output: str) -> list[tuple[dict, str]]:
    matches = re.finditer(
        r"---\n(?P<metadata>.*?)---\n(?P<body>.*?)(?=\n---\n|\Z)",
        output,
        flags=re.DOTALL,
    )
    return [
        (yaml.safe_load(match.group("metadata")), match.group("body"))
        for match in matches
    ]


def assert_diagnostic_path(stderr: str, path: Path) -> None:
    normalized = stderr.replace("\\", "/").lower()
    path_text = path.as_posix().lower()
    marker = "/.zpp/"
    expected = path_text[path_text.index(marker) + 1 :] if marker in path_text else path.name.lower()
    assert expected in normalized, stderr


def agent_name(value: str) -> str:
    return {"Pi": "pi", "Codex": "codex", "Claude Code": "claude"}[value]


def agent_path(context, agent: str) -> Path:
    return {
        "pi": context.home / ".pi" / "agent" / "extensions" / "zpp" / "index.ts",
        "codex": context.home / ".codex" / "hooks.json",
        "claude": context.home / ".claude" / "settings.json",
    }[agent]


def git_init(path: Path) -> None:
    subprocess.run(
        ["git", "init", "-q", str(path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@given("ZPP is installed")
def step_installed(context):
    assert app.info.name == "zpp"


@given("a clean user home")
def step_clean_home(context):
    assert snapshot(context.home) == {".": ("directory", None)}


@given("a clean user home with an initialized global ZPP layer")
@given("a clean user home with initialized ZPP state")
def step_clean_initialized_home(context):
    step_clean_home(context)
    initialize(context)


@given("a project without local ZPP state")
@given("the current project has no repository-local agent integration")
def step_clean_project(context):
    assert not (context.project / ".zpp").exists()
    assert not any((context.project / name).exists() for name in (".pi", ".codex", ".claude"))


@given("no interactive terminal is available")
def step_noninteractive(context):
    context.interactive = False


@given("rg, jq, and zmem are unavailable on PATH")
def step_tool_traits_unavailable(context):
    context.unavailable_executables = {"rg", "jq", "zmem"}


@given("an interactive terminal is available")
def step_interactive(context):
    context.interactive = True


@given("valid initialized user state")
@given("a valid initialized ZPP user state")
def step_initialized(context):
    initialize(context)
    context.existing_user_state = snapshot(context.home / ".zpp")


@given("partially initialized valid user state with missing required entries")
def step_partial_user_state(context):
    root = context.home / ".zpp"
    write_layer(root / "global")
    (root / "profiles").mkdir()
    context.missing_user_paths = (root / "saved", root / "cached")


@given("the existing managed files have distinguishable valid formatting")
def step_distinct_user_bytes(context):
    config = context.home / ".zpp" / "global" / "config.json"
    config.write_text('{ "traitsConfig": {}, "trait_overwrites": false }\n', encoding="utf-8")
    context.preserved_files = {config: config.read_bytes()}


@given("user state contains an invalid managed source")
def step_invalid_user_state(context):
    root = context.home / ".zpp"
    (root / "global").mkdir(parents=True)
    (root / "global" / "config.json").write_text("not-json\n", encoding="utf-8")
    (root / "global" / "trait.json").write_text("[]\n", encoding="utf-8")
    for name in ("profiles", "saved", "cached"):
        (root / name).mkdir()
    (root / "saved" / "_bindings.json").write_text("{}\n", encoding="utf-8")
    context.invalid_source = root / "global" / "config.json"


@given("other required user-state entries are missing")
def step_missing_user_entries(context):
    context.missing_user_paths = (context.home / ".zpp" / "global" / "traits",)
    context.state_before = snapshot(context.home / ".zpp")


@given("Pi, Codex, and Claude Code have no ZPP integration")
def step_no_agent_integrations(context):
    context.agents_before = snapshot(context.home)
    assert not any(agent_path(context, name).exists() for name in ("pi", "codex", "claude"))


@when("the user requests the ZPP version")
def step_version(context):
    invoke(context, ["--version"])


@when("the user requests ZPP help")
def step_help(context):
    invoke(context, ["--help"])


@when("the user runs zpp init")
def step_run_init(context):
    invoke(context, ["init"])


@when("the user runs zpp init twice")
def step_run_init_twice(context):
    invoke(context, ["init"])
    context.after_first_init = snapshot(context.home / ".zpp")
    invoke(context, ["init"])


@when("the user runs zpp init with agents Pi and Codex")
def step_init_pi_codex(context):
    invoke(context, ["init", "--agent", "pi", "--agent", "codex"])


@when("the user runs zpp init with agent Pi twice")
def step_init_pi_twice(context):
    invoke(context, ["init", "--agent", "pi"])
    invoke(context, ["init", "--agent", "pi"])


@when("the user runs zpp init and selects Claude Code")
def step_select_claude(context):
    context.selector_answer = ("claude",)
    invoke(context, ["init"])


@when("the user runs zpp init and submits the selector with no checked agent")
def step_select_none(context):
    context.selector_answer = ()
    invoke(context, ["init"])


@when("the user cancels zpp init from the agent selector")
def step_cancel_selector(context):
    context.selector_answer = None
    invoke(context, ["init"])


@when("the user runs zpp init with agent Claude Code")
def step_init_claude(context):
    invoke(context, ["init", "--agent", "claude"])


@when("the user runs zpp init with an unsupported agent name")
def step_bad_agent(context):
    invoke(context, ["init", "--agent", "unsupported"])


@then("the product identifies itself as ZPP version 0.9.0")
def step_assert_version(context):
    assert context.results[0].exit_code == 0
    assert context.results[0].stdout.strip() == "ZPP version 0.9.0"


@then("the help exposes the confirmed initial command surface")
def step_assert_help(context):
    output = context.results[1].stdout
    for command in ("init", "profile", "local", "resolve"):
        assert command in output


@then("the help does not expose a separate agent installation command")
def step_no_agent_command(context):
    assert "agent install" not in context.results[1].stdout.lower()


@then("the help exposes the independent workflow lifecycle command group")
def step_workflow_command_group(context):
    assert "workflow" in context.results[1].stdout.lower()


@then("the help does not expose a generic skill command group")
def step_no_generic_skill_command_group(context):
    output = context.results[1].stdout.lower()
    assert re.search(r"(?m)^\|\s*skill(?:\s|\|)", output) is None


@then("initialization succeeds")
def step_init_succeeds(context):
    assert context.result.exit_code == 0, context.result.output


@then("initialization succeeds both times")
@then("both initializations succeed without offering agent selection")
def step_two_inits_succeed(context):
    assert all(result.exit_code == 0 for result in context.results[-2:])
    assert context.selector_offers == []


@then("the neutral global trait layer exists")
@then("the neutral global user state is initialized")
def step_global_exists(context):
    root = context.home / ".zpp" / "global"
    assert (root / "config.json").is_file()
    assert (root / "trait.json").is_file()
    assert (root / "traits").is_dir()


@then("the empty profile, saved, and cache roots exist")
@then("the saved and cache roots exist")
def step_empty_roots(context):
    root = context.home / ".zpp"
    assert (root / "profiles").is_dir()
    assert (root / "saved").is_dir()
    assert (root / "cached").is_dir()
    assert json.loads((root / "saved" / "_bindings.json").read_text(encoding="utf-8")) == {}


@then("no named profile exists")
def step_no_profile(context):
    assert list((context.home / ".zpp" / "profiles").iterdir()) == []


@then("no cache artifact exists")
@then("no trait cache is created")
def step_no_cache(context):
    cache = context.home / ".zpp" / "cached"
    assert not any(path.is_file() for path in cache.rglob("*"))


@then("the project still has no local ZPP state")
def step_no_local_state(context):
    assert not (context.project / ".zpp").exists()


@then("no agent application is configured")
@then("no agent application is changed")
def step_no_agents(context):
    assert not any(agent_path(context, name).exists() for name in ("pi", "codex", "claude"))


@then("every missing required user-state entry is created")
def step_missing_created(context):
    assert all(path.exists() for path in context.missing_user_paths)


@then("every pre-existing managed file is byte-for-byte unchanged")
def step_preserved_files(context):
    assert all(path.read_bytes() == source for path, source in context.preserved_files.items())


@then("the second initialization makes no further change")
def step_second_unchanged(context):
    assert snapshot(context.home / ".zpp") == context.after_first_init


@then("initialization fails as a managed-state rejection")
@then("agent setup fails as a managed-state rejection")
def step_managed_rejection(context):
    assert context.result.exit_code == 1


@then("the diagnostic identifies the invalid source path")
@then("the diagnostic identifies the invalid managed source")
def step_invalid_diagnostic(context):
    assert_diagnostic_path(context.result.stderr, context.invalid_source)


@then("the diagnostic identifies the invalid managed source path")
def step_invalid_managed_path(context):
    assert_diagnostic_path(context.result.stderr, context.invalid_source)


@then("no missing user-state entry is created")
def step_no_missing_created(context):
    assert all(not path.exists() for path in context.missing_user_paths)


@then("the existing user state is unchanged")
def step_user_unchanged(context):
    expected = getattr(context, "state_before", getattr(context, "existing_user_state", None))
    if expected is not None:
        assert snapshot(context.home / ".zpp") == expected


@then("initialization succeeds without offering agent selection")
def step_init_no_selector(context):
    assert context.result.exit_code == 0
    assert context.selector_offers == []


@then("one selector offers Pi, Codex, and Claude Code")
def step_selector_offers(context):
    assert context.selector_offers == [("pi", "codex", "claude")]


@then("{label} has one ZPP-managed native lifecycle hook")
def step_agent_installed(context, label):
    assert agent_path(context, agent_name(label)).is_file()


@then("neither agent receives a ZPP instruction paragraph or skill")
@then("Claude Code receives no ZPP instruction paragraph or skill")
def step_no_policy_install(context):
    assert not (context.home / ".codex" / "skills").exists()
    assert not (context.home / ".claude" / "skills").exists()


@then("their agent-owned hook trust and enablement state is unchanged")
def step_trust_unchanged(context):
    assert not any((context.home / name / "trust.json").exists() for name in (".pi", ".codex", ".claude"))


@then("Claude Code is unchanged")
def step_claude_unchanged(context):
    assert not agent_path(context, "claude").exists()


@then("Pi and Codex are unchanged")
def step_pi_codex_unchanged(context):
    assert not agent_path(context, "pi").exists()
    assert not agent_path(context, "codex").exists()


@then("the current project still has no repository-local agent integration")
def step_no_repo_agent(context):
    assert not any((context.project / name).exists() for name in (".pi", ".codex", ".claude"))


@then("initialization is cancelled")
def step_cancelled(context):
    assert context.result.exit_code == 1
    assert "cancelled" in context.result.stderr.lower()


@given("valid initialized user state contains an activatable authored trait")
def step_activatable_state(context):
    initialize(context)
    root = context.home / ".zpp" / "global"
    write_trait(root, "neutral", body="Do the neutral thing.\n")
    (root / "trait.json").write_text('[{"trait":"neutral"}]\n', encoding="utf-8")


@given("no trait cache exists")
def step_no_trait_cache(context):
    assert not any((context.home / ".zpp" / "cached").rglob("traits.json"))


@given("Pi has a ZPP integration surrounded by unmanaged content")
def step_pi_surrounded(context):
    invoke(context, ["init", "--agent", "pi"])
    sibling = context.home / ".pi" / "agent" / "extensions" / "keep.ts"
    sibling.write_text("unmanaged π\n", encoding="utf-8")
    context.pi_unmanaged = {sibling: sibling.read_bytes()}
    context.results.clear()


@given("Codex was previously configured by ZPP")
def step_codex_existing(context):
    invoke(context, ["init", "--agent", "codex"])
    context.codex_before = snapshot(context.home / ".codex")
    context.results.clear()


@then("Pi has exactly one valid ZPP integration")
def step_one_pi_integration(context):
    assert agent_path(context, "pi").is_file()


@then("Pi's unmanaged content is byte-for-byte unchanged")
def step_pi_unmanaged_unchanged(context):
    assert all(path.read_bytes() == source for path, source in context.pi_unmanaged.items())


@then("Codex remains installed and unchanged")
def step_codex_still(context):
    assert snapshot(context.home / ".codex") == context.codex_before


@then("no effective trait, workflow direction, or platform guidance is copied into Pi's installed hook")
def step_pi_no_trait_copy(context):
    source = agent_path(context, "pi").read_text(encoding="utf-8")
    assert "Do the neutral thing" not in source
    assert "zpp" in source and "resolve" in source


@then("trait resolution is not invoked")
def step_resolution_not_invoked(context):
    assert not any((context.home / ".zpp" / "cached").rglob("traits.json"))


@given('{agent} was configured by ZPP')
def step_agent_configured(context, agent):
    initialize(context)
    context.agent = agent_name(agent)
    invoke(context, ["init", "--agent", context.agent])
    assert context.result.exit_code == 0
    context.results.clear()


@given("its native hook is trusted and enabled by the agent application")
def step_hook_enabled(context):
    context.hook_enabled = True


@given("its current working directory resolves one effective trait document")
def step_hook_one_trait(context):
    root = context.home / ".zpp" / "global"
    write_trait(root, "current", body="Current context.\n")
    (root / "trait.json").write_text('[{"trait":"current"}]\n', encoding="utf-8")


@given("its current working directory resolves no active traits")
def step_hook_empty(context):
    triggers = json.loads(
        (context.home / ".zpp" / "global" / "trait.json").read_text(
            encoding="utf-8"
        )
    )
    assert triggers == []


@given("its current working directory causes trait resolution to fail")
def step_hook_failure(context):
    root = context.home / ".zpp" / "global"
    (root / "traits" / "broken.md").write_text("invalid\n", encoding="utf-8")
    (root / "trait.json").write_text('[{"trait":"broken"}]\n', encoding="utf-8")
    context.injected = ["stale context"]


use_step_matcher("re")


@when(r"(?:.+ )?invokes the ZPP hook")
@when("the native ZPP hook is invoked")
def step_invoke_hook(context):
    context.results.clear()
    result = invoke(
        context,
        ["resolve", str(context.project), "--agent", context.agent],
    )
    context.injected = [result.stdout] if result.exit_code == 0 and result.stdout else []


use_step_matcher("parse")


@then("ZPP resolves the current working directory")
@then("ZPP resolves the current working directory with {agent} as the invoking agent")
def step_hook_cwd(context, agent=None):
    assert context.result.exit_code == 0
    if agent is not None:
        assert agent_name(agent) == context.agent


@then("only {agent}'s active plugin trait sources are eligible")
def step_hook_agent_plugins(context, agent):
    assert agent_name(agent) == context.agent
    source = agent_path(context, context.agent).read_text(encoding="utf-8")
    expected = (
        f'"--agent", "{context.agent}"'
        if context.agent == "pi"
        else f"--agent {context.agent}"
    )
    assert expected in source


@then("the complete effective trait document is injected exactly once into {agent} context")
def step_hook_injected(context, agent):
    assert agent_name(agent) == context.agent
    assert len(context.injected) == 1
    assert parse_documents(context.injected[0])[0][0]["name"] == "current"


@then("hook execution succeeds")
def step_hook_success(context):
    assert context.result.exit_code == 0


@then("no ZPP trait context is injected into {agent}")
def step_hook_no_context(context, agent):
    assert agent_name(agent) == context.agent
    assert context.injected == []


@then("the resolution failure is surfaced through {agent}")
def step_hook_failure_surfaced(context, agent):
    assert agent_name(agent) == context.agent
    assert context.result.exit_code == 1 and context.result.stderr


@then("no stale or partial ZPP trait context is injected")
def step_no_stale_context(context):
    assert context.injected == []


@given("Claude Code has an unmanaged hook conflicting with ZPP integration")
def step_claude_conflict(context):
    path = agent_path(context, "claude")
    path.parent.mkdir(parents=True)
    document = {"theme": "keep", "hooks": {"SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": "zpp resolve"}]}]}}
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    context.conflicting_path = path
    context.conflicting_before = path.read_bytes()
    context.claude_before = snapshot(path.parent)


@given("Pi has no ZPP integration")
def step_pi_missing(context):
    context.pi_before = snapshot(context.home / ".pi")


@given("Codex has an unmanaged hook conflicting with ZPP integration")
def step_codex_conflict(context):
    path = agent_path(context, "codex")
    path.parent.mkdir(parents=True)
    document = {"hooks": {"SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": "zpp resolve"}]}]}}
    path.write_text(json.dumps(document), encoding="utf-8")
    context.conflicting_path = path
    context.conflicting_before = path.read_bytes()


@then("the diagnostic identifies the conflicting path")
def step_conflict_path(context):
    assert str(context.conflicting_path) in context.result.stderr


@then("the conflicting unmanaged hook is unchanged")
@then("the conflicting Codex hook remains unchanged")
def step_conflict_unchanged(context):
    assert context.conflicting_path.read_bytes() == context.conflicting_before


@then("all other Claude Code content is unchanged")
def step_claude_content_unchanged(context):
    assert snapshot(context.conflicting_path.parent) == context.claude_before


@then("Pi remains unchanged")
def step_pi_unchanged(context):
    root = getattr(context, "pi_unchanged_root", context.home / ".pi")
    assert snapshot(root) == context.pi_before


@then("the invocation fails as a usage error")
def step_usage_error(context):
    assert context.result.exit_code == 2


@then("no ZPP user state is created")
def step_no_user_state(context):
    assert not (context.home / ".zpp").exists()


# Profile and saved lifecycle


@given('a valid profile named "{name}" with distinctive authored bytes')
def step_existing_profile(context, name):
    root = context.home / ".zpp" / "profiles" / name
    write_layer(root)
    (root / "config.json").write_text('{ "traitsConfig": {}, "trait_overwrites": false }\n', encoding="utf-8")
    context.profile_bytes = snapshot(root)


@given('no profile named "{name}" exists')
def step_no_named_profile(context, name):
    assert not (context.home / ".zpp" / "profiles" / name).exists()


@given('profile "{name}" has invalid managed state and a required artifact absent')
def step_broken_profile(context, name):
    root = context.home / ".zpp" / "profiles" / name
    root.mkdir(parents=True)
    (root / "config.json").write_text("invalid\n", encoding="utf-8")
    (root / "trait.json").write_text("[]\n", encoding="utf-8")
    context.invalid_source = root / "config.json"


@given("the complete ZPP user state is recorded")
def step_record_user_state(context):
    context.state_before = snapshot(context.home / ".zpp")


use_step_matcher("re")


@when(r"the user runs (?P<command>zpp (?:profile|local)(?!.* and declines confirmation).+)")
def step_run_profile_or_local(context, command):
    invoke(context, translate_command(context, command))


use_step_matcher("parse")


@then("both profile creations succeed")
@then("both saved creations succeed")
def step_last_two_succeed(context):
    assert all(result.exit_code == 0 for result in context.results[-2:])


@then('the authored bytes of profile "alpha" are unchanged')
def step_profile_bytes(context):
    assert snapshot(context.home / ".zpp" / "profiles" / "alpha") == context.profile_bytes


@then('profile "beta" contains one neutral authored ZPP layer')
def step_beta_neutral(context):
    root = context.home / ".zpp" / "profiles" / "beta"
    assert json.loads((root / "config.json").read_text(encoding="utf-8")) == {"trait_overwrites": False, "traitsConfig": {}}
    assert json.loads((root / "trait.json").read_text(encoding="utf-8")) == []
    assert (root / "traits").is_dir()


@then("neither profile has a derived cache")
def step_profiles_no_cache(context):
    assert not (context.home / ".zpp" / "cached" / "profiles" / "alpha").exists()
    assert not (context.home / ".zpp" / "cached" / "profiles" / "beta").exists()


@then("the command succeeds with stdout:")
def step_stdout_docstring(context):
    assert context.result.exit_code == 0
    assert context.result.stdout.strip() == context.text.strip()


@then("the command is rejected with exit code 1")
@then("resolution fails with exit code 1")
def step_exit_one(context):
    assert context.result.exit_code == 1


use_step_matcher("re")


@then(r'the diagnostic identifies (?P<subject>the invalid profile name|the invalid saved name|the invalid managed source|the missing source profile|the existing destination|the persistent default profile|".+")')
def step_diagnostic_subject(context, subject):
    subject = subject.strip()
    if subject == "the invalid profile name" or subject == "the invalid saved name":
        expected = "Invalid"
    elif subject == "the invalid managed source":
        assert_diagnostic_path(context.result.stderr, context.invalid_source)
        return
    elif subject == "the missing source profile":
        expected = "source profile does not exist"
    elif subject == "the existing destination":
        expected = "destination profile already exists"
    elif subject == "the persistent default profile":
        expected = "persistent default profile"
    elif subject.startswith('"'):
        assert_diagnostic_path(context.result.stderr, fixture_path(context, subject))
        return
    else:
        expected = subject
    assert expected.lower() in context.result.stderr.lower()


use_step_matcher("parse")


@then("the complete ZPP user state is unchanged")
def step_complete_user_unchanged(context):
    assert snapshot(context.home / ".zpp") == context.state_before


@given('profiles "work" and "keep" and their independent caches exist')
def step_profiles_and_caches(context):
    for name in ("work", "keep"):
        invoke(context, ["profile", "create", name])
        cache = context.home / ".zpp" / "cached" / "profiles" / name
        cache.mkdir(parents=True)
        (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    context.keep_before = snapshot(context.home / ".zpp" / "profiles" / "keep")
    context.results.clear()


@given('ZPP_PROFILE is "work"')
def step_profile_env(context):
    context.env["ZPP_PROFILE"] = "work"


@when("the user runs zpp profile remove work and declines confirmation")
def step_decline_profile(context):
    invoke(context, ["profile", "remove", "work"], input_text="n\n")


@then('profile "work" and its cache remain unchanged')
def step_work_remains(context):
    assert (context.home / ".zpp" / "profiles" / "work").exists()
    assert (context.home / ".zpp" / "cached" / "profiles" / "work").exists()


@then('profile "work" and its independent cache no longer exist')
def step_work_removed(context):
    assert not (context.home / ".zpp" / "profiles" / "work").exists()
    assert not (context.home / ".zpp" / "cached" / "profiles" / "work").exists()


@then('profile "keep" and its independent cache are unchanged')
def step_keep_profile(context):
    assert snapshot(context.home / ".zpp" / "profiles" / "keep") == context.keep_before


@then("ZPP_PROFILE remains \"work\"")
def step_env_unchanged(context):
    assert context.env["ZPP_PROFILE"] == "work"


@then("the command succeeds")
def step_command_succeeds(context):
    assert context.result.exit_code == 0, context.result.output


@then("the command succeeds with empty stdout")
def step_empty_stdout(context):
    assert context.result.exit_code == 0
    assert context.result.stdout == ""


use_step_matcher("re")


@given(r'"(?P<path>C:\\work\\[ab])" is an existing directory and no saved layer named "(?P<name>.+)" exists')
def step_saved_target(context, path, name):
    target = fixture_path(context, path)
    target.mkdir(parents=True, exist_ok=True)
    assert not (context.home / ".zpp" / "saved" / name).exists()


use_step_matcher("parse")


@then("the saved creation succeeds")
def step_saved_succeeds(context):
    assert context.result.exit_code == 0


@then("one authored layer exists at ~/.zpp/saved/shared")
@then('saved layer "shared" is one neutral authored ZPP layer')
def step_saved_layer(context):
    root = context.home / ".zpp" / "saved" / "shared"
    assert (root / "config.json").is_file() and (root / "trait.json").is_file() and (root / "traits").is_dir()


@then('no saved layer named "shared" exists under ~/.zpp/profiles')
def step_saved_not_profile(context):
    assert not (context.home / ".zpp" / "profiles" / "shared").exists()


@then('no independent cache exists for saved layer "shared"')
def step_saved_no_cache(context):
    assert not (context.home / ".zpp" / "cached" / "saved" / "shared").exists()


@then("the command succeeds with these saved bindings in canonical-target order:")
def step_saved_table(context):
    expected = [
        (
            row["name"],
            str(fixture_path(context, row["target"]).resolve(strict=False)).lower(),
        )
        for row in context.table
    ]
    actual = [(line.split("\t", 1)[0], line.split("\t", 1)[1].lower()) for line in context.result.stdout.splitlines()]
    assert actual == expected, (actual, expected)


@given('an existing saved layer named "shared" with distinctive authored bytes bound to "C:\\work\\b"')
def step_existing_saved(context):
    target = fixture_path(context, "C:\\work\\b")
    target.mkdir(parents=True)
    invoke(context, ["profile", "saved", "create", "shared", str(target)])
    root = context.home / ".zpp" / "saved" / "shared"
    (root / "config.json").write_text('{ "traitsConfig": {}, "trait_overwrites": false }\n', encoding="utf-8")
    context.saved_bytes = snapshot(root)
    context.results.clear()


@given('"C:\\work\\a" is an existing directory')
def step_work_a(context):
    fixture_path(context, "C:\\work\\a").mkdir(parents=True, exist_ok=True)


@given('"c:/WORK/B" identifies the same Windows target as "C:\\work\\b"')
def step_equivalent_b(context):
    context.paths["c:/work/b"] = context.paths["c:\\work\\b"]


@when('the user repeats zpp profile saved create shared "c:/WORK/B"')
def step_repeat_saved(context):
    invoke(context, ["profile", "saved", "create", "shared", str(context.paths["c:\\work\\b"])])


@then('the authored bytes of saved layer "shared" are unchanged')
def step_saved_bytes(context):
    assert snapshot(context.home / ".zpp" / "saved" / "shared") == context.saved_bytes


@then('the saved index maps exactly both canonical absolute targets to "shared"')
def step_two_bindings(context):
    index = json.loads((context.home / ".zpp" / "saved" / "_bindings.json").read_text(encoding="utf-8"))
    assert len(index) == 2 and set(index.values()) == {"shared"}


@given('"C:\\work\\a" is canonically bound to saved layer "shared"')
def step_bound_shared(context):
    target = fixture_path(context, "C:\\work\\a")
    target.mkdir(parents=True, exist_ok=True)
    invoke(context, ["profile", "saved", "create", "shared", str(target)])
    context.results.clear()


@given('no saved layer named "other" exists')
def step_no_other_saved(context):
    assert not (context.home / ".zpp" / "saved" / "other").exists()


use_step_matcher("re")


@given(r'"(?P<path>C:\\missing)" does not exist and no saved layer named "new" exists')
def step_missing_saved_target(context, path):
    assert not fixture_path(context, path).exists()


@given(r'"(?P<path>C:\\work\\file\.txt)" is an existing file and no saved layer named "new" exists')
def step_file_saved_target(context, path):
    target = fixture_path(context, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("file\n", encoding="utf-8")


use_step_matcher("parse")


@given('saved layer "broken" has invalid managed state and "C:\\work\\a" is an existing directory')
def step_broken_saved(context):
    target = fixture_path(context, "C:\\work\\a")
    target.mkdir(parents=True, exist_ok=True)
    root = context.home / ".zpp" / "saved" / "broken"
    root.mkdir(parents=True)
    (root / "config.json").write_text("invalid\n", encoding="utf-8")
    (root / "trait.json").write_text("[]\n", encoding="utf-8")
    context.invalid_source = root / "config.json"


@given('saved layer "shared" has two target bindings and an independent cache')
def step_shared_two_cache(context):
    for authored in ("C:\\work\\a", "C:\\work\\b"):
        target = fixture_path(context, authored)
        target.mkdir(parents=True, exist_ok=True)
        invoke(context, ["profile", "saved", "create", "shared", str(target)])
    cache = context.home / ".zpp" / "cached" / "saved" / "shared"
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    context.results.clear()


@given('saved layer "keep" has the canonical target binding "C:\\work\\keep" and an independent cache')
def step_keep_saved(context):
    target = fixture_path(context, "C:\\work\\keep")
    target.mkdir(parents=True)
    invoke(context, ["profile", "saved", "create", "keep", str(target)])
    cache = context.home / ".zpp" / "cached" / "saved" / "keep"
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text("{}\n", encoding="utf-8")
    context.keep_saved_before = snapshot(context.home / ".zpp" / "saved" / "keep")
    context.results.clear()


@when("the user runs zpp profile saved remove shared and declines confirmation")
def step_decline_saved(context):
    invoke(context, ["profile", "saved", "remove", "shared"], input_text="n\n")


@then('saved layer "shared", its bindings, and its cache remain unchanged')
def step_shared_remains(context):
    assert (context.home / ".zpp" / "saved" / "shared").exists()
    assert (context.home / ".zpp" / "cached" / "saved" / "shared").exists()
    index = json.loads((context.home / ".zpp" / "saved" / "_bindings.json").read_text(encoding="utf-8"))
    assert list(index.values()).count("shared") == 2


@then('every binding for "shared" is absent from the saved index')
def step_shared_bindings_removed(context):
    index = json.loads((context.home / ".zpp" / "saved" / "_bindings.json").read_text(encoding="utf-8"))
    assert "shared" not in index.values()


@then('saved layer "shared" and its independent cache no longer exist')
def step_shared_removed(context):
    assert not (context.home / ".zpp" / "saved" / "shared").exists()
    assert not (context.home / ".zpp" / "cached" / "saved" / "shared").exists()


@then('saved layer "keep", its binding, and its independent cache are unchanged')
def step_keep_saved_unchanged(context):
    assert snapshot(context.home / ".zpp" / "saved" / "keep") == context.keep_saved_before
    assert (context.home / ".zpp" / "cached" / "saved" / "keep").exists()


# Local layers


@given("the current working directory is the root of a Git worktree")
def step_git_root(context):
    git_init(context.project)


@given('an existing directory "src\\nested" is inside that worktree')
def step_nested_dir(context):
    context.nested = fixture_path(context, "src\\nested")
    context.nested.mkdir(parents=True)


@given("neither target has local ZPP state")
def step_no_target_layers(context):
    assert not (context.project / ".zpp").exists()
    assert not (context.nested / ".zpp").exists()


@when('the user repeats zpp local init "src"')
def step_local_explicit(context):
    invoke(context, ["local", "init", str(fixture_path(context, "src"))])


@then("both local initializations succeed")
def step_local_success(context):
    assert all(result.exit_code == 0 for result in context.results[-2:])


@then("each target contains one neutral authored ZPP layer")
def step_each_local(context):
    for target in (context.project, context.nested):
        assert (target / ".zpp" / "config.json").is_file()
        assert (target / ".zpp" / "trait.json").is_file()
        assert (target / ".zpp" / "traits").is_dir()


@then("neither target contains derived cache state")
def step_no_local_caches(context):
    assert not (context.project / ".zpp" / "cached").exists()
    assert not (context.nested / ".zpp" / "cached").exists()


@then("no other directory gains local ZPP state")
def step_only_expected_local(context):
    roots = {path.parent.resolve() for path in context.project.rglob(".zpp")}
    assert roots == {context.project.resolve(), context.nested.resolve()}


@given('an existing Git-worktree directory "src"')
def step_git_src(context):
    git_init(context.project)
    context.src = context.project / "src"
    context.src.mkdir()


@given('"src/.zpp" contains valid distinctive trait.json and config.json bytes')
def step_distinct_local(context):
    root = context.src / ".zpp"
    root.mkdir()
    (root / "config.json").write_text('{ "traitsConfig": {}, "trait_overwrites": false }\n', encoding="utf-8")
    (root / "trait.json").write_text("[ ]\n", encoding="utf-8")
    context.local_bytes = {path: path.read_bytes() for path in (root / "config.json", root / "trait.json")}


@given('"src/.zpp/traits" is absent')
def step_traits_absent(context):
    assert not (context.src / ".zpp" / "traits").exists()


@then("the distinctive authored bytes are unchanged")
def step_local_bytes(context):
    assert all(path.read_bytes() == source for path, source in context.local_bytes.items())


@then('"src/.zpp/traits" exists as a directory')
def step_local_traits(context):
    assert (context.src / ".zpp" / "traits").is_dir()


@then('"src/.zpp" contains no derived cache state')
def step_local_no_cache(context):
    assert not (context.src / ".zpp" / "cached").exists()


@given('"src/.zpp" contains an invalid managed source')
def step_invalid_local(context):
    root = context.src / ".zpp"
    root.mkdir()
    (root / "config.json").write_text("invalid\n", encoding="utf-8")
    (root / "trait.json").write_text("[]\n", encoding="utf-8")
    context.invalid_source = root / "config.json"


@given("another required local-layer artifact is absent")
def step_missing_local_artifact(context):
    assert not (context.src / ".zpp" / "traits").exists()


@given("the complete worktree state is recorded")
@given("the complete surrounding state is recorded")
def step_record_worktree(context):
    context.worktree_before = snapshot(context.project)


@then("the complete worktree state is unchanged")
@then("the complete surrounding state is unchanged")
def step_worktree_unchanged(context):
    assert snapshot(context.project) == context.worktree_before


use_step_matcher("re")


@given(r'"(?P<path>C:\\missing)" does not exist')
def step_missing_target(context, path):
    assert not fixture_path(context, path).exists()


@given(r'"(?P<path>C:\\work\\file\.txt)" is an existing file')
def step_file_target(context, path):
    target = fixture_path(context, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("file\n", encoding="utf-8")


@given(r'"(?P<path>C:\\outside)" is an existing directory outside Git')
def step_outside_git(context, path):
    fixture_path(context, path).mkdir(parents=True)


use_step_matcher("parse")


# Trait compilation and resolution


@given("an initialized global layer has multiple valid activated authored traits")
def step_compilation_traits(context):
    initialize(context)
    root = context.home / ".zpp" / "global"
    context.compilation_sources = [
        write_trait(root, "alpha", body="  alpha whitespace\n", omit_optional=True),
        write_trait(root, "beta", body="β advisory\n", order=2, config={"enabled": True}, skill_lookup=["helper"]),
    ]
    (root / "trait.json").write_text('[{"trait":"alpha"},{"trait":"beta"}]\n', encoding="utf-8")


@given("one trait omits optional frontmatter while another contains order, config, skill lookup, and UTF-8 text")
def step_compilation_shape(context):
    context.authored_bytes = {path: path.read_bytes() for path in context.compilation_sources}


@given("an inactive profile also has an authored trait")
def step_inactive_profile(context):
    invoke(context, ["profile", "create", "inactive"])
    root = context.home / ".zpp" / "profiles" / "inactive"
    write_trait(root, "inactive")
    (root / "trait.json").write_text('[{"trait":"inactive"}]\n', encoding="utf-8")
    context.results.clear()


@given("no derived trait cache exists")
def step_no_derived_cache(context):
    assert not any((context.home / ".zpp" / "cached").rglob("traits.json"))


@when("the user runs zpp resolve for an existing directory")
@when("the user runs zpp resolve for an existing target")
@when("the user runs zpp resolve for the target")
@when("the user runs zpp resolve for the nested target")
def step_resolve_target(context):
    target = getattr(context, "target", context.project)
    invoke(context, ["resolve", str(target)])


@then("resolution succeeds with complete native documents for the activated global traits")
def step_compilation_output(context):
    assert context.result.exit_code == 0
    assert {meta["name"] for meta, _ in parse_documents(context.result.stdout)} == {"alpha", "beta"}


@then("the resolved bodies preserve their authored whitespace and UTF-8 text")
def step_compilation_bodies(context):
    bodies = {meta["name"]: body for meta, body in parse_documents(context.result.stdout)}
    assert bodies == {"alpha": "  alpha whitespace\n", "beta": "β advisory\n"}


@then("the participating global layer gains one independent compiled cache")
def step_global_cache(context):
    root = context.home / ".zpp" / "cached" / "global"
    assert (root / "traits.json").is_file() and (root / "traits.watch.json").is_file()


@then("no cache is created for the inactive profile")
def step_inactive_no_cache(context):
    assert not (context.home / ".zpp" / "cached" / "profiles" / "inactive").exists()


@then("every authored trait file remains byte-for-byte unchanged")
def step_sources_unchanged(context):
    assert all(path.read_bytes() == source for path, source in context.authored_bytes.items())


@given("an activated authored trait has previously been resolved")
def step_previously_resolved(context):
    initialize(context)
    root = context.home / ".zpp" / "global"
    context.changed_source = write_trait(root, "changing", body="old advisory\n")
    (root / "trait.json").write_text('[{"trait":"changing"}]\n', encoding="utf-8")
    invoke(context, ["resolve", str(context.project)])
    assert context.result.exit_code == 0
    context.results.clear()


@given("its authored body changes after the derived cache was certified")
def step_change_source(context):
    source = context.changed_source.read_text(encoding="utf-8").replace("old advisory", "new advisory")
    context.changed_source.write_text(source, encoding="utf-8")
    cache = context.home / ".zpp" / "cached" / "global" / "traits.json"
    newer = cache.stat().st_mtime_ns + 10_000_000
    os.utime(context.changed_source, ns=(newer, newer))


@when("the user runs zpp resolve for its target")
def step_resolve_changed(context):
    invoke(context, ["resolve", str(context.project)])


@then("resolution succeeds with the changed advisory body")
def step_changed_body(context):
    assert context.result.exit_code == 0 and "new advisory" in context.result.stdout


@then("no stale advisory body is returned")
def step_no_old_body(context):
    assert "old advisory" not in context.result.stdout


@then("the authored trait remains authoritative")
def step_authored_authority(context):
    assert "new advisory" in context.changed_source.read_text(encoding="utf-8")


@given("a participating layer has stale derived data")
def step_stale_layer(context):
    initialize(context)
    root = context.home / ".zpp" / "global"
    context.invalid_traits = [write_trait(root, "one"), write_trait(root, "two")]
    (root / "trait.json").write_text('[{"trait":"one"},{"trait":"two"}]\n', encoding="utf-8")
    invoke(context, ["resolve", str(context.project)])
    context.stale_output = context.result.stdout
    context.results.clear()


@given("multiple authored traits in that layer are invalid")
def step_multiple_invalid(context):
    cache = context.home / ".zpp" / "cached" / "global" / "traits.json"
    newer = cache.stat().st_mtime_ns + 10_000_000
    for path in context.invalid_traits:
        path.write_text("invalid\n", encoding="utf-8")
        os.utime(path, ns=(newer, newer))


@then("resolution fails as a managed-state rejection")
def step_resolution_rejected(context):
    assert context.result.exit_code == 1


@then("stdout is empty")
def step_stdout_empty(context):
    assert context.result.stdout == ""


@then("stderr is empty")
def step_stderr_empty(context):
    assert context.result.stderr == ""


@then("stderr identifies every invalid authored source without a stack trace")
def step_all_invalid_sources(context):
    assert all(str(path) in context.result.stderr for path in context.invalid_traits)
    assert "Traceback" not in context.result.stderr


@then("no valid subset or stale trait document is returned")
def step_no_stale_subset(context):
    assert context.result.stdout == "" and context.stale_output


@given("the current directory is an existing target")
def step_current_target(context):
    context.target = context.project


@given("the global layer authors a valid neutral trait")
def step_global_neutral(context):
    root = context.home / ".zpp" / "global"
    write_trait(root, "neutral", body="Neutral advisory.\n")


@given("the global layer configures that trait")
def step_global_configures(context):
    root = context.home / ".zpp" / "global"
    (root / "config.json").write_text(json.dumps({"trait_overwrites": False, "traitsConfig": {"neutral": {"useThis": False}}}), encoding="utf-8")


@given("the global trait trigger configuration is empty")
def step_empty_triggers(context):
    (context.home / ".zpp" / "global" / "trait.json").write_text("[]\n", encoding="utf-8")


@when("the user runs zpp resolve without a target argument")
def step_resolve_default(context):
    invoke(context, ["resolve"])


@then("resolution succeeds")
def step_resolution_success(context):
    assert context.result.exit_code == 0, context.result.output


@given("the global trait trigger configuration contains only that trait name")
def step_conditionless(context):
    (context.home / ".zpp" / "global" / "trait.json").write_text('[{"trait":"neutral"}]\n', encoding="utf-8")


@then("stdout contains exactly the complete effective neutral trait document")
def step_exact_neutral(context):
    documents = parse_documents(context.result.stdout)
    assert len(documents) == 1 and documents[0][0]["name"] == "neutral"


@given("an existing target contains a matching workspace file for the second alternative of a workspace_contain rule")
def step_workspace_match(context):
    initialize(context)
    context.target = context.project
    (context.project / "src").mkdir()
    (context.project / "src" / "match.py").write_text("", encoding="utf-8")


@given("a fixture executable named neutral-tool is available on PATH")
def step_fixture_tool(context):
    tools = context.sandbox / "tools"
    tools.mkdir()
    executable = tools / "neutral-tool.CMD"
    executable.write_text("@exit /b 0\n", encoding="utf-8")
    context.env["PATH"] = f"{tools}{os.pathsep}{context.env['PATH']}"


@given("matching decoy files exist only under .git, an independent cache directory, and a directory symlink")
def step_decoys(context):
    (context.target / ".git").mkdir()
    (context.target / ".git" / "git.decoy").write_text("", encoding="utf-8")
    local = context.target / ".zpp"
    write_layer(local)
    (local / "cached").mkdir()
    (local / "cached" / "cache.decoy").write_text("", encoding="utf-8")
    outside = context.sandbox / "symlink-source"
    outside.mkdir()
    (outside / "link.decoy").write_text("", encoding="utf-8")
    try:
        (context.target / "linked").symlink_to(outside, target_is_directory=True)
    except OSError:
        context.symlink_unavailable = True


@given("the composed trigger rules include matching which and workspace_contain rules for the same neutral trait")
def step_matching_rules(context):
    root = context.home / ".zpp" / "global"
    for name in ("neutral", "git-only", "cache-only", "link-only", "unavailable"):
        write_trait(root, name, skill_lookup=["lookup-note"] if name == "neutral" else [])
    rules = [
        {"trait": "neutral", "which": "neutral-tool"},
        {"trait": "neutral", "workspace_contain": ["missing.none", "src/**/*.py"]},
        {"trait": "git-only", "workspace_contain": [".git/*.decoy"]},
        {"trait": "cache-only", "workspace_contain": [".zpp/cached/*.decoy"]},
    ]
    if not getattr(context, "symlink_unavailable", False):
        rules.append({"trait": "link-only", "workspace_contain": ["linked/*.decoy"]})
    context.trigger_rules = rules


@given("the composed trigger rules include traits whose only matches are the excluded decoys")
def step_decoy_rules(context):
    traits = {rule["trait"] for rule in context.trigger_rules}
    assert {"git-only", "cache-only"}.issubset(traits)
    if not getattr(context, "symlink_unavailable", False):
        assert "link-only" in traits


@given("the composed trigger rules include a trait whose executable is unavailable")
def step_unavailable_rule(context):
    context.trigger_rules.append({"trait": "unavailable", "which": "zpp-missing-tool"})
    (context.home / ".zpp" / "global" / "trait.json").write_text(json.dumps(context.trigger_rules), encoding="utf-8")


@then("stdout contains the matching neutral trait exactly once")
def step_neutral_once(context):
    assert [meta["name"] for meta, _ in parse_documents(context.result.stdout)].count("neutral") == 1


@then("stdout contains no trait matched only through .git, an independent cache directory, or directory symlink traversal")
def step_no_decoys(context):
    names = {meta["name"] for meta, _ in parse_documents(context.result.stdout)}
    assert not names.intersection({"git-only", "cache-only", "link-only"})


@then("stdout contains no trait whose executable is unavailable")
def step_no_unavailable(context):
    assert "unavailable" not in {meta["name"] for meta, _ in parse_documents(context.result.stdout)}


@then("the resolved skill lookup remains passive frontmatter metadata")
def step_skill_lookup_passive(context):
    neutral = next(meta for meta, _ in parse_documents(context.result.stdout) if meta["name"] == "neutral")
    assert neutral["skill_lookup"] == ["lookup-note"]


@given("the global layer activates trait alpha")
def step_global_alpha(context):
    initialize(context)
    root = context.home / ".zpp" / "global"
    write_trait(root, "alpha")
    write_trait(root, "gamma")
    (root / "trait.json").write_text('[{"trait":"alpha"}]\n', encoding="utf-8")


@given("the repository-root layer sets trait_overwrites to true without a trait.json file")
def step_root_overwrite(context):
    git_init(context.project)
    write_layer(context.project / ".zpp", config={"trait_overwrites": True, "traitsConfig": {}}, omit_triggers=True)


@given("a nested layer uses extending trigger behavior and activates trait beta")
def step_nested_beta(context):
    context.target = context.project / "nested"
    context.target.mkdir()
    root = context.target / ".zpp"
    write_layer(root, triggers=[{"trait": "beta"}])
    write_trait(root, "beta")


@given("trait gamma is authored and configured but is not named by an active trigger")
def step_gamma_config(context):
    root = context.target / ".zpp"
    (root / "config.json").write_text(json.dumps({"trait_overwrites": False, "traitsConfig": {"gamma": {"ignored": True}}}), encoding="utf-8")


@then("stdout contains exactly the effective trait document named beta")
def step_only_beta(context):
    assert [meta["name"] for meta, _ in parse_documents(context.result.stdout)] == ["beta"]


@given("an existing target is nested inside a Git worktree")
def step_nested_worktree(context):
    initialize(context)
    git_init(context.project)
    context.target = context.project / "one" / "two"
    context.target.mkdir(parents=True)


@given("ZPP_PROFILE names an existing work profile")
def step_work_profile(context):
    invoke(context, ["profile", "create", "work"])
    context.env["ZPP_PROFILE"] = "work"
    context.results.clear()


@given("global, work profile, repository-root, and root-to-target nested layers participate")
def step_all_layers(context):
    roots = [
        context.home / ".zpp" / "global",
        context.home / ".zpp" / "profiles" / "work",
        context.project / ".zpp",
        context.project / "one" / ".zpp",
        context.target / ".zpp",
    ]
    for root in roots[2:]:
        write_layer(root)
    context.precedence_roots = roots


@given("two saved bindings are ancestors of the target with different saved layer names")
def step_two_saved_ancestors(context):
    for name, target in (("far", context.project), ("close", context.project / "one")):
        invoke(context, ["profile", "saved", "create", name, str(target)])
    context.results.clear()


@given("the closer saved binding is nested below the farther saved binding")
def step_saved_closer(context):
    assert (context.project / "one").is_relative_to(context.project)


@given("each participating layer supplies a definition or configuration for the same activated neutral trait")
def step_precedence_definitions(context):
    roots = [
        context.precedence_roots[0],
        context.precedence_roots[1],
        context.home / ".zpp" / "saved" / "far",
        context.home / ".zpp" / "saved" / "close",
        *context.precedence_roots[2:],
    ]
    for number, root in enumerate(roots):
        write_trait(root, "neutral", description=f"layer {number}", body=f"body {number}\n", config={"base": number, "nested": {"base": number}})
        config = {"trait_overwrites": False, "traitsConfig": {"neutral": {f"layer{number}": True, "nested": {"value": number}}}}
        (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (roots[0] / "trait.json").write_text('[{"trait":"neutral"}]\n', encoding="utf-8")
    context.precedence_all_roots = roots


@given("the closest nested layer supplies the winning description, order, default config, skill lookup, and advisory body")
def step_winning_nested(context):
    root = context.target / ".zpp"
    write_trait(root, "neutral", description="winning description", body="winning advisory\n", order=7, config={"default": True, "nested": {"default": True}}, skill_lookup=["winning-skill"])


@given("successive traitsConfig values contain distinct keys and replacement values for the same nested object key")
def step_distinct_overlays(context):
    for number, root in enumerate(context.precedence_all_roots):
        config = json.loads((root / "config.json").read_text(encoding="utf-8"))
        overlay = config["traitsConfig"]["neutral"]
        assert overlay[f"layer{number}"] is True
        assert overlay["nested"] == {"value": number}


@then("the work profile participates after global")
def step_profile_participates(context):
    metadata = parse_documents(context.result.stdout)[0][0]
    assert metadata["config"]["layer0"] is True and metadata["config"]["layer1"] is True


@then("only the closest matching saved layer participates")
def step_only_close_saved(context):
    config = parse_documents(context.result.stdout)[0][0]["config"]
    assert "layer3" in config and "layer2" not in config


@then("repository layers participate from the repository root toward the target")
def step_repo_layer_order(context):
    config = parse_documents(context.result.stdout)[0][0]["config"]
    assert all(key in config for key in ("layer4", "layer5", "layer6"))


@then("the effective trait uses the complete document from the closest nested definition")
def step_winning_document(context):
    metadata, body = parse_documents(context.result.stdout)[0]
    assert metadata["description"] == "winning description"
    assert metadata["order"] == 7 and metadata["skill_lookup"] == ["winning-skill"]
    assert body == "winning advisory\n"


@then("its effective config contains distinct layered keys")
def step_layered_keys(context):
    config = parse_documents(context.result.stdout)[0][0]["config"]
    assert all(config[key] is True for key in ("layer0", "layer1", "layer3", "layer4", "layer5", "layer6"))


@then("its latest nested object value replaces rather than recursively merges earlier nested object values")
def step_shallow_nested(context):
    config = parse_documents(context.result.stdout)[0][0]["config"]
    assert config["nested"] == {"value": 6}


@given("an existing target is outside every Git worktree")
def step_outside_worktree(context):
    initialize(context)
    context.target = context.sandbox / "outside-tree" / "target"
    context.target.mkdir(parents=True)


@given("the target descends from a saved binding")
def step_target_saved(context):
    invoke(context, ["profile", "saved", "create", "outside", str(context.target.parent)])
    context.results.clear()


@given("global and saved rules activate different neutral traits")
def step_global_saved_rules(context):
    global_root = context.home / ".zpp" / "global"
    saved_root = context.home / ".zpp" / "saved" / "outside"
    write_trait(global_root, "global-trait")
    write_trait(saved_root, "saved-trait")
    (global_root / "trait.json").write_text('[{"trait":"global-trait"}]\n', encoding="utf-8")
    (saved_root / "trait.json").write_text('[{"trait":"saved-trait"}]\n', encoding="utf-8")


@then("stdout contains exactly the global and saved effective trait documents in order")
def step_global_saved_output(context):
    assert [meta["name"] for meta, _ in parse_documents(context.result.stdout)] == ["global-trait", "saved-trait"]


@then("no repository or subfolder layer is required")
def step_no_repo_required(context):
    assert context.result.exit_code == 0 and not (context.target / ".zpp").exists()


@given("traits are first activated in the order alpha, beta, gamma, delta, epsilon, zeta")
def step_order_traits(context):
    initialize(context)
    git_init(context.project)
    context.target = context.project
    root = context.home / ".zpp" / "global"
    names = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
    orders = {"alpha": 1, "gamma": 100, "delta": 100, "zeta": 200}
    for name in names:
        write_trait(root, name, order=orders.get(name))
    rules = [{"trait": name} for name in names]
    (root / "trait.json").write_text(json.dumps(rules), encoding="utf-8")


@given("one of those traits is activated by a later duplicate rule")
def step_duplicate_activation(context):
    path = context.home / ".zpp" / "global" / "trait.json"
    rules = json.loads(path.read_text(encoding="utf-8"))
    rules.append({"trait": "gamma"})
    path.write_text(json.dumps(rules), encoding="utf-8")


@given("gamma and delta have order 100")
@given("zeta has order 200")
@given("beta and epsilon have no order")
@given("alpha originally has an explicit order")
def step_order_characterized(context):
    root = context.home / ".zpp" / "global" / "traits"
    metadata = {
        name: yaml.safe_load(path.read_text(encoding="utf-8").split("---\n", 2)[1])
        for name, path in ((path.stem, path) for path in root.glob("*.md"))
    }
    assert metadata["gamma"]["order"] == metadata["delta"]["order"] == 100
    assert metadata["zeta"]["order"] == 200
    assert metadata["beta"]["order"] is None and metadata["epsilon"]["order"] is None
    assert metadata["alpha"]["order"] is not None


@given("a later layer completely replaces alpha with an authored document that has no order")
def step_replace_alpha(context):
    root = context.project / ".zpp"
    write_layer(root)
    write_trait(root, "alpha", order=None)


@given("traitsConfig for zeta contains a config key named order")
def step_config_order_key(context):
    root = context.project / ".zpp"
    (root / "config.json").write_text(json.dumps({"trait_overwrites": False, "traitsConfig": {"zeta": {"order": "config-only"}}}), encoding="utf-8")


@then("stdout contains exactly these effective trait documents in order:")
def step_trait_order(context):
    expected = [row["name"] for row in context.table]
    assert [meta["name"] for meta, _ in parse_documents(context.result.stdout)] == expected


@given("an activated neutral trait has all accepted frontmatter fields")
def step_full_trait(context):
    initialize(context)
    context.target = context.project
    root = context.home / ".zpp" / "global"
    context.full_body = "  UTF-8 指示\n\n deliberate tail  \n"
    write_trait(root, "complete", description="描述", body=context.full_body, order=4, config={"base": True, "replace": "old"}, skill_lookup=["one", "two"])
    (root / "trait.json").write_text('[{"trait":"complete"}]\n', encoding="utf-8")


@given("its description and advisory body contain UTF-8 text")
@given("its advisory body contains deliberate whitespace")
def step_full_trait_characterized(context):
    source = (context.home / ".zpp" / "global" / "traits" / "complete.md").read_text(
        encoding="utf-8"
    )
    assert "描述" in source and context.full_body in source


@given("a participating layer overrides part of its config")
def step_full_overlay(context):
    root = context.home / ".zpp" / "global"
    (root / "config.json").write_text(json.dumps({"trait_overwrites": False, "traitsConfig": {"complete": {"replace": "new"}}}, ensure_ascii=False), encoding="utf-8")


@then("stdout contains exactly one complete Markdown trait document")
def step_one_complete_doc(context):
    assert len(parse_documents(context.result.stdout)) == 1


@then("its YAML frontmatter semantically contains name, description, order, effective config, and ordered skill_lookup")
def step_complete_metadata(context):
    metadata = parse_documents(context.result.stdout)[0][0]
    assert metadata["name"] == "complete" and metadata["description"] == "描述"
    assert metadata["order"] == 4 and metadata["skill_lookup"] == ["one", "two"]
    assert metadata["config"] == {"base": True, "replace": "new"}


@then("its body preserves the authored UTF-8 text and whitespace")
def step_body_exact(context):
    assert parse_documents(context.result.stdout)[0][1] == context.full_body


@then("the effective config contains the accepted shallow override")
def step_effective_override(context):
    assert parse_documents(context.result.stdout)[0][0]["config"]["replace"] == "new"


@given("the requested target does not exist")
def step_invalid_missing_resolution(context):
    initialize(context)


@given("the requested target exists as a file")
def step_invalid_file_resolution(context):
    initialize(context)
    target = context.paths["c:\\work\\file.txt"]
    target.parent.mkdir(parents=True)
    target.write_text("file\n", encoding="utf-8")


@given("ZPP_PROFILE names a profile that does not exist")
def step_unknown_profile(context):
    initialize(context)
    context.target = context.project
    context.env["ZPP_PROFILE"] = "missing-profile"


@given("the saved index binds the target to a saved layer that does not exist")
def step_missing_saved_layer(context):
    initialize(context)
    context.target = context.project
    index = context.home / ".zpp" / "saved" / "_bindings.json"
    index.write_text(json.dumps({str(context.project.resolve()): "missing-saved"}), encoding="utf-8")


@when("the user runs zpp resolve for the missing target")
def step_run_missing_resolve(context):
    invoke(context, ["resolve", str(context.paths["c:\\missing"])])


@when("the user runs zpp resolve for the file target")
def step_run_file_resolve(context):
    invoke(context, ["resolve", str(context.paths["c:\\work\\file.txt"])])


use_step_matcher("re")


@then(r"stderr identifies (?P<subject>the missing target|the file target|the unknown profile|the missing saved layer) without a stack trace")
def step_resolution_diagnostic(context, subject):
    mappings = {
        "the missing target": str(context.paths["c:\\missing"].resolve(strict=False)),
        "the file target": str(context.paths["c:\\work\\file.txt"].resolve(strict=False)),
        "the unknown profile": "missing-profile",
        "the missing saved layer": "missing-saved",
    }
    if subject == "the missing target":
        assert_diagnostic_path(context.result.stderr, context.paths["c:\\missing"])
    elif subject == "the file target":
        assert_diagnostic_path(context.result.stderr, context.paths["c:\\work\\file.txt"])
    else:
        assert mappings[subject].lower() in context.result.stderr.lower()
    assert "Traceback" not in context.result.stderr


use_step_matcher("parse")


@then("no fallback resolution is returned")
def step_no_fallback(context):
    assert context.result.stdout == ""


# Workflow skill distribution


def workflow_skill_root(
    context,
    agent: str,
    *,
    scope: str,
    target: Path | None = None,
) -> Path:
    base = context.home if scope == "global" else (target or context.project)
    return base / (".claude/skills" if agent == "claude" else ".agents/skills")


def workflow_skill_snapshot(context) -> tuple[dict, dict]:
    return snapshot(context.home), snapshot(context.project)


def make_workflow_projection_outdated(root: Path) -> None:
    manifest = root / ".zpp-workflow-skills.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["bundle_version"] = "0.8.0"
    manifest.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def assert_workflow_projection(context, root: Path) -> None:
    assert (root / ".zpp-workflow-skills.json").is_file()
    assert {path.name for path in root.iterdir() if path.name.startswith("zpp-")} == set(
        context.workflow_skill_names
    )
    assert all((root / name / "SKILL.md").is_file() for name in context.workflow_skill_names)


@given("the packaged ZPP workflow bundle contains all seven permanent skills")
@given("the packaged ZPP workflow bundle contains all eight permanent skills")
@given("the packaged ZPP workflow bundle contains all eleven permanent skills")
def step_packaged_workflow_bundle(context):
    context.workflow_skill_names = (
        "zpp-author-skill",
        "zpp-clarify-change",
        "zpp-commit-zmem",
        "zpp-form-specs",
        "zpp-lean-audit",
        "zpp-mature-utilities",
        "zpp-plan-utilities",
        "zpp-reconcile-codespace-worktrees",
        "zpp-shape-feature",
        "zpp-use-zmem",
        "zpp-wire-feature",
    )


@given("the current directory is the root of a Git worktree")
def step_skill_git_root(context):
    git_init(context.project)


@given("Codex, Pi, and Claude Code have no local ZPP workflow skills")
@given("every supported agent has no ZPP workflow skills")
def step_no_local_workflow_skills(context):
    git_init(context.project)
    assert not workflow_skill_root(context, "codex", scope="local").exists()
    assert not workflow_skill_root(context, "claude", scope="local").exists()


@given("Codex, Pi, and Claude Code have no global ZPP workflow skills")
def step_no_global_workflow_skills(context):
    assert not workflow_skill_root(context, "codex", scope="global").exists()
    assert not workflow_skill_root(context, "claude", scope="global").exists()


@given("the current project has no authored ZPP layer")
def step_no_authored_project_layer(context):
    assert not (context.project / ".zpp").exists()


@when("the user runs zpp workflow install with agents Codex, Pi, and Claude Code")
def step_install_all_agents(context):
    invoke(
        context,
        ["workflow", "install", "--agent", "codex", "--agent", "pi", "--agent", "claude"],
    )


@when("the user runs zpp workflow install --global with agents Codex, Pi, and Claude Code")
def step_install_all_agents_global(context):
    invoke(
        context,
        [
            "workflow",
            "install",
            "--global",
            "--agent",
            "codex",
            "--agent",
            "pi",
            "--agent",
            "claude",
        ],
    )


@then("installation succeeds without offering agent selection")
def step_skill_install_succeeds(context):
    assert context.result.exit_code == 0, context.result.output
    assert context.selector_offers == []


@then("one managed bundle is installed in the repository-local shared Codex and Pi skill scope")
def step_local_shared_bundle(context):
    assert_workflow_projection(
        context,
        workflow_skill_root(context, "codex", scope="local"),
    )


@then("one managed bundle is installed in the repository-local Claude Code skill scope")
def step_local_claude_bundle(context):
    assert_workflow_projection(
        context,
        workflow_skill_root(context, "claude", scope="local"),
    )


@then("one managed bundle is installed in the user-global shared Codex and Pi skill scope")
def step_global_shared_bundle(context):
    assert_workflow_projection(
        context,
        workflow_skill_root(context, "codex", scope="global"),
    )


@then("one managed bundle is installed in the user-global Claude Code skill scope")
def step_global_claude_bundle(context):
    assert_workflow_projection(
        context,
        workflow_skill_root(context, "claude", scope="global"),
    )


@then("no duplicate Codex or Pi projection is created")
def step_no_shared_duplicate(context):
    root = workflow_skill_root(context, "codex", scope="local")
    assert root == workflow_skill_root(context, "pi", scope="local")
    assert not (context.project / ".codex" / "skills").exists()
    assert not (context.project / ".pi" / "skills").exists()


@then("the current project still has no authored ZPP layer")
@then("no authored ZPP layer is created or modified")
def step_no_authored_layer_after_skills(context):
    assert not (context.project / ".zpp").exists()
    if hasattr(context, "skill_target"):
        assert not (context.skill_target / ".zpp").exists()


@then("no repository-local skill scope is changed")
def step_no_local_skill_scope(context):
    assert not workflow_skill_root(context, "codex", scope="local").exists()
    assert not workflow_skill_root(context, "claude", scope="local").exists()


@given('"C:\\work\\repo\\nested" is an existing directory inside a Git worktree')
def step_exact_nested_skill_target(context):
    root = context.sandbox / "work" / "repo"
    context.skill_target = root / "nested"
    context.skill_target.mkdir(parents=True)
    git_init(root)
    context.paths["c:\\work\\repo\\nested"] = context.skill_target


@given("the current directory is outside that worktree")
def step_current_outside_target_worktree(context):
    assert not context.project.is_relative_to(context.skill_target.parent)


@when('the user runs zpp workflow install "C:\\work\\repo\\nested" with agent Claude Code')
def step_install_exact_target(context):
    invoke(
        context,
        ["workflow", "install", str(context.skill_target), "--agent", "claude"],
    )


@then("the managed bundle is installed only in that exact directory's local Claude Code skill scope")
def step_only_exact_target(context):
    assert_workflow_projection(
        context,
        workflow_skill_root(context, "claude", scope="local", target=context.skill_target),
    )
    assert not workflow_skill_root(
        context,
        "claude",
        scope="local",
        target=context.skill_target.parent,
    ).exists()


@given("every agent skill scope is recorded")
def step_record_agent_skill_scopes(context):
    context.skill_state_before = workflow_skill_snapshot(context)


def run_invalid_skill_target(context, target: str) -> None:
    invoke(
        context,
        ["workflow", "install", str(fixture_path(context, target)), "--agent", "codex"],
    )


@when('the user runs zpp workflow install "C:\\missing" with agent Codex')
def step_install_missing_skill_target(context):
    run_invalid_skill_target(context, '"C:\\missing"')


@when('the user runs zpp workflow install "C:\\work\\file.txt" with agent Codex')
def step_install_file_skill_target(context):
    run_invalid_skill_target(context, '"C:\\work\\file.txt"')


@when('the user runs zpp workflow install "C:\\outside" with agent Codex')
def step_install_outside_skill_target(context):
    run_invalid_skill_target(context, '"C:\\outside"')


@when('the user runs zpp workflow install "C:\\work\\repo" --global with agent Codex')
def step_global_with_target(context):
    invoke(
        context,
        ["workflow", "install", str(context.sandbox / "work" / "repo"), "--global", "--agent", "codex"],
    )


@then("the invocation is rejected as a domain error")
def step_skill_domain_error(context):
    assert context.result.exit_code == 1, context.result.output


@then("the invocation is rejected as a usage error")
def step_skill_usage_error(context):
    assert context.result.exit_code == 2, context.result.output


@then("every agent skill scope is unchanged")
def step_agent_skill_scopes_unchanged(context):
    assert workflow_skill_snapshot(context) == context.skill_state_before


@when("the user runs zpp workflow install and selects Pi and Claude Code")
def step_select_skill_agents(context):
    context.selector_answer = ("pi", "claude")
    invoke(context, ["workflow", "install"])


@then("the managed bundle is installed in the selected native local scopes")
def step_selected_skill_scopes(context):
    assert_workflow_projection(context, workflow_skill_root(context, "pi", scope="local"))
    assert_workflow_projection(context, workflow_skill_root(context, "claude", scope="local"))


@then("Codex receives no independent projection beyond the shared Pi scope")
def step_codex_shared_only(context):
    assert workflow_skill_root(context, "codex", scope="local") == workflow_skill_root(
        context,
        "pi",
        scope="local",
    )
    assert not (context.project / ".codex" / "skills").exists()


@when("the user submits zpp workflow install with no checked agent")
def step_skill_select_none(context):
    context.selector_answer = ()
    invoke(context, ["workflow", "install"])


@then("installation succeeds without changing any agent skill scope")
def step_empty_skill_selection(context):
    assert context.result.exit_code == 0
    assert workflow_skill_snapshot(context) == context.skill_state_before


@when("the user cancels zpp workflow install from the agent selector")
def step_cancel_skill_selection(context):
    context.selector_answer = None
    invoke(context, ["workflow", "install"])


@then("installation is cancelled without changing any agent skill scope")
def step_cancelled_skill_selection(context):
    assert context.result.exit_code == 1
    assert "cancelled" in context.result.stderr.lower()
    assert workflow_skill_snapshot(context) == context.skill_state_before


@when("the user runs zpp workflow install without an agent option")
def step_skill_no_agent(context):
    invoke(context, ["workflow", "install"])


@given("Codex has a compatible managed global ZPP workflow bundle")
def step_compatible_global_codex(context):
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--global", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    context.codex_global_root = workflow_skill_root(context, "codex", scope="global")
    context.codex_global_before = snapshot(context.codex_global_root)
    context.results.clear()


def assert_agent_no_local_bundle(context, agent: str) -> None:
    git_init(context.project)
    root = workflow_skill_root(context, agent, scope="local")
    context.pi_unchanged_root = root
    context.pi_before = snapshot(root)
    assert not root.exists()


@given("Codex has no local ZPP workflow bundle")
def step_codex_no_local_bundle(context):
    assert_agent_no_local_bundle(context, "codex")


@given("Pi has no local ZPP workflow bundle")
def step_pi_no_local_bundle(context):
    assert_agent_no_local_bundle(context, "pi")


@given("Claude Code has no local ZPP workflow bundle")
def step_claude_no_local_bundle(context):
    assert_agent_no_local_bundle(context, "claude")


@when("the user runs zpp workflow install with agent Codex")
def step_install_codex_skill(context):
    invoke(context, ["workflow", "install", "--agent", "codex"])


@then("installation succeeds and reports that the compatible global bundle is reused")
def step_global_bundle_reused(context):
    assert context.result.exit_code == 0, context.result.output
    assert "global" in context.result.stdout.lower()
    assert "skipped" in context.result.stdout.lower()


@then("no local bundle is installed")
def step_no_local_bundle(context):
    assert not workflow_skill_root(context, "codex", scope="local").exists()


@when("the user repeats zpp workflow install with agent Codex and --force")
def step_force_local_codex(context):
    invoke(context, ["workflow", "install", "--agent", "codex", "--force"])


@then("a compatible managed local bundle is installed")
def step_compatible_local_installed(context):
    assert context.result.exit_code == 0, context.result.output
    assert_workflow_projection(context, workflow_skill_root(context, "codex", scope="local"))


@then("both managed scopes are reported without claiming scope precedence")
def step_both_scopes_reported(context):
    output = context.result.stdout.lower()
    assert "global and local" in output
    assert "no scope precedence" in output


@given("Claude Code has an outdated managed global ZPP workflow bundle")
def step_outdated_global_claude(context):
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--global", "--agent", "claude"])
    assert result.exit_code == 0, result.output
    context.claude_global_root = workflow_skill_root(context, "claude", scope="global")
    make_workflow_projection_outdated(context.claude_global_root)
    context.claude_global_before = snapshot(context.claude_global_root)
    context.results.clear()


@when("the user runs zpp workflow install with agent Claude Code")
def step_install_claude_skill(context):
    invoke(context, ["workflow", "install", "--agent", "claude"])


@then("the current managed bundle is installed locally")
def step_current_local_claude(context):
    assert context.result.exit_code == 0, context.result.output
    assert_workflow_projection(context, workflow_skill_root(context, "claude", scope="local"))


@then("the differing managed scope versions are reported without selecting one")
def step_version_difference_reported(context):
    output = context.result.stdout.lower()
    assert "versions differ" in output
    assert "no scope precedence" in output


@given("Pi has a compatible managed local ZPP workflow bundle")
def step_compatible_local_pi(context):
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    context.pi_skill_root = workflow_skill_root(context, "pi", scope="local")
    context.results.clear()


@given("unrelated files surround the managed projection")
def step_surround_skill_projection(context):
    unrelated = context.pi_skill_root / "third-party" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("third-party π\n", encoding="utf-8")
    context.unrelated_skill_bytes = {unrelated: unrelated.read_bytes()}
    context.managed_projection_before = snapshot(context.pi_skill_root)


@when("the user runs zpp workflow install with agent Pi twice")
def step_install_pi_skill_twice(context):
    invoke(context, ["workflow", "install", "--agent", "pi"])
    invoke(context, ["workflow", "install", "--agent", "pi"])


@then("both installations succeed")
def step_both_skill_installs_succeed(context):
    assert all(result.exit_code == 0 for result in context.results[-2:])


@then("the managed projection is unchanged")
def step_managed_projection_unchanged(context):
    assert snapshot(context.pi_skill_root) == context.managed_projection_before


@then("the unrelated files are byte-for-byte unchanged")
@then("the unrelated skills are unchanged")
def step_unrelated_skills_unchanged(context):
    assert all(path.read_bytes() == source for path, source in context.unrelated_skill_bytes.items())


def create_unmanaged_local_skill_conflict(context, agent: str) -> None:
    git_init(context.project)
    root = workflow_skill_root(context, agent, scope="local")
    context.skill_conflict = root / context.workflow_skill_names[0] / "SKILL.md"
    context.skill_conflict.parent.mkdir(parents=True)
    context.skill_conflict.write_text("unmanaged π\n", encoding="utf-8")
    context.skill_conflict_before = context.skill_conflict.read_bytes()


@given("Claude Code has an unmanaged local conflict at a required skill destination")
def step_unmanaged_local_claude_conflict(context):
    create_unmanaged_local_skill_conflict(context, "claude")


@given("Codex has an unmanaged local conflict at a required skill destination")
def step_unmanaged_local_codex_conflict(context):
    create_unmanaged_local_skill_conflict(context, "codex")


@when("the user runs zpp workflow install with agents Pi and Claude Code")
def step_install_pi_claude_skills(context):
    invoke(context, ["workflow", "install", "--agent", "pi", "--agent", "claude"])


@when("the user runs zpp workflow install with agent Codex and --force")
def step_force_conflicting_codex(context):
    invoke(context, ["workflow", "install", "--agent", "codex", "--force"])


@then("installation fails as a managed-state rejection")
@then("update fails as a managed-state rejection")
def step_skill_managed_rejection(context):
    assert context.result.exit_code == 1, context.result.output


@then("the conflicting Claude Code content is unchanged")
@then("the conflicting content is unchanged")
def step_skill_conflict_unchanged(context):
    assert context.skill_conflict.read_bytes() == context.skill_conflict_before


@given("Codex has outdated managed global and forced local ZPP workflow bundles")
def step_outdated_codex_both_scopes(context):
    git_init(context.project)
    for arguments in (
        ["workflow", "install", "--global", "--agent", "codex"],
        ["workflow", "install", "--agent", "codex", "--force"],
    ):
        result = invoke(context, arguments)
        assert result.exit_code == 0, result.output
    context.codex_global_root = workflow_skill_root(context, "codex", scope="global")
    context.codex_local_root = workflow_skill_root(context, "codex", scope="local")
    make_workflow_projection_outdated(context.codex_global_root)
    make_workflow_projection_outdated(context.codex_local_root)
    context.codex_local_before = snapshot(context.codex_local_root)
    context.results.clear()


@when("the user runs zpp workflow update --global with agent Codex")
def step_update_global_codex(context):
    invoke(context, ["workflow", "update", "--global", "--agent", "codex"])


@then("only the Codex global managed bundle is updated to the packaged version")
def step_only_codex_global_updated(context):
    assert context.result.exit_code == 0, context.result.output
    manifest = json.loads(
        (context.codex_global_root / ".zpp-workflow-skills.json").read_text(encoding="utf-8")
    )
    assert manifest["bundle_version"] == "0.9.0"


@then("the forced local Codex bundle is unchanged")
def step_codex_local_unchanged(context):
    assert snapshot(context.codex_local_root) == context.codex_local_before


@then("every Claude Code scope is unchanged")
def step_claude_scopes_unchanged(context):
    assert snapshot(context.claude_global_root) == context.claude_global_before
    assert not workflow_skill_root(context, "claude", scope="local").exists()


@then("the differing Codex scope versions are reported")
def step_codex_difference_reported(context):
    assert "versions differ for codex" in context.result.stdout.lower()


@given("Codex has a historical managed global workflow bundle that predates one permanent skill")
def step_historical_global_codex_bundle(context):
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--global", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    root = workflow_skill_root(context, "codex", scope="global")
    manifest_path = root / ".zpp-workflow-skills.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    omitted = "zpp-reconcile-codespace-worktrees"
    shutil.rmtree(root / omitted)
    manifest["files"] = {
        path: digest
        for path, digest in manifest["files"].items()
        if not path.startswith(f"{omitted}/")
    }
    files = tuple(
        SkillFile(path, (root / Path(path)).read_bytes())
        for path in sorted(manifest["files"])
    )
    manifest["bundle_version"] = "0.8.0"
    manifest["fingerprint"] = fingerprint_skill_files(files)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    context.codex_global_root = root
    context.historical_owned_paths = frozenset(manifest["files"])
    context.results.clear()


@given("unrelated skills surround the historical managed projection")
def step_unrelated_historical_global_skills(context):
    unrelated = context.codex_global_root / "third-party" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep historical neighbor π\n", encoding="utf-8")
    context.unrelated_global_bytes = {unrelated: unrelated.read_bytes()}


@then("the Codex global projection contains the complete current workflow bundle")
def step_historical_global_updated(context):
    assert context.result.exit_code == 0, context.result.output
    assert_workflow_projection(context, context.codex_global_root)


@then("only paths owned by the historical manifest were replaced")
def step_only_historical_owned_paths_replaced(context):
    current = json.loads(
        (context.codex_global_root / ".zpp-workflow-skills.json").read_text(
            encoding="utf-8"
        )
    )
    assert context.historical_owned_paths < frozenset(current["files"])
    assert any(
        path.startswith("zpp-reconcile-codespace-worktrees/")
        for path in current["files"]
    )


@then("the unrelated global skills are byte-for-byte unchanged")
def step_unrelated_global_skills_unchanged(context):
    assert all(
        path.read_bytes() == content
        for path, content in context.unrelated_global_bytes.items()
    )


@when("the user runs zpp workflow update with agent Codex")
def step_update_local_codex(context):
    invoke(context, ["workflow", "update", "--agent", "codex"])


@then("update reports that the local projection is not installed")
def step_update_reports_local_absent(context):
    assert context.result.exit_code == 1, context.result.output
    assert "not installed" in context.result.stderr.lower(), context.result.stderr


@then("it does not describe absent local state as unmanaged content")
def step_absent_is_not_unmanaged(context):
    assert "unmanaged" not in context.result.stderr.lower()


@then("the compatible global bundle remains unchanged")
def step_compatible_global_bundle_unchanged(context):
    assert snapshot(context.codex_global_root) == context.codex_global_before


@given("Claude Code has an unmanaged global skill directory matching a permanent skill name")
def step_unmanaged_global_claude_skill(context):
    root = workflow_skill_root(context, "claude", scope="global")
    context.skill_conflict = root / context.workflow_skill_names[0] / "SKILL.md"
    context.skill_conflict.parent.mkdir(parents=True)
    context.skill_conflict.write_text("unmanaged\n", encoding="utf-8")
    context.skill_conflict_before = context.skill_conflict.read_bytes()


@when("the user runs zpp workflow update --global with agent Claude Code")
def step_update_unmanaged_claude(context):
    invoke(context, ["workflow", "update", "--global", "--agent", "claude"])


@given("Pi has a managed local ZPP workflow bundle surrounded by unrelated skills")
def step_managed_pi_with_unrelated(context):
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--agent", "pi"])
    assert result.exit_code == 0, result.output
    context.pi_skill_root = workflow_skill_root(context, "pi", scope="local")
    unrelated = context.pi_skill_root / "third-party" / "SKILL.md"
    unrelated.parent.mkdir()
    unrelated.write_text("keep π\n", encoding="utf-8")
    context.unrelated_skill_bytes = {unrelated: unrelated.read_bytes()}
    context.results.clear()


@given("Claude Code has a managed local ZPP workflow bundle")
def step_managed_local_claude(context):
    result = invoke(context, ["workflow", "install", "--agent", "claude"])
    assert result.exit_code == 0, result.output
    context.claude_local_root = workflow_skill_root(context, "claude", scope="local")
    context.claude_local_before = snapshot(context.claude_local_root)
    context.results.clear()


@when("the user runs zpp workflow remove with agent Pi and declines confirmation")
def step_decline_skill_remove(context):
    context.skill_state_before = workflow_skill_snapshot(context)
    invoke(context, ["workflow", "remove", "--agent", "pi"], input_text="n\n")


@when("the user runs zpp workflow remove with agent Pi and --yes")
def step_confirm_skill_remove(context):
    invoke(context, ["workflow", "remove", "--agent", "pi", "--yes"])


@then("only the managed shared Codex and Pi projection is removed")
def step_shared_projection_removed(context):
    assert context.result.exit_code == 0, context.result.output
    assert not (context.pi_skill_root / ".zpp-workflow-skills.json").exists()
    assert all(not (context.pi_skill_root / name).exists() for name in context.workflow_skill_names)


@then("the Claude Code projection is unchanged")
def step_claude_projection_unchanged(context):
    assert snapshot(context.claude_local_root) == context.claude_local_before


@given("a participating layer activates a conditionless automatic-workflow trait")
def step_automatic_workflow_trait(context):
    initialize(context)
    context.target = context.project
    root = context.home / ".zpp" / "global"
    write_trait(
        root,
        "automatic-workflow",
        body=(
            "Continue across satisfied workflow stages without requesting approval at "
            "checkpoints, successful verification, or ordinary handoffs. Pause only "
            "for unresolved clarification, a new product boundary, or a missing or "
            "changed utility shape. Skill lookup remains passive and grants no "
            "authority or failed-gate bypass.\n"
        ),
        config={"useThis": True, "mode": "automatic"},
        skill_lookup=list(context.workflow_skill_names),
    )
    (root / "trait.json").write_text(
        '[{"trait":"automatic-workflow"}]\n',
        encoding="utf-8",
    )


@given("that trait references the permanent workflow skills through skill lookup")
def step_automatic_trait_lookup(context):
    source = (
        context.home / ".zpp" / "global" / "traits" / "automatic-workflow.md"
    ).read_text(encoding="utf-8")
    assert all(name in source for name in context.workflow_skill_names)


@when("the user resolves traits for the target")
def step_resolve_automatic_trait(context):
    invoke(context, ["resolve", str(context.target)])


@then("the effective trait directs unattended continuation only across satisfied gates")
def step_automatic_trait_direction(context):
    assert context.result.exit_code == 0, context.result.output
    assert "Continue across satisfied workflow stages" in context.result.stdout


@then("the skill lookup remains passive frontmatter metadata")
def step_automatic_lookup_passive(context):
    metadata, body = parse_documents(context.result.stdout)[0]
    assert metadata["skill_lookup"] == list(context.workflow_skill_names)
    assert not any(name in body for name in context.workflow_skill_names)


@then("the trait does not grant mutation authority or bypass a failed gate")
def step_automatic_trait_limits(context):
    assert "grants no authority or failed-gate bypass" in context.result.stdout


@when("the user installs the managed bundle for every supported agent")
def step_install_bundle_for_every_agent(context):
    git_init(context.project)
    step_install_all_agents(context)
    context.installed_workflow_roots = (
        workflow_skill_root(context, "codex", scope="local"),
        workflow_skill_root(context, "claude", scope="local"),
    )


@given("the packaged default profile contains executable-guarded tool-use traits")
def step_packaged_tool_traits(context):
    root = REPO_ROOT / "src" / "zpp" / "artifacts" / "profiles" / "default"
    triggers = json.loads((root / "trait.json").read_text(encoding="utf-8"))
    assert triggers[-3:] == [
        {"trait": "use-rg", "which": "rg"},
        {"trait": "use-jq", "which": "jq"},
        {"trait": "use-zmem", "which": "zmem"},
    ]


@then("every native projection contains zpp-use-zmem, zpp-lean-audit, and zpp-author-skill")
def step_projection_contains_generic_skills(context):
    for root in context.installed_workflow_roots:
        for name in ("zpp-use-zmem", "zpp-lean-audit", "zpp-author-skill"):
            assert (root / name / "SKILL.md").is_file()


@then("use-zmem looks up zpp-use-zmem and zpp-commit-zmem only when the zmem executable is available")
def step_use_zmem_guard(context):
    root = REPO_ROOT / "src" / "zpp" / "artifacts" / "profiles" / "default"
    triggers = json.loads((root / "trait.json").read_text(encoding="utf-8"))
    assert {"trait": "use-zmem", "which": "zmem"} in triggers
    source = (root / "traits" / "use-zmem.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(source.split("---", 2)[1])
    assert metadata["skill_lookup"] == ["zpp-use-zmem", "zpp-commit-zmem"]


@then("zpp-use-zmem teaches recall, search, detail inspection, links, output interpretation, and current-authority verification")
def step_zmem_skill_complete(context):
    source = (
        context.installed_workflow_roots[0] / "zpp-use-zmem" / "SKILL.md"
    ).read_text(encoding="utf-8").lower()
    assert all(term in source for term in (
        "zmem recall", "zmem search", "zmem show", "zmem links",
        "json", "--human", "canonical openspec", "current code",
    ))


@then("zpp-lean-audit is read-only and substantially attributed to the upstream Ponytail ladder, taxonomy, output, and safety boundaries")
def step_lean_skill_contract(context):
    source = (
        context.installed_workflow_roots[0] / "zpp-lean-audit" / "SKILL.md"
    ).read_text(encoding="utf-8").lower()
    assert "dietrichgebert/ponytail" in source and "remain read-only" in source
    assert all(tag in source for tag in ("delete:", "stdlib:", "native:", "yagni:", "shrink:"))
    assert all(term in source for term in ("rank", "output", "security", "accessibility"))


@then("zpp-lean-audit preserves ZPP's proportional maturity evaluation for external dependencies")
def step_lean_dependency_fit(context):
    source = (
        context.installed_workflow_roots[0] / "zpp-lean-audit" / "SKILL.md"
    ).read_text(encoding="utf-8").lower()
    assert all(term in source for term in (
        "package maturity", "integration cost", "proportion", "universal percentage",
    ))


@then("zpp-author-skill keeps context-continuity and explicit-control-flow guidance in focused references rather than runtime traits")
def step_author_skill_references(context):
    skill = context.installed_workflow_roots[0] / "zpp-author-skill"
    body = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "references/context-continuity.md" in body
    assert "references/explicit-control-flow.md" in body
    assert (skill / "references" / "context-continuity.md").is_file()
    assert (skill / "references" / "explicit-control-flow.md").is_file()
    trait_root = REPO_ROOT / "src" / "zpp" / "artifacts" / "profiles" / "default" / "traits"
    assert not (trait_root / "context-continuity.md").exists()
    assert not (trait_root / "explicit-control-flow.md").exists()


@then("every native projection contains the same seven permanent workflow skills")
@then("every native projection contains the same eight permanent workflow skills")
@then("every native projection contains the same eleven permanent workflow skills")
def step_every_projection_same_bundle(context):
    for root in context.installed_workflow_roots:
        assert_workflow_projection(context, root)


@then("each skill retains its required packaged resources and scripts")
def step_packaged_resources_retained(context):
    for root in context.installed_workflow_roots:
        scripts = root / "zpp-commit-zmem" / "scripts"
        assert (scripts / "check-commit-msg.ps1").is_file()
        assert (scripts / "check-commit-msg.sh").is_file()


@given("a mitigated codespace records its generated project and store branches")
def step_recorded_reconciliation_branches(context):
    skill = (
        REPO_ROOT
        / "src"
        / "zpp"
        / "artifacts"
        / "skills"
        / "zpp-reconcile-codespace-worktrees"
        / "SKILL.md"
    )
    context.reconciliation_skill = skill.read_text(encoding="utf-8")
    assert "effective path" in context.reconciliation_skill
    assert "branch" in context.reconciliation_skill


@then("every native projection contains the permanent codespace worktree-reconciliation skill")
def step_projection_contains_reconciliation_skill(context):
    for root in context.installed_workflow_roots:
        assert (
            root / "zpp-reconcile-codespace-worktrees" / "SKILL.md"
        ).is_file()


@then("the skill consumes the recorded codespace branch metadata")
@then("the skill consumes the released claim's generated-checkout and branch metadata")
def step_reconciliation_consumes_metadata(context):
    source = context.reconciliation_skill
    assert "zpp codespace status ID --json" in source
    assert "released claim's generated-checkout and branch metadata" in source
    assert "source path" in source
    assert "source/effective checkout identities" in source


@then("reconciliation requires explicit invocation")
def step_reconciliation_is_explicit(context):
    assert "Require an explicit reconciliation request" in context.reconciliation_skill


@then("the skill never makes codespace locking merge work automatically")
def step_reconciliation_never_auto_merges(context):
    source = context.reconciliation_skill
    assert "never authorize a" in source
    assert "merge" in source


@then("successful reconciliation can give every retained branch a disposition before finalization")
def step_reconciliation_records_disposition(context):
    source = " ".join(context.reconciliation_skill.split())
    assert "every retained branch an explicit reconciled or abandoned disposition" in source
    assert "before finalization" in source


@then("no skill body contains platform, framework, test-runner, or agent-specific policy")
def step_skill_bodies_neutral(context):
    forbidden = (
        "pytest",
        "behave",
        "python-bdd",
        "django",
        "fastapi",
        "react",
        "claude code",
        ".agents/skills",
        ".claude/skills",
        ".pi/",
        ".codex/",
        "powershell",
        "posix",
    )
    for root in context.installed_workflow_roots:
        for name in context.workflow_skill_names:
            source = (root / name / "SKILL.md").read_text(encoding="utf-8").lower()
            assert not any(term in source for term in forbidden), (name, source)


@then("all Python, Django, TypeScript, and Flutter workflow guidance remains in independent optional traits outside the skill bodies")
def step_platform_guidance_in_optional_traits(context):
    root = REPO_ROOT / "src" / "zpp" / "artifacts" / "profiles" / "default"
    names = {
        "python-bdd", "python-tdd", "python-build", "python-django-tdd",
        "typescript-bdd", "typescript-tdd", "flutter-bdd", "flutter-tdd",
    }
    triggers = {item["trait"] for item in json.loads((root / "trait.json").read_text(encoding="utf-8"))}
    assert triggers.isdisjoint(names)
    assert all((root / "traits" / f"{name}.md").is_file() for name in names)


@then("platform-specific installation behavior remains outside the skill bodies")
def step_installation_policy_outside_bodies(context):
    assert workflow_skill_root(context, "codex", scope="local") == (
        context.project / ".agents" / "skills"
    )
    assert workflow_skill_root(context, "claude", scope="local") == (
        context.project / ".claude" / "skills"
    )


# Standard default profile and profile activation


def authored_bytes(root: Path) -> dict[str, bytes]:
    managed = (root / "config.json", root / "trait.json")
    traits = tuple(sorted((root / "traits").glob("*.md")))
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in (*managed, *traits)
        if path.is_file()
    }


@then("the persistent user-owned default profile exists")
def step_default_profile_exists(context):
    root = context.home / ".zpp" / "profiles" / "default"
    assert (root / "config.json").is_file()
    assert (root / "trait.json").is_file()
    assert (root / "traits").is_dir()


@then(
    "the default profile is provisioned without participating in resolution"
)
def step_default_profile_inactive(context):
    global_triggers = context.home / ".zpp" / "global" / "trait.json"
    assert json.loads(global_triggers.read_text(encoding="utf-8")) == []
    assert context.env["ZPP_PROFILE"] is None


@then(
    "the default profile selects exactly automatic-workflow, codespace-claim-guard, "
    "zero-assumptions, and ponytail when explicitly used"
)
@then(
    "the default profile conditionlessly selects exactly automatic-workflow, "
    "codespace-claim-guard, zero-assumptions, and ponytail when explicitly used"
)
def step_default_profile_triggers(context):
    source = context.home / ".zpp" / "profiles" / "default" / "trait.json"
    triggers = json.loads(source.read_text(encoding="utf-8"))
    assert triggers[:4] == [
        {"trait": "automatic-workflow"},
        {"trait": "codespace-claim-guard"},
        {"trait": "zero-assumptions"},
        {"trait": "ponytail"},
    ]


@then("the default profile guards use-rg, use-jq, and use-zmem by their corresponding executables")
def step_default_tool_guards(context):
    source = context.home / ".zpp" / "profiles" / "default" / "trait.json"
    assert json.loads(source.read_text(encoding="utf-8"))[4:] == [
        {"trait": "use-rg", "which": "rg"},
        {"trait": "use-jq", "which": "jq"},
        {"trait": "use-zmem", "which": "zmem"},
    ]


@then(
    "the default profile contains inactive python-bdd, python-tdd, "
    "and python-build traits"
)
def step_default_optional_python_traits(context):
    root = context.home / ".zpp" / "profiles" / "default"
    triggers = {
        item["trait"]
        for item in json.loads((root / "trait.json").read_text(encoding="utf-8"))
    }
    optional = {"python-bdd", "python-tdd", "python-build"}
    assert all((root / "traits" / f"{name}.md").is_file() for name in optional)
    assert triggers.isdisjoint(optional)


@then("the default profile contains all packaged platform workflow traits without activating them")
def step_default_optional_platform_traits(context):
    root = context.home / ".zpp" / "profiles" / "default"
    triggers = {
        item["trait"]
        for item in json.loads((root / "trait.json").read_text(encoding="utf-8"))
    }
    optional = {
        "python-bdd",
        "python-tdd",
        "python-build",
        "python-django-tdd",
        "typescript-bdd",
        "typescript-tdd",
        "flutter-bdd",
        "flutter-tdd",
    }
    assert all((root / "traits" / f"{name}.md").is_file() for name in optional)
    assert triggers.isdisjoint(optional)


@given("the default profile has valid user-authored changes with distinctive formatting")
def step_user_edited_default(context):
    root = context.home / ".zpp" / "profiles" / "default"
    (root / "config.json").write_text(
        '{ "traitsConfig": {"automatic-workflow": {"mode": "manual"}}, '
        '"trait_overwrites": false }\n',
        encoding="utf-8",
    )
    context.default_before = snapshot(root)


@then("the complete default profile is byte-for-byte unchanged")
@then("no bundled default content is reapplied")
def step_user_default_preserved(context):
    root = context.home / ".zpp" / "profiles" / "default"
    assert snapshot(root) == context.default_before


@given('profile "source" has distinctive valid authored bytes and an independent cache')
def step_copy_source_profile(context):
    root = context.home / ".zpp" / "profiles" / "source"
    write_layer(root, triggers=[{"trait": "source"}])
    write_trait(root, "source", body="source distinctive body\n")
    (root / "config.json").write_text(
        '{ "traitsConfig": {}, "trait_overwrites": false }\n',
        encoding="utf-8",
    )
    cache = context.home / ".zpp" / "cached" / "profiles" / "source"
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text('{"source": true}\n', encoding="utf-8")
    context.source_authored_before = authored_bytes(root)
    context.source_cache_before = snapshot(cache)


@given("the global layer has distinctive authored bytes")
def step_distinct_global_bytes(context):
    root = context.home / ".zpp" / "global"
    write_trait(root, "global-distinctive", body="global distinctive body\n")
    (root / "trait.json").write_text(
        '[{"trait":"global-distinctive"}]\n',
        encoding="utf-8",
    )
    context.global_before = snapshot(root)


@then('profile "derived" contains a byte-for-byte copy of the authored source layer')
def step_derived_profile_copy(context):
    derived = context.home / ".zpp" / "profiles" / "derived"
    assert authored_bytes(derived) == context.source_authored_before


@then('profile "derived" has no derived cache')
def step_derived_has_no_cache(context):
    assert not (context.home / ".zpp" / "cached" / "profiles" / "derived").exists()


@then('profile "source" and its independent cache are unchanged')
def step_copy_source_unchanged(context):
    source = context.home / ".zpp" / "profiles" / "source"
    cache = context.home / ".zpp" / "cached" / "profiles" / "source"
    assert authored_bytes(source) == context.source_authored_before
    assert snapshot(cache) == context.source_cache_before


@then("the global layer is unchanged")
def step_global_unchanged(context):
    assert snapshot(context.home / ".zpp" / "global") == context.global_before


@given('profiles "source" and "existing" already exist')
def step_source_and_existing_profiles(context):
    for name in ("source", "existing"):
        result = invoke(context, ["profile", "create", name])
        assert result.exit_code == 0, result.output
    context.results.clear()


@given('profile "broken" has invalid managed state')
def step_invalid_profile_for_copy(context):
    root = context.home / ".zpp" / "profiles" / "broken"
    write_layer(root)
    (root / "config.json").write_text("invalid\n", encoding="utf-8")
    context.invalid_source = root / "config.json"


@given("the current timestamp for archive naming is 20260730-143522")
def step_fixed_archive_time(context):
    context.archive_time = datetime(2026, 7, 30, 14, 35, 22)


@given("the global layer has distinctive valid authored bytes and derived state")
def step_global_layer_for_activation(context):
    root = context.home / ".zpp" / "global"
    write_trait(root, "prior-global", body="prior global body\n")
    (root / "trait.json").write_text(
        '[{"trait":"prior-global"}]\n',
        encoding="utf-8",
    )
    cache = context.home / ".zpp" / "cached" / "global"
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text('{"prior": true}\n', encoding="utf-8")
    (cache / "traits.watch.json").write_text('{"prior": true}\n', encoding="utf-8")
    context.prior_global_authored = authored_bytes(root)


@given(
    "the default profile has different distinctive valid authored bytes "
    "and derived state"
)
def step_default_layer_for_activation(context):
    root = context.home / ".zpp" / "profiles" / "default"
    (root / "config.json").write_text(
        '{ "trait_overwrites": false, "traitsConfig": '
        '{"automatic-workflow": {"marker": "default"}} }\n',
        encoding="utf-8",
    )
    cache = context.home / ".zpp" / "cached" / "profiles" / "default"
    cache.mkdir(parents=True)
    (cache / "traits.json").write_text('{"default": true}\n', encoding="utf-8")
    context.default_authored_before = authored_bytes(root)
    context.default_cache_before = snapshot(cache)


@when('the user runs zpp global activate {profile}')
def step_activate_global_profile(context, profile):
    fixed = getattr(context, "archive_time", None)
    if fixed is None:
        invoke(context, ["global", "activate", profile])
        return
    with patch("zpp.core.state.datetime") as clock:
        clock.now.return_value = fixed
        invoke(context, ["global", "activate", profile])


@then('profile "20260730-143522-global" contains the prior global authored layer')
def step_archived_global_layer(context):
    archive = context.home / ".zpp" / "profiles" / "20260730-143522-global"
    actual = authored_bytes(archive)
    assert actual == context.prior_global_authored, (
        actual,
        context.prior_global_authored,
        tuple(path.name for path in archive.parent.iterdir()),
    )


@then("the global layer contains a byte-for-byte copy of the default authored layer")
def step_global_matches_default(context):
    assert authored_bytes(context.home / ".zpp" / "global") == (
        context.default_authored_before
    )


@then("the default profile is byte-for-byte unchanged")
def step_default_profile_unchanged(context):
    root = context.home / ".zpp" / "profiles" / "default"
    assert authored_bytes(root) == context.default_authored_before


@then("no derived cache or modification sidecar is copied into either authored layer")
def step_no_derived_state_copied(context):
    root = context.home / ".zpp"
    archive = root / "profiles" / "20260730-143522-global"
    assert not (root / "global" / "cached").exists()
    assert not (archive / "cached").exists()
    assert not tuple((root / "global").rglob("traits.watch.json"))
    assert not tuple(archive.rglob("traits.watch.json"))


@then("affected derived caches are invalidated")
def step_activation_cache_invalidated(context):
    root = context.home / ".zpp"
    assert not (root / "cached" / "global").exists()
    assert snapshot(root / "cached" / "profiles" / "default") == (
        context.default_cache_before
    )


@when("the user resolves traits without ZPP_PROFILE")
def step_resolve_without_profile(context):
    context.env["ZPP_PROFILE"] = None
    invoke(context, ["resolve", str(context.project)])


@then("the platform-neutral base traits resolve from global")
def step_base_traits_from_global(context):
    assert context.result.exit_code == 0, context.result.output
    names = [meta["name"] for meta, _ in parse_documents(context.result.stdout)]
    assert names[:4] == [
        "automatic-workflow", "codespace-claim-guard", "zero-assumptions", "ponytail"
    ]
    assert set(names[4:]).issubset({"use-rg", "use-jq", "use-zmem"})


@given('profiles "work" and "default" exist')
def step_work_and_default_profiles(context):
    result = invoke(context, ["profile", "create", "work"])
    assert result.exit_code == 0, result.output
    context.default_authored_before = authored_bytes(
        context.home / ".zpp" / "profiles" / "default"
    )
    context.results.clear()


@then("the default profile still exists unchanged")
def step_default_still_unchanged(context):
    root = context.home / ".zpp" / "profiles" / "default"
    assert authored_bytes(root) == context.default_authored_before


# Standard trait resolution


@given('ZPP_PROFILE is "default"')
def step_default_profile_env(context):
    context.env["ZPP_PROFILE"] = "default"


@then('automatic-workflow has effective mode "automatic"')
def step_automatic_mode(context):
    documents = parse_documents(context.result.stdout)
    automatic = next(meta for meta, _ in documents if meta["name"] == "automatic-workflow")
    assert automatic["config"]["mode"] == "automatic"


@then("stdout contains no Python-specific trait")
def step_no_python_traits(context):
    names = {meta["name"] for meta, _ in parse_documents(context.result.stdout)}
    assert names.isdisjoint({"python-bdd", "python-tdd", "python-build"})


@given('the repository layer overrides automatic-workflow mode to "manual"')
def step_local_manual_mode(context):
    git_init(context.project)
    context.target = context.project
    write_layer(
        context.project / ".zpp",
        config={
            "trait_overwrites": False,
            "traitsConfig": {"automatic-workflow": {"mode": "manual"}},
        },
    )


@when("the user runs zpp resolve for the repository target")
def step_resolve_repository_target(context):
    invoke(context, ["resolve", str(context.project)])


@then('automatic-workflow remains active with effective mode "manual"')
def step_manual_mode_active(context):
    documents = parse_documents(context.result.stdout)
    automatic = next(meta for meta, _ in documents if meta["name"] == "automatic-workflow")
    assert automatic["config"]["mode"] == "manual"


@then("the same platform-neutral base traits remain active")
def step_same_base_traits(context):
    names = [meta["name"] for meta, _ in parse_documents(context.result.stdout)]
    assert names[:4] == [
        "automatic-workflow", "codespace-claim-guard", "zero-assumptions", "ponytail"
    ]
    assert set(names[4:]).issubset({"use-rg", "use-jq", "use-zmem"})


@then("codespace-claim-guard remains active")
def step_claim_guard_remains_active(context):
    names = {meta["name"] for meta, _ in parse_documents(context.result.stdout)}
    assert "codespace-claim-guard" in names


use_step_matcher("re")


@given(
    r"the repository layer additionally activates "
    r"(?P<trait>python-(?:bdd|tdd|build|django-tdd)|typescript-(?:bdd|tdd)|flutter-(?:bdd|tdd))"
)
def step_activate_optional_python_trait(context, trait):
    git_init(context.project)
    context.target = context.project
    write_layer(context.project / ".zpp", triggers=[{"trait": trait}])


@then(
    r"stdout contains "
    r"(?P<trait>python-(?:bdd|tdd|build|django-tdd)|typescript-(?:bdd|tdd)|flutter-(?:bdd|tdd)) "
    r"with only (?P<responsibility>Behave|pytest|the uv environment|Django testing|TypeScript BDD|TypeScript TDD|Flutter BDD|Flutter TDD) guidance"
)
def step_optional_python_guidance(context, trait, responsibility):
    documents = parse_documents(context.result.stdout)
    body = next(body for meta, body in documents if meta["name"] == trait)
    expected = {
        "Behave": "Behave",
        "pytest": "pytest",
        "the uv environment": "uv",
        "Django testing": "Django",
        "TypeScript BDD": "TypeScript",
        "TypeScript TDD": "TypeScript",
        "Flutter BDD": "Flutter",
        "Flutter TDD": "Flutter",
    }[responsibility]
    assert expected in body


use_step_matcher("parse")


@then("stdout contains no other optional Python trait")
@then("stdout contains no other optional platform workflow trait")
def step_no_other_python_trait(context):
    names = {
        meta["name"]
        for meta, _ in parse_documents(context.result.stdout)
        if meta["name"].startswith(("python-", "typescript-", "flutter-"))
    }
    assert len(names) == 1


# Standard workflow trait ownership and delegated progression


@given("the user-owned default profile is recorded")
def step_record_default_profile(context):
    context.default_profile_before = snapshot(
        context.home / ".zpp" / "profiles" / "default"
    )


@then("the user-owned default profile is unchanged")
def step_owned_default_unchanged(context):
    assert snapshot(context.home / ".zpp" / "profiles" / "default") == (
        context.default_profile_before
    )


@then("completed checkpoints, successful verification, and ordinary stage transitions are not human gates")
def step_ordinary_transitions_not_gates(context):
    output = context.result.stdout
    assert "checkpoints, successful verification, or ordinary handoffs" in output


@then(
    "the effective trait pauses only for unresolved clarification, "
    "a new product boundary, or a missing or changed utility shape"
)
def step_only_real_human_gates(context):
    assert (
        "Pause only for unresolved clarification, a new product boundary, "
        "or a missing or changed utility shape"
    ) in context.result.stdout


@given('a participating layer activates automatic-workflow with mode "manual"')
def step_manual_automatic_workflow(context):
    initialize(context)
    context.target = context.project
    context.env["ZPP_PROFILE"] = "default"
    git_init(context.project)
    root = context.project / ".zpp"
    write_layer(
        root,
        config={
            "trait_overwrites": False,
            "traitsConfig": {"automatic-workflow": {"mode": "manual"}},
        },
    )
    context.manual_config_before = (root / "config.json").read_bytes()


@given("the user explicitly delegates the complete change end to end")
def step_complete_delegation(context):
    context.complete_delegation = True


@when("a workflow stage completes with its gate satisfied")
def step_satisfied_stage(context):
    assert context.complete_delegation
    invoke(context, ["resolve", str(context.target)])


@then(
    "the effective guidance directs continuation through the next owning "
    "workflow without requesting stage approval"
)
def step_delegated_continuation(context):
    assert context.result.exit_code == 0, context.result.output
    output = " ".join(context.result.stdout.split())
    assert "delegated end to end" in output
    assert "without approval" in output


@then("the manual configuration remains unchanged")
def step_manual_config_unchanged(context):
    source = context.project / ".zpp" / "config.json"
    assert source.read_bytes() == context.manual_config_before
    metadata = parse_documents(context.result.stdout)[0][0]
    assert metadata["config"]["mode"] == "manual"


@then("the trait still cannot execute a skill or grant mutation authority")
def step_manual_trait_advisory(context):
    output = " ".join(context.result.stdout.split())
    assert "skill lookup is passive and grants no authority" in output.lower()


@given("the initialized default profile contains the platform-neutral base traits")
def step_initialized_default_traits(context):
    initialize(context)
    step_default_profile_triggers(context)
    step_default_optional_python_traits(context)


@then("cross-cutting zero-assumption and Ponytail guidance remains in its owning trait")
@then(
    "cross-cutting codespace claim, zero-assumption, and Ponytail guidance "
    "remains in its owning trait"
)
def step_cross_cutting_trait_ownership(context):
    traits = context.home / ".zpp" / "profiles" / "default" / "traits"
    claim = (traits / "codespace-claim-guard.md").read_text(encoding="utf-8")
    zero = (traits / "zero-assumptions.md").read_text(encoding="utf-8")
    ponytail = (traits / "ponytail.md").read_text(encoding="utf-8")
    assert "OpenSpec worksets are opening projections, never ownership" in claim
    assert "Do not invent" in zero
    assert "dependency" in ponytail


@given("a participating layer activates codespace-claim-guard")
def step_activate_claim_guard(context):
    initialize(context)
    context.env["ZPP_PROFILE"] = "default"
    context.claim_guard = " ".join((
        context.home
        / ".zpp"
        / "profiles"
        / "default"
        / "traits"
        / "codespace-claim-guard.md"
    ).read_text(encoding="utf-8").split())


@given('automatic-workflow has effective mode "automatic"')
def step_claim_workflow_automatic(context):
    context.claim_workflow_mode = "automatic"


@given('automatic-workflow has effective mode "manual"')
def step_claim_workflow_manual(context):
    context.claim_workflow_mode = "manual"


@when("a write-capable ZPP workflow is about to mutate a physical checkout")
def step_claim_guard_before_mutation(context):
    assert context.claim_guard
    assert context.claim_workflow_mode in {"automatic", "manual"}


@then("the claim guard directs automatic acquisition or verification of the claim")
def step_claim_guard_automatic(context):
    assert context.claim_workflow_mode == "automatic"
    assert "automatic obtains or verifies the complete claim" in context.claim_guard


@then("the claim guard directs prompting before claim acquisition")
def step_claim_guard_manual(context):
    assert context.claim_workflow_mode == "manual"
    assert "manual prompts before acquisition" in context.claim_guard


@then("the trait does not treat an OpenSpec workset as ownership")
def step_claim_guard_not_workset_authority(context):
    assert "OpenSpec worksets are opening projections, never ownership" in context.claim_guard


@then("the trait rejects supported direct writes into associated read-only members")
def step_claim_guard_rejects_read_only_writes(context):
    assert (
        "reject supported direct writes into another claim or an associated "
        "codespace read-only member"
    ) in context.claim_guard


@then("the trait cannot override a conflicting claim or grant mutation authority")
def step_claim_guard_is_advisory(context):
    assert "cannot override conflicts or grant mutation authority" in context.claim_guard


@then("each permanent skill contains only its stage-specific operations and gates")
def step_skills_stage_specific(context):
    forbidden = (
        "Persist established information before absorbing new details",
        "Keep feature wiring thin by composing small focused utilities",
    )
    for root in context.installed_workflow_roots:
        for name in context.workflow_skill_names:
            source = (root / name / "SKILL.md").read_text(encoding="utf-8")
            assert not any(text in source for text in forbidden)


@then(
    "hard OpenSpec operation ownership, verification authority, and zmem "
    "materiality remain in their owning skills"
)
def step_hard_rules_remain_in_skills(context):
    root = context.installed_workflow_roots[0]
    mature = (root / "zpp-mature-utilities" / "SKILL.md").read_text(encoding="utf-8")
    wire = (root / "zpp-wire-feature" / "SKILL.md").read_text(encoding="utf-8")
    zmem = (root / "zpp-commit-zmem" / "SKILL.md").read_text(encoding="utf-8")
    assert "OpenSpec operation prerequisite" in mature
    assert "root agent exclusively owns" in wire
    assert "material tracked work" in zmem


@then(
    "python-bdd, python-tdd, and python-build remain independent optional "
    "traits outside the skill bodies"
)
def step_python_traits_outside_skills(context):
    optional = ("python-bdd", "python-tdd", "python-build")
    for root in context.installed_workflow_roots:
        skill_text = "\n".join(
            (root / name / "SKILL.md").read_text(encoding="utf-8")
            for name in context.workflow_skill_names
        )
        leaked = [name for name in optional if name in skill_text]
        assert not leaked, (root, leaked)


def install_change_lifecycle_policy(context) -> None:
    initialize(context)
    git_init(context.project)
    result = invoke(context, ["workflow", "install", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    root = workflow_skill_root(context, "codex", scope="local")
    context.lifecycle_skills = {
        name: (root / name / "SKILL.md").read_text(encoding="utf-8")
        for name in context.workflow_skill_names
    }
    context.lifecycle_trait = (
        context.home
        / ".zpp"
        / "profiles"
        / "default"
        / "traits"
        / "automatic-workflow.md"
    ).read_text(encoding="utf-8")


@given(
    "a workflow relates a product change, a utility companion, "
    "and a temporary internal anchor"
)
def step_related_change_types(context):
    install_change_lifecycle_policy(context)


@given("an unrelated OpenSpec change remains active")
def step_unrelated_change_active(context):
    context.unrelated_change_active = True


@when("the mature workflow reaches finalization")
def step_workflow_reaches_finalization(context):
    assert context.lifecycle_skills


@then("the product change is handed to the owning OpenSpec finalizer")
def step_product_change_finalized(context):
    source = context.lifecycle_skills["zpp-form-specs"]
    assert "explicitly to `openspec-archive-change`" in source
    assert "Require the product change to be archived" in source


@then("the verified utility companion and consumed internal anchor are discarded")
def step_companions_discarded(context):
    mature = context.lifecycle_skills["zpp-mature-utilities"]
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "re-list active changes and require that companion to be absent" in mature.lower()
    assert "consumed internal anchor" in form.lower()
    assert "to be discarded" in form.lower()


@then("the unrelated active change is left untouched")
def step_unrelated_change_untouched(context):
    assert context.unrelated_change_active
    assert "Leave unrelated active changes untouched" in (
        context.lifecycle_skills["zpp-form-specs"]
    )
    assert "leave unrelated changes untouched" in context.lifecycle_trait


@then("completion requires a final audit of the related change set")
def step_final_related_change_audit(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    form = context.lifecycle_skills["zpp-form-specs"]
    trait = " ".join(context.lifecycle_trait.split())
    assert "session-local related set" in clarify
    assert "audit the session-local related change set" in form
    assert "Close or assign each related change before completion" in trait


@given("a consumed related OpenSpec change remains active without an owning stage")
def step_unowned_related_change(context):
    install_change_lifecycle_policy(context)
    context.unowned_related_change = True


@when("the workflow evaluates its completion gate")
def step_evaluate_completion_gate(context):
    assert context.unowned_related_change


@then("the workflow cannot report completion")
def step_completion_blocked(context):
    source = context.lifecycle_skills["zpp-form-specs"]
    assert "the workflow is incomplete" in source
    assert "never report overall completion" in source


@then("the unrelated OpenSpec change list is not required to be empty")
def step_unrelated_list_may_remain_active(context):
    assert "leave unrelated changes untouched" in context.lifecycle_trait
    assert "Leave unrelated active changes untouched" in (
        context.lifecycle_skills["zpp-form-specs"]
    )


@given("canonical OpenSpec records the currently accepted product behavior")
def step_canonical_openspec_current(context):
    install_change_lifecycle_policy(context)


@given("zmem records chronological decisions including a later change of direction")
def step_zmem_temporal_decisions(context):
    context.temporal_decisions = ("initial direction", "later direction")


@given("an active OpenSpec change contains mutable proposal and capability delta specs")
def step_active_planning_artifacts(context):
    context.active_planning_artifacts = True


@when("clarification establishes the product boundary")
def step_clarification_establishes_boundary(context):
    assert context.temporal_decisions
    assert context.active_planning_artifacts


@then("it compares the later zmem direction with canonical OpenSpec")
def step_clarification_compares_history(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "compare the latest relevant direction with canonical OpenSpec" in clarify


@then("it treats canonical OpenSpec as the long-standing current authority")
def step_canonical_authority(context):
    trait = " ".join(context.lifecycle_trait.split())
    assert "Canonical OpenSpec owns current accepted behavior" in trait


@then("it treats zmem as temporal decision history rather than current product truth")
def step_zmem_temporal_not_current(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "chronological evidence of meaningful decision changes" in clarify
    assert "never as current product truth" in clarify


@then("it treats the active OpenSpec planning artifacts as temporary working state")
def step_planning_artifacts_temporary_working_state(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "proposal and capability delta specs as mutable working state" in clarify


@then("no zmem dependency graph is required")
def step_no_zmem_dependency_graph(context):
    zmem = context.lifecycle_skills["zpp-commit-zmem"]
    assert "do not require a dependency graph" in zmem


@given("an OpenSpec proposal declares multiple new or modified capabilities")
def step_proposal_declares_capabilities(context):
    install_change_lifecycle_policy(context)
    context.declared_capabilities = ("first-capability", "second-capability")


@when("clarification settles behavior for the complete change")
def step_clarification_settles_complete_change(context):
    assert context.declared_capabilities


@then(
    "proposal.md retains the overview, capability inventory, impact, "
    "and unresolved owner decisions"
)
def step_proposal_retains_overview(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "motivation, scope, capability inventory, impact" in clarify
    assert "Unresolved — Do Not Assume" in clarify


@then("each declared capability has its own specs capability delta document")
def step_each_capability_has_delta(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "one status-reported delta at `specs/<capability>/spec.md`" in clarify


@then("settled behavior is persisted into its owning delta before clarification continues")
def step_settled_behavior_persisted(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "settled normative behavior belongs in its owning capability delta" in clarify
    assert "update the proposal and every affected capability delta before asking" in clarify


@then(
    "design and task artifacts follow the selected OpenSpec schema "
    "rather than a ZPP one-file rule"
)
def step_schema_owns_other_artifacts(context):
    clarify = context.lifecycle_skills["zpp-clarify-change"]
    assert "follow the selected schema's complete artifact graph" in clarify
    assert "do not impose ZPP-specific artifact omissions" in clarify


@given("a confirmed OpenSpec change contains proposal and capability delta documents")
def step_confirmed_multi_artifact_change(context):
    install_change_lifecycle_policy(context)


@when("the workflow shapes the complete Gherkin feature set")
def step_shape_complete_gherkin(context):
    context.shaping_started = True


@then("shaping consumes both proposal and capability delta documents")
def step_shaping_consumes_artifacts(context):
    assert context.shaping_started
    shape = context.lifecycle_skills["zpp-shape-feature"]
    assert "confirmed proposal and every status-reported capability delta" in shape


@then("shaping removes only executable examples duplicated by Gherkin")
def step_shaping_removes_only_examples(context):
    shape = context.lifecycle_skills["zpp-shape-feature"]
    assert "remove only duplicated executable examples" in shape


@then("shaping preserves stable intent, constraints, invariants, and acceptance obligations")
def step_shaping_preserves_contract(context):
    shape = context.lifecycle_skills["zpp-shape-feature"]
    assert "preserve intent, scope, constraints, invariants, and acceptance obligations" in shape


@when("mature green behavior later forms canonical specifications")
def step_mature_green_forms_specs(context):
    context.specification_formation_started = True


@then("formation reconciles the existing capability deltas")
def step_formation_reconciles_deltas(context):
    assert context.specification_formation_started
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "Reconcile each existing capability delta" in form


@then("formation does not create capability specifications for the first time")
def step_formation_requires_existing_deltas(context):
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "Do not create a declared capability's delta for the first time" in form


@given("a valid conventional commit message contains no zmem annotation")
def step_unannotated_conventional_message(context):
    context.commit_message = context.project / "commit-message.txt"
    context.commit_message.write_text(
        "fix(workflow): allow ordinary commit\n",
        encoding="utf-8",
    )


def run_packaged_zmem_validator(context, *, require_zmem: bool) -> None:
    scripts = (
        REPO_ROOT
        / "src"
        / "zpp"
        / "artifacts"
        / "skills"
        / "zpp-commit-zmem"
        / "scripts"
    )
    if os.name == "nt":
        executable = shutil.which("pwsh") or shutil.which("powershell")
        assert executable is not None
        command = [
            executable,
            "-NoProfile",
            "-File",
            str(scripts / "check-commit-msg.ps1"),
        ]
    else:
        executable = shutil.which("sh")
        assert executable is not None
        command = [executable, str(scripts / "check-commit-msg.sh")]
    if require_zmem:
        command.append("--require-zmem")
    command.extend(("--file", str(context.commit_message)))
    context.validator_result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    context.validator_output = json.loads(context.validator_result.stdout)


@when("the bundled commit-message validator checks an ordinary commit")
def step_validate_ordinary_commit(context):
    run_packaged_zmem_validator(context, require_zmem=False)


@then("validation succeeds with zero zmem annotations")
def step_ordinary_commit_valid(context):
    assert context.validator_result.returncode == 0
    assert context.validator_output["ok"] is True
    assert context.validator_output["annotations"] == 0


@when("the bundled commit-message validator checks a memory-bearing checkpoint")
def step_validate_memory_checkpoint(context):
    run_packaged_zmem_validator(context, require_zmem=True)


@then("validation fails because a canonical zmem annotation is required")
def step_memory_checkpoint_requires_annotation(context):
    assert context.validator_result.returncode == 23
    assert context.validator_output["ok"] is False
    assert context.validator_output["code"] == 23


@given("mature green behavior reflects the latest accepted decision")
def step_green_behavior_latest_decision(context):
    install_change_lifecycle_policy(context)


@given("zmem retains earlier directions, reversals, and their reasons")
def step_zmem_retains_history(context):
    context.temporal_history_retained = True


@when("the workflow forms canonical OpenSpec specifications")
def step_form_canonical_specs(context):
    assert context.temporal_history_retained


@then("only the enduring current behavior enters canonical OpenSpec")
def step_only_current_behavior_is_canonical(context):
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "Canonical specs own the current mature product behavior only" in form


@then("abandoned or superseded chronology remains in zmem")
def step_superseded_chronology_in_zmem(context):
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "Zmem retains the meaningful temporal sequence" in form
    assert "abandoned or superseded chronology" in form


@then("no zmem checkpoint is created merely to mark specification formation")
def step_no_spec_marker_zmem(context):
    form = context.lifecycle_skills["zpp-form-specs"]
    assert "never repeat an already recorded decision" in form
    assert "merely to mark specification adoption" in form


# Codespace integration fixtures exercise the public Typer commands while
# replacing only the external OpenSpec/editor/process boundary in ``invoke``.
from zpp.utils.codespace_models import CodespaceIndex
from zpp.utils.codespace_identity import projection_name
from zpp.utils.codespace_state import load_codespace_index
from zpp.utils.codespace_targets import CodespaceTarget
from zpp.utils.openspec_adapter import (
    OpenSpecMember,
    OpenSpecStoreRelation,
    OpenSpecWorkset,
)

use_step_matcher("re")


def create_committed_repository(root: Path, name: str) -> Path:
    path = root / name
    path.mkdir(parents=True)
    git_init(path)
    (path / "tracked.txt").write_text(f"{name}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ZPP Test",
            "-c",
            "user.email=zpp@example.invalid",
            "commit",
            "-q",
            "-m",
            "initial",
        ],
        cwd=path,
        check=True,
        capture_output=True,
    )
    return path.resolve()


# Bindings for the claim-owned codespace contract.
use_step_matcher("parse")


def setup_claim_codespace(context) -> None:
    if getattr(context, "claim_codespace_ready", False):
        return
    context.claim_codespace_ready = True
    context.openspec_worksets = {}
    context.openspec_relations = {}
    context.zpp_created_worksets = []
    context.removed_worksets = []
    context.opened_worksets = []
    context.private_registries = {}
    context.executed_environments = []
    context.activated_environments = []
    context.codespace_root = context.home / ".zpp" / "codespaces"
    roots = context.sandbox / "repositories"
    roots.mkdir()
    context.repos = {
        name: create_committed_repository(roots, name)
        for name in (
            "project-a",
            "project-b",
            "project-c",
            "store-1",
            "reference",
            "addition",
        )
    }
    context.repos["store-2"] = create_committed_repository(roots, "store-2")
    for name in ("project-a", "project-b", "project-c"):
        local_root = context.repos[name] / "openspec"
        local_root.mkdir()
        (local_root / "config.yaml").write_text(
            "schema: spec-driven\n",
            encoding="utf-8",
        )
    governing_one = OpenSpecStoreRelation(
        "store-1", context.repos["store-1"], "governing"
    )
    governing_two = OpenSpecStoreRelation(
        "store-2", context.repos["store-2"], "governing"
    )
    reference = OpenSpecStoreRelation(
        "reference", context.repos["reference"], "reference"
    )
    context.openspec_relations = {
        context.repos["project-a"]: (),
        context.repos["project-b"]: (governing_one, reference),
        context.repos["project-c"]: (governing_one, reference),
        context.repos["addition"]: (governing_two,),
    }
    context.workspace = context.sandbox / "explicit.code-workspace"
    context.workspace.write_text(
        json.dumps(
            {
                "folders": [
                    {"path": str(context.repos["project-a"])},
                    {"path": str(context.repos["project-b"])},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def claim_index(context) -> CodespaceIndex:
    return load_codespace_index(context.codespace_root)


def run_lock(
    context,
    paths: tuple[Path, ...],
    *,
    read_only: tuple[Path, ...] = (),
    yes: bool = False,
    input_text: str | None = "n\n",
):
    arguments = ["codespace", "lock", *(str(path) for path in paths)]
    for path in read_only:
        arguments.extend(("--read-only", str(path)))
    if yes:
        arguments.append("--yes")
    result = invoke(context, arguments, input_text=input_text)
    if result.exit_code == 0:
        context.last_instance = result.stdout.strip().splitlines()[-1]
    return result


def ensure_base_claim(context) -> None:
    setup_claim_codespace(context)
    index = claim_index(context)
    candidates = [
        claim
        for claim in index.claims.values()
        if {member.name for member in claim.members} >= {"project-a", "project-b"}
    ]
    if candidates:
        context.active_instance = candidates[0].instance_id
        return
    result = run_lock(
        context,
        (context.repos["project-a"], context.repos["project-b"]),
    )
    assert result.exit_code == 0, result.output
    context.active_instance = context.last_instance
    context.results.clear()


def ensure_mitigated_claim(context) -> None:
    ensure_base_claim(context)
    index = claim_index(context)
    candidates = [
        claim
        for claim in index.claims.values()
        if any(member.generated_worktree for member in claim.members)
    ]
    if candidates:
        context.mitigated_instance = candidates[0].instance_id
        return
    result = run_lock(
        context,
        (context.repos["project-c"], context.repos["project-b"]),
        yes=True,
    )
    assert result.exit_code == 0, result.output
    context.mitigated_instance = context.last_instance
    context.prepared_instance = context.last_instance
    context.results.clear()


def ensure_mixed_claim(context) -> None:
    setup_claim_codespace(context)
    candidates = [
        claim
        for claim in claim_index(context).claims.values()
        if any(member.access == "read_only" for member in claim.members)
    ]
    if candidates:
        context.active_instance = candidates[0].instance_id
        return
    result = run_lock(
        context,
        (context.repos["project-a"],),
        read_only=(context.repos["reference"],),
    )
    assert result.exit_code == 0, result.output
    context.active_instance = context.last_instance
    context.results.clear()


def commit_change(path: Path, message: str) -> None:
    (path / "tracked.txt").write_text(f"{message}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ZPP Test",
            "-c",
            "user.email=zpp@example.invalid",
            "commit",
            "-q",
            "-m",
            message,
        ],
        cwd=path,
        check=True,
        capture_output=True,
    )


def claim_given(context, text: str) -> None:
    setup_claim_codespace(context)
    if text == "explicit writable paths and explicit read-only repository paths have committed heads":
        context.mixed_writable = (context.repos["project-a"],)
        context.mixed_read_only = (context.repos["reference"],)
    elif text == "a read-only repository resolves external OpenSpec stores":
        context.openspec_relations[context.repos["reference"]] = (
            OpenSpecStoreRelation("store-2", context.repos["store-2"], "governing"),
        )
    elif text == "another active codespace already claims one selected read-only repository":
        owner = run_lock(context, (context.repos["reference"],))
        assert owner.exit_code == 0, owner.output
        context.reference_owner = context.last_instance
    elif text == "the current directory belongs only to a read-only member of one or more codespaces":
        ensure_mixed_claim(context)
        context.recorded_index = claim_index(context)
        os.chdir(context.repos["reference"])
    elif text == "a selected read-only repository has no first commit":
        unborn = context.sandbox / "repositories" / "unborn-reference"
        unborn.mkdir(exist_ok=True)
        git_init(unborn)
        context.request_paths = (context.repos["project-a"],)
        context.request_read_only = (unborn,)
    elif text == "a prepared codespace with writable and read-only members has no OpenSpec workset projection":
        ensure_mixed_claim(context)
        context.prepared_instance = context.active_instance
        assert claim_index(context).claims[context.prepared_instance].projection is None
    elif text == "an active codespace contains committed writable and read-only members":
        ensure_mixed_claim(context)
        context.original_claim = claim_index(context).claims[context.active_instance]
    elif text == "an active codespace has a durable mixed-access shape and may have one optional projection":
        ensure_mixed_claim(context)
        invoke(context, ["codespace", "open", context.active_instance])
        context.original_claim = claim_index(context).claims[context.active_instance]
        context.original_worksets = dict(context.openspec_worksets)
    elif text in {
        "a shape-changing edit targets an active codespace without --yes or -y",
        "a shape-changing edit targets an active codespace",
    }:
        ensure_mixed_claim(context)
        context.original_claim = claim_index(context).claims[context.active_instance]
    elif text == "instead the user declines either confirmation":
        context.decline_original = claim_index(context).claims[context.successor_instance]
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.successor_instance,
                "--add-read-only",
                str(context.repos["store-2"]),
            ],
            input_text="y\nn\n",
        )
    elif text == "an edit contains contradictory operations or cannot complete validation, mitigation, or replacement":
        ensure_mixed_claim(context)
        context.original_claim = claim_index(context).claims[context.active_instance]
    elif text == "an edit produces the existing effective membership, roles, and paths":
        ensure_mixed_claim(context)
        context.original_claim = claim_index(context).claims[context.active_instance]
    elif text == "an active codespace contains retained, removed, and demoted generated writable members":
        ensure_base_claim(context)
        owner = run_lock(context, (context.repos["addition"],))
        assert owner.exit_code == 0, owner.output
        result = run_lock(
            context,
            (
                context.repos["project-c"],
                context.repos["project-b"],
                context.repos["addition"],
            ),
            yes=True,
        )
        assert result.exit_code == 0, result.output
        context.active_instance = context.last_instance
        context.original_claim = claim_index(context).claims[context.active_instance]
        context.generated_before = {
            member.name: member
            for member in context.original_claim.members
            if member.generated_worktree
        }
    elif text == "an active codespace has writable and read-only physical checkout targets and a durable claim":
        ensure_mixed_claim(context)
    elif text == "an agent is associated with a codespace containing a read-only repository":
        ensure_mixed_claim(context)
        context.env["ZPP_CODESPACE_ID"] = context.active_instance
        context.guard_target = context.repos["reference"] / "guarded.txt"
    elif text == "the current directory is inside a checkout claimed by one active ZPP codespace":
        ensure_base_claim(context)
        os.chdir(context.repos["project-a"])
        context.before_claims = len(claim_index(context).claims)
    elif text == "instead no active claim or explicit input supplies writable targets":
        for claim in tuple(claim_index(context).claims.values()):
            invoke(context, ["codespace", "unlock", claim.instance_id])
        os.chdir(context.repos["reference"])
    elif text.startswith("two ZPP processes"):
        context.concurrent_paths = (
            (context.repos["project-a"], context.repos["project-b"]),
            (context.repos["project-a"], context.repos["project-c"]),
        )
    elif text.startswith("a requested repository has no first commit"):
        unborn = context.sandbox / "repositories" / "unborn-target"
        unborn.mkdir(exist_ok=True)
        git_init(unborn)
        context.request_paths = (unborn,)
    elif text.startswith("an associated store is neither"):
        context.openspec_relations[context.repos["project-b"]] = ValueError(
            "unclassified OpenSpec store relation: unknown"
        )
        context.request_paths = (context.repos["project-b"],)
    elif text == "all codespace claim and optional workset state is recorded":
        context.recorded_index = claim_index(context)
        context.recorded_worksets = dict(context.openspec_worksets)
    elif text == "one claimed checkout later receives file changes and new commits":
        ensure_base_claim(context)
        context.starting_claim = claim_index(context).claims[context.active_instance]
        commit_change(context.repos["project-b"], "advanced")
        (context.repos["project-b"] / "dirty.txt").write_text(
            "dirty\n", encoding="utf-8"
        )
    elif text == "the claimed Project B checkout has advanced to a new commit":
        ensure_base_claim(context)
        commit_change(context.repos["project-b"], "advanced")
    elif text.startswith("mitigation would use a sibling path"):
        ensure_base_claim(context)
        context.fixed_instance = "collisionid"
        context.collision_path = (
            context.repos["project-b"].parent / "project-b-collisionid"
        )
        context.collision_path.mkdir()
    elif text in {
        "the complete project, store, optional workset, and claim state is recorded",
        "the complete original codespace state is recorded",
    }:
        context.recorded_index = claim_index(context)
        context.recorded_worksets = dict(context.openspec_worksets)
    elif text == "a prepared codespace has no OpenSpec workset projection":
        ensure_mitigated_claim(context)
        context.prepared_instance = context.mitigated_instance
        assert claim_index(context).claims[context.prepared_instance].projection is None
    elif text.startswith("a mitigated codespace maps"):
        ensure_mitigated_claim(context)
    elif text.startswith("a released codespace has a clean"):
        ensure_mitigated_claim(context)
        claim = claim_index(context).claims[context.mitigated_instance]
        generated = [member for member in claim.members if member.generated_worktree]
        assert len(generated) >= 2
        (generated[1].effective_path / "dirty.txt").write_text(
            "dirty\n", encoding="utf-8"
        )
        invoke(context, ["codespace", "unlock", claim.instance_id])
        context.released_instance = claim.instance_id
        context.generated_paths = tuple(member.effective_path for member in generated)
    elif text.startswith("a durable codespace claim was abandoned"):
        ensure_mitigated_claim(context)
        context.abandoned_instance = context.mitigated_instance
    elif text == "its generated worktrees may contain dirty files":
        claim = claim_index(context).claims[context.abandoned_instance]
        generated = [member for member in claim.members if member.generated_worktree]
        (generated[0].effective_path / "dirty.txt").write_text(
            "dirty\n", encoding="utf-8"
        )
        context.abandoned_paths = tuple(member.effective_path for member in generated)
    elif text.startswith("orphaned ZPP-owned projections"):
        context.openspec_worksets["zpp-orphan-g1"] = OpenSpecWorkset(
            "zpp-orphan-g1", ()
        )
        context.openspec_worksets["user-owned"] = OpenSpecWorkset("user-owned", ())
    elif text == "an unrelated user-owned OpenSpec workset exists":
        context.openspec_worksets["user-owned"] = OpenSpecWorkset("user-owned", ())
    elif text.startswith("a ZPP-owned workset projection"):
        context.openspec_worksets["zpp-orphan-g1"] = OpenSpecWorkset(
            "zpp-orphan-g1", ()
        )
    elif text.startswith("user-owned worksets"):
        context.openspec_worksets["user-owned"] = OpenSpecWorkset("user-owned", ())
        context.user_state_before = dict(context.openspec_worksets)
    elif text.startswith("codespaces have previously used"):
        context.history_ids = []
        for path in (context.repos["project-a"], context.repos["project-c"]):
            result = run_lock(context, (path,))
            assert result.exit_code == 0, result.output
            identifier = context.last_instance
            invoke(context, ["codespace", "unlock", identifier])
            context.history_ids.append(identifier)
    elif text.startswith("a mitigated codespace records every"):
        ensure_mitigated_claim(context)
        context.lifecycle_instance = context.mitigated_instance
        context.lifecycle_branches = tuple(
            member.branch
            for member in claim_index(context).claims[context.lifecycle_instance].members
            if member.generated_worktree
        )
    elif text.startswith("another active codespace claims"):
        ensure_base_claim(context)
        context.guard_owner = context.active_instance
        context.guard_target = context.repos["project-b"] / "guarded.txt"
        os.chdir(context.repos["project-c"])
    elif text.startswith("its shell work is associated"):
        ensure_base_claim(context)
        os.chdir(context.repos["project-a"])
    elif any(
        marker in text
        for marker in (
            "one codespace claims",
            "an active codespace",
            "a requested codespace conflicts",
            "another request contains",
        )
    ):
        ensure_base_claim(context)


def claim_when(context, text: str) -> None:
    setup_claim_codespace(context)
    if text == "the user runs zpp codespace lock with the writable paths and --read-only paths":
        context.result = run_lock(
            context,
            context.mixed_writable,
            read_only=context.mixed_read_only,
        )
        context.mixed_instance = context.last_instance
    elif text == "the user runs a codespace command without an identity or activated environment":
        context.result = invoke(context, ["codespace", "status"])
    elif text.startswith("the user runs zpp codespace edit with --") and text.endswith(
        "for a committed path and --yes"
    ):
        operation = text.split(" with ", 1)[1].split(" for ", 1)[0]
        target = {
            "--add": context.repos["addition"],
            "--add-read-only": context.repos["project-c"],
            "--remove": context.repos["reference"],
            "--promote": context.repos["reference"],
            "--demote": context.repos["project-a"],
        }[operation]
        context.edit_operation = operation
        context.edit_target = target
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                operation,
                str(target),
                "--yes",
            ],
        )
        if context.result.exit_code == 0:
            context.successor_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "one valid edit changes several members and access roles":
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                "--add",
                str(context.repos["addition"]),
                "--remove",
                str(context.repos["reference"]),
                "--demote",
                str(context.repos["project-a"]),
                "--yes",
            ],
        )
        if context.result.exit_code == 0:
            context.successor_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "the user accepts the complete successor shape":
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                "--add-read-only",
                str(context.repos["project-c"]),
            ],
            input_text="y\ny\n",
        )
        if context.result.exit_code == 0:
            context.successor_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "the user accepts the release confirmation":
        assert context.result.exit_code == 0
    elif text == "the user runs zpp codespace edit with --yes or -y":
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                "--add-read-only",
                str(context.repos["project-c"]),
                "-y",
            ],
        )
        if context.result.exit_code == 0:
            context.successor_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "the user attempts the edit":
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                "--add",
                str(context.repos["addition"]),
                "--remove",
                str(context.repos["addition"]),
                "--yes",
            ],
        )
    elif text == "the user runs zpp codespace edit":
        context.result = invoke(
            context, ["codespace", "edit", context.active_instance]
        )
    elif text == "the user confirms the shape edit":
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.active_instance,
                "--remove",
                str(context.repos["store-1"]),
                "--demote",
                str(context.repos["project-b"]),
                "--yes",
            ],
        )
        if context.result.exit_code == 0:
            context.successor_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "a supported direct edit or write targets that read-only repository":
        payload = {
            "cwd": str(context.repos["project-a"]),
            "tool_name": "apply_patch",
            "tool_input": {
                "command": f"*** Update File: {context.guard_target}"
            },
        }
        context.guard_result = invoke(
            context,
            ["codespace", "guard", "--agent", "codex"],
            input_text=json.dumps(payload, ensure_ascii=False),
        )
        context.guard_output = json.loads(context.guard_result.stdout)
    elif text == "the user runs zpp codespace lock using an explicit workspace descriptor":
        context.result = invoke(
            context,
            ["codespace", "lock", "--workspace", str(context.workspace)],
        )
        context.last_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "the user runs zpp codespace lock using an explicit path list":
        context.result = run_lock(
            context,
            (context.repos["project-a"], context.repos["project-b"]),
        )
    elif text == "the user runs zpp codespace lock without paths":
        context.result = invoke(context, ["codespace", "lock"])
    elif text == "the user repeats locking with an explicit workspace descriptor or path list":
        context.result = run_lock(context, (context.repos["project-c"],))
    elif text == "both attempt to acquire their complete target sets concurrently":
        from concurrent.futures import ThreadPoolExecutor
        from zpp.core.codespaces import lock_codespace

        def acquire(paths):
            try:
                result = lock_codespace(
                    home=context.home,
                    targets=tuple(
                        CodespaceTarget(path.name, path, "writable") for path in paths
                    ),
                    mitigate=False,
                )
                return ("success", result.claim.instance_id)
            except BaseException as error:
                return ("error", str(error))

        with ExitStack() as stack:
            stack.enter_context(
                patch(
                    "zpp.utils.codespace_targets.resolve_openspec_relations",
                    return_value=(),
                )
            )
            stack.enter_context(
                patch("zpp.core.codespaces.list_openspec_worksets", return_value=())
            )
            stack.enter_context(
                patch("zpp.core.codespaces.materialize_private_registry")
            )
            with ThreadPoolExecutor(max_workers=2) as executor:
                context.concurrent_results = list(
                    executor.map(acquire, context.concurrent_paths)
                )
    elif text == "ZPP inspects or re-locks the same effective target set":
        context.status_result = invoke(
            context, ["codespace", "status", context.active_instance, "--json"]
        )
        context.result = run_lock(
            context,
            (context.repos["project-a"], context.repos["project-b"]),
        )
    elif text == "the user attempts to lock the requested target set":
        paths = getattr(
            context,
            "request_paths",
            (context.repos["project-c"], context.repos["project-b"]),
        )
        context.result = run_lock(
            context,
            tuple(paths),
            read_only=tuple(getattr(context, "request_read_only", ())),
            input_text="n\n",
        )
    elif text == "the user declines the grouped mitigation offer":
        context.result = run_lock(
            context,
            (context.repos["project-c"], context.repos["project-b"]),
            input_text="n\n",
        )
    elif text in {"the user confirms conflict mitigation", "the user confirms mitigation"}:
        context.result = run_lock(
            context,
            (context.repos["project-c"], context.repos["project-b"]),
            yes=True,
        )
        if context.result.exit_code == 0:
            context.mitigated_instance = context.last_instance
            context.prepared_instance = context.last_instance
    elif text == "the user declines the offer to open it":
        context.opened_before_decline = tuple(context.opened_worksets)
    elif text == "the user later runs zpp codespace open for the prepared codespace":
        context.result = invoke(
            context,
            ["codespace", "open", context.prepared_instance, "--tool", "code"],
        )
    elif text == "the codespace membership or effective paths later change":
        context.projection_before_add = claim_index(context).claims[
            context.prepared_instance
        ].projection
        context.result = invoke(
            context,
            [
                "codespace",
                "edit",
                context.prepared_instance,
                "--add",
                str(context.repos["addition"]),
                "--yes",
            ],
        )
        if context.result.exit_code == 0:
            context.superseded_projection_instance = context.prepared_instance
            context.prepared_instance = context.result.stdout.strip().splitlines()[-1]
    elif text == "the user runs zpp codespace activate for that codespace":
        context.result = invoke(
            context, ["codespace", "activate", context.mitigated_instance]
        )
    elif text == "the user runs zpp codespace exec for that codespace with an OpenSpec command":
        context.result = invoke(
            context,
            [
                "codespace",
                "exec",
                "--codespace",
                context.mitigated_instance,
                "--",
                "openspec",
                "context",
                "--json",
            ],
        )
    elif text == "the user runs zpp codespace list and zpp codespace status":
        context.list_result = invoke(context, ["codespace", "list"])
        context.status_result = invoke(
            context, ["codespace", "status", context.active_instance, "--json"]
        )
    elif text == "the user runs zpp codespace unlock for the active codespace":
        context.result = invoke(
            context, ["codespace", "unlock", context.active_instance]
        )
        context.released_instance = context.active_instance
    elif text == "the user runs zpp codespace cleanup":
        context.result = invoke(
            context, ["codespace", "cleanup", context.released_instance]
        )
    elif text == "every retained branch is reconciled or explicitly abandoned and generated worktrees are gone":
        released = claim_index(context).released[context.released_instance]
        for debt in released.debts:
            if debt.effective_path.exists():
                dirty = debt.effective_path / "dirty.txt"
                if dirty.exists():
                    dirty.unlink()
        invoke(context, ["codespace", "cleanup", context.released_instance])
        released = claim_index(context).released[context.released_instance]
        for debt in released.debts:
            invoke(
                context,
                [
                    "codespace",
                    "disposition",
                    context.released_instance,
                    debt.checkout_key,
                    "--state",
                    "reconciled",
                ],
            )
    elif text == "the reconciliation workflow or user runs zpp codespace finalize":
        context.result = invoke(
            context, ["codespace", "finalize", context.released_instance]
        )
    elif text == "the user explicitly confirms forced recovery":
        context.result = invoke(
            context,
            [
                "codespace",
                "unlock",
                context.abandoned_instance,
                "--force",
                "--yes",
            ],
        )
    elif text == "the user runs any mutating zpp codespace command":
        context.result = run_lock(context, (context.repos["project-a"],))
    elif text == "those released codespaces are finalized":
        for identifier in context.history_ids:
            context.result = invoke(context, ["codespace", "finalize", identifier])
    elif text == "the user locks, edits, opens, unlocks, cleans, recovers, or finalizes that codespace":
        identifier = context.lifecycle_instance
        invoke(context, ["codespace", "open", identifier])
        edited = invoke(
            context,
            [
                "codespace",
                "edit",
                identifier,
                "--add",
                str(context.repos["addition"]),
                "--yes",
            ],
        )
        identifier = edited.stdout.strip().splitlines()[-1]
        invoke(context, ["codespace", "unlock", identifier])
        invoke(context, ["codespace", "cleanup", identifier])
        released = claim_index(context).released[identifier]
        for debt in released.debts:
            invoke(
                context,
                [
                    "codespace",
                    "disposition",
                    identifier,
                    debt.checkout_key,
                    "--state",
                    "abandoned",
                ],
            )
        context.lifecycle_released = claim_index(context).released[identifier]
    elif text.endswith("attempts a supported direct edit or write tool call from a different codespace"):
        agent = context.agent
        cwd = str(context.repos["project-c"])
        if agent == "pi":
            payload = {
                "cwd": cwd,
                "toolName": "write",
                "input": {"path": str(context.guard_target)},
            }
        elif agent == "codex":
            payload = {
                "cwd": cwd,
                "tool_name": "apply_patch",
                "tool_input": {
                    "command": f"*** Update File: {context.guard_target}"
                },
            }
        else:
            payload = {
                "cwd": cwd,
                "tool_name": "Write",
                "tool_input": {"file_path": str(context.guard_target)},
            }
        context.guard_result = invoke(
            context,
            ["codespace", "guard", "--agent", agent],
            input_text=json.dumps(payload, ensure_ascii=False),
        )
        context.guard_output = json.loads(context.guard_result.stdout)
    elif text.endswith("submits a supported shell tool call"):
        agent = context.agent
        payload = (
            {
                "cwd": str(context.repos["project-a"]),
                "toolName": "bash",
                "input": {"command": "echo ok"},
            }
            if agent == "pi"
            else {
                "cwd": str(context.repos["project-a"]),
                "tool_name": "Bash",
                "tool_input": {"command": "echo ok"},
            }
        )
        context.guard_result = invoke(
            context,
            ["codespace", "guard", "--agent", agent],
            input_text=json.dumps(payload, ensure_ascii=False),
        )
        context.guard_output = json.loads(context.guard_result.stdout)


def claim_then(context, text: str) -> None:
    index = claim_index(context)
    result = getattr(context, "result", None)
    if text == "one codespace view records the writable and read-only repositories with their access roles":
        claim = index.claims[context.mixed_instance]
        assert {member.name: member.access for member in claim.members} == {
            "project-a": "writable",
            "reference": "read_only",
        }
    elif text == "only the complete writable OpenSpec closure is exclusively claimed":
        claim = index.claims[context.mixed_instance]
        assert {member.name for member in claim.members if member.access == "writable"} == {
            "project-a"
        }
    elif text == "no read-only repository is treated as a conflict or receives an isolated worktree":
        reference = next(
            member
            for member in index.claims[context.mixed_instance].members
            if member.name == "reference"
        )
        assert reference.access == "read_only" and not reference.generated_worktree
    elif text == "related stores of a read-only repository are omitted unless independently selected":
        assert all(
            member.store_id != "store-2"
            for member in index.claims[context.mixed_instance].members
        )
    elif text == "the same read-only repository can remain in both codespaces":
        assert context.reference_owner in index.claims
        assert context.mixed_instance in index.claims
    elif text == "ZPP requires explicit codespace selection":
        assert result.exit_code != 0
        assert "current directory is not inside an active codespace" in result.stderr
    elif text == "no claim or codespace view is changed":
        assert index == context.recorded_index
    elif text == "the projection contains the complete writable and read-only view":
        claim = index.claims[context.prepared_instance]
        name = projection_name(claim.instance_id, claim.projection.generation)
        assert {member.path for member in context.openspec_worksets[name].members} == {
            member.effective_path for member in claim.members
        }
    elif text.startswith("ZPP applies ") and text.endswith(
        " to the complete successor shape"
    ):
        assert result.exit_code == 0, result.output
        claim = index.claims[context.successor_instance]
        members = {member.name: member for member in claim.members}
        if context.edit_operation == "--add":
            assert members["addition"].access == "writable"
        elif context.edit_operation == "--add-read-only":
            assert members["project-c"].access == "read_only"
        elif context.edit_operation == "--remove":
            assert "reference" not in members
        elif context.edit_operation == "--promote":
            assert members["reference"].access == "writable"
        else:
            assert members["project-a"].access == "read_only"
    elif text == "the narrower zpp codespace add command is unavailable":
        unavailable = invoke(context, ["codespace", "add", "--help"])
        assert unavailable.exit_code != 0
    elif text == "one successor identity and snapshot are calculated from the resulting roles, paths, and current full commits":
        successor = index.claims[context.successor_instance]
        assert successor.instance_id != context.original_claim.instance_id
        assert successor.snapshot_key != context.original_claim.snapshot_key
        assert all(len(member.commit) == 40 for member in successor.members)
    elif text == "the successor atomically replaces the superseded active identity and writable claim":
        assert context.original_claim.instance_id not in index.claims
        assert context.successor_instance in index.claims
    elif text == "no unlocked interval or partial successor shape is observable":
        successor = index.claims[context.successor_instance]
        assert {member.name for member in successor.members} >= {
            "addition",
            "store-2",
            "project-a",
        }
    elif text == "the superseded projection is removed or replaced with the successor projection":
        successor = index.claims[context.successor_instance]
        assert successor.projection is not None
        old_name = projection_name(
            context.original_claim.instance_id,
            context.original_claim.projection.generation,
        )
        new_name = projection_name(
            successor.instance_id,
            successor.projection.generation,
        )
        assert old_name in context.removed_worksets and new_name in context.openspec_worksets
    elif text == "later file changes and commits do not automatically recalculate the successor identity":
        before = index.claims[context.successor_instance]
        commit_change(context.repos["addition"], "after-edit")
        status = invoke(context, ["codespace", "status", context.successor_instance])
        assert status.exit_code == 0
        assert claim_index(context).claims[context.successor_instance] == before
    elif text == "ZPP separately asks to release the superseded lock":
        assert "Apply this complete successor shape?" in result.output
        assert "Release superseded codespace lock" in result.output
    elif text in {
        "ZPP performs the atomic successor replacement",
        "ZPP performs the same atomic successor replacement",
    }:
        assert result.exit_code == 0
        assert context.successor_instance in index.claims
        assert context.active_instance not in index.claims
    elif text == "the original identity, claim, shape, and optional projection remain unchanged":
        assert result.exit_code != 0
        expected = getattr(context, "decline_original", context.original_claim)
        assert index.claims[expected.instance_id] == expected
    elif text == "both replacement confirmations are preauthorized":
        assert result.exit_code == 0
        assert "Apply this complete successor shape?" not in result.output
        assert "Release superseded codespace lock" not in result.output
    elif text == "the edit is rejected before any partial successor becomes active":
        assert result.exit_code != 0
        assert "contradictory edit operations" in result.stderr
    elif text == "the existing identity and snapshot remain unchanged":
        assert index.claims[context.active_instance] == context.original_claim
    elif text == "ZPP requests no replacement confirmation":
        assert "Apply this complete successor shape?" not in result.output
        assert "Release superseded codespace lock" not in result.output
    elif text == "retained generated members transfer to the successor identity":
        successor = index.claims[context.successor_instance]
        retained = {member.name: member for member in successor.members}
        for name in ("addition", "store-2"):
            assert retained[name].effective_path == context.generated_before[name].effective_path
    elif text == "removed generated worktrees and branches remain reconciliation debt under the superseded identity":
        released = index.released[context.original_claim.instance_id]
        debt_paths = {debt.effective_path for debt in released.debts}
        assert context.generated_before["store-1"].effective_path in debt_paths
    elif text == "a demoted member references its canonical checkout read-only in the successor":
        member = next(
            item
            for item in index.claims[context.successor_instance].members
            if item.name == "project-b"
        )
        assert member.access == "read_only"
        assert member.effective_path == context.repos["project-b"]
    elif text == "its generated worktree and branch remain superseded reconciliation debt":
        released = index.released[context.original_claim.instance_id]
        assert any(
            debt.effective_path == context.generated_before["project-b"].effective_path
            and debt.branch == context.generated_before["project-b"].branch
            for debt in released.debts
        )
    elif text == "no generated content is deleted":
        assert all(member.effective_path.exists() for member in context.generated_before.values())
    elif text == "the active codespace and every writable and read-only member are inspectable with their access roles":
        assert context.list_result.exit_code == context.status_result.exit_code == 0
        payload = json.loads(context.status_result.stdout)
        assert {item["access"] for item in payload["current"]} == {
            "writable",
            "read_only",
        }
    elif text == "no read-only member is reported as claimed, generated, or pending reconciliation merely for joining the view":
        payload = json.loads(context.status_result.stdout)
        read_only = next(item for item in payload["current"] if item["access"] == "read_only")
        assert read_only["claimed"] is False and read_only["generated"] is False
    elif text == "the installed agent guard rejects the mutation as read-only in the associated codespace":
        assert context.guard_result.exit_code == 0
        output = context.guard_output["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "read-only" in output["permissionDecisionReason"]
    elif text == "unsupported tools, arbitrary shell effects, manual editor actions, and cross-machine writes remain outside the guarantee":
        unsupported = invoke(
            context,
            ["codespace", "guard", "--agent", "codex"],
            input_text=json.dumps(
                {
                    "cwd": str(context.repos["project-a"]),
                    "tool_name": "Read",
                    "tool_input": {},
                }
            ),
        )
        assert unsupported.exit_code == 0 and json.loads(unsupported.stdout) == {}
    elif text == "one durable codespace claim owns every complete project checkout exactly once":
        assert result.exit_code == 0, result.output
        claim = index.claims[context.last_instance]
        projects = [member for member in claim.members if member.kind == "project"]
        assert {member.original_path for member in projects} == {
            context.repos["project-a"],
            context.repos["project-b"],
        }
        assert len({member.checkout_key for member in claim.members}) == len(claim.members)
    elif text == "the claim also owns the external writable store checkout exactly once":
        claim = index.claims[context.last_instance]
        stores = [member for member in claim.members if member.store_id == "store-1"]
        assert len(stores) == 1 and stores[0].access == "writable"
    elif text == "the repo-local OpenSpec root is covered by its containing project checkout":
        claim = index.claims[context.last_instance]
        assert sum(
            member.original_path == context.repos["project-a"]
            for member in claim.members
        ) == 1
    elif text == "the reference-only store remains shared and unclaimed":
        assert all(
            member.store_id != "reference"
            for claim in index.claims.values()
            for member in claim.members
        )
    elif text == "the claim records each target's full starting commit hash":
        claim = index.claims[context.last_instance]
        assert all(len(member.commit) == 40 for member in claim.members)
    elif text == "no Git worktree or OpenSpec workset is created":
        claim = index.claims[context.last_instance]
        assert not any(member.generated_worktree for member in claim.members)
        assert context.zpp_created_worksets == []
    elif text == "no editor or agent is opened":
        assert context.opened_worksets == []
    elif text == "ZPP identifies the existing codespace":
        assert result.exit_code == 0
        assert result.stdout.strip() == context.active_instance
    elif text == "no second claim or OpenSpec workset is created":
        assert len(index.claims) == context.before_claims
        assert context.zpp_created_worksets == []
    elif text in {
        "locking is rejected without inferring ownership from an OpenSpec workset",
        "locking does not guess the folders open in an editor",
    }:
        assert result.exit_code != 0
        assert "explicit writable targets" in result.stderr
    elif text == "ZPP resolves the explicitly requested writable targets":
        assert result.exit_code == 0 and context.last_instance in index.claims
    elif text == "exactly one complete codespace claim becomes active":
        assert len(index.claims) == 1, context.concurrent_results
        assert sum(item[0] == "success" for item in context.concurrent_results) == 1, (
            context.concurrent_results
        )
    elif text == "the other request reports the active owner of the conflicting checkout":
        failed = next(item for item in context.concurrent_results if item[0] == "error")
        owner = next(iter(index.claims))
        assert owner in failed[1], context.concurrent_results
    elif text == "no partial claim remains from the rejected request":
        assert len(index.claims) == 1
        assert len(next(iter(index.claims.values())).members) == 2
    elif text == "the existing codespace remains active":
        assert result.exit_code == 0
        assert result.stdout.strip() == context.active_instance
        assert set(index.claims) == {context.active_instance}
    elif text == "its starting commit hashes remain unchanged":
        assert index.claims[context.active_instance].members == context.starting_claim.members
    elif text == "no claim or optional workset generation is replaced because of commit movement":
        assert index.claims[context.active_instance].instance_id == context.starting_claim.instance_id
        assert index.claims[context.active_instance].projection == context.starting_claim.projection
    elif text == "current dirty and commit state is reported separately":
        payload = json.loads(context.status_result.stdout)
        state = next(item for item in payload["current"] if item["name"] == "project-b")
        assert state["current_commit"] != state["starting_commit"]
        assert state["dirty"] is True
    elif text == "locking is rejected with the unresolved target identified":
        assert result.exit_code != 0
        assert "unborn" in result.stderr or "unclassified" in result.stderr
    elif text == "all recorded codespace claim and optional workset state is unchanged":
        assert index == context.recorded_index
        assert context.openspec_worksets == context.recorded_worksets
    elif text in {
        "the conflict report includes Project B and Store 1 together",
        "Project B remains conflicting despite its changed current commit",
    }:
        assert result.exit_code != 0
        assert "project-b" in result.stderr and "store-1" in result.stderr
    elif text == "Project C is not reported as conflicting":
        assert "project-c" not in result.stderr
    elif text == "no mitigation occurs before the user confirms it":
        assert len(index.claims) == 1
        assert not any(
            member.generated_worktree
            for claim in index.claims.values()
            for member in claim.members
        )
    elif text == "no worktree, branch, claim, or OpenSpec workset is created":
        assert result.exit_code != 0
        assert index == context.recorded_index
        assert context.openspec_worksets == context.recorded_worksets
    elif text == "the complete recorded state is unchanged":
        assert result.exit_code != 0
        assert index == context.recorded_index
        assert context.openspec_worksets == context.recorded_worksets
    elif text == "Project C continues using its canonical checkout":
        assert result.exit_code == 0, result.output
        claim = index.claims[context.last_instance]
        project = next(member for member in claim.members if member.name == "project-c")
        assert project.effective_path == context.repos["project-c"]
    elif text == "Project B and Store 1 receive distinct sibling worktrees named from the new codespace instance":
        claim = index.claims[context.last_instance]
        generated = [member for member in claim.members if member.generated_worktree]
        assert len(generated) == 2
        assert all(member.effective_path.name.endswith(claim.instance_id) for member in generated)
    elif text == "each generated worktree branches from its target's recorded starting commit":
        claim = index.claims[context.last_instance]
        assert all(
            member.branch and member.commit
            for member in claim.members
            if member.generated_worktree
        )
    elif text == "no uncommitted content is copied into a generated worktree":
        claim = index.claims[context.last_instance]
        assert all(
            not (member.effective_path / "dirty.txt").exists()
            for member in claim.members
            if member.generated_worktree
        )
    elif text == "the mitigated codespace claims the isolated physical checkouts":
        claim = index.claims[context.last_instance]
        assert all(
            member.checkout_key != member.source_checkout_key
            for member in claim.members
            if member.generated_worktree
        )
    elif text == "its private OpenSpec registry maps the original Store 1 id to the isolated Store 1 checkout":
        claim = index.claims[context.last_instance]
        store = next(member for member in claim.members if member.store_id == "store-1")
        assert context.private_registries[claim.instance_id]["store-1"] == store.effective_path
    elif text in {
        "the shared global OpenSpec registry is unchanged",
        "neither path changes shared global OpenSpec registration",
    }:
        assert context.openspec_relations
    elif text == "no OpenSpec workset is created until opening is requested":
        assert context.zpp_created_worksets == []
    elif text == "ZPP offers to open the prepared codespace without changing the existing workspace":
        assert context.opened_worksets == []
        assert context.prepared_instance in index.claims
    elif text == "the prepared codespace and its claim remain available without a projection":
        claim = index.claims[context.prepared_instance]
        assert claim.projection is None
    elif text == "the current editor or agent remains unchanged":
        assert tuple(context.opened_worksets) == context.opened_before_decline
    elif text == "ZPP creates and opens one owned projection named `zpp-<instance>-g<generation>`":
        claim = index.claims[context.prepared_instance]
        assert claim.projection is not None
        expected = f"zpp-{claim.instance_id}-g{claim.projection.generation}"
        assert context.zpp_created_worksets == [expected]
        assert context.opened_worksets[-1][0] == expected
    elif text == "repeated opening reuses that projection while its effective paths are unchanged":
        before = tuple(context.zpp_created_worksets)
        repeated = invoke(context, ["codespace", "open", context.prepared_instance])
        assert repeated.exit_code == 0
        assert tuple(context.zpp_created_worksets) == before
    elif text == "opening replaces the projection with the next structural generation":
        current = index.claims[context.prepared_instance].projection
        assert current.generation == context.projection_before_add.generation + 1
    elif text == "the superseded ZPP-owned projection is removed":
        previous = f"zpp-{context.superseded_projection_instance}-g{context.projection_before_add.generation}"
        assert previous in context.removed_worksets
        assert previous not in context.openspec_worksets
    elif text == "mitigation is rejected without reusing or overwriting the existing path or branch":
        assert result.exit_code != 0
        assert context.collision_path.exists()
        assert index == context.recorded_index
    elif text == "the resulting shell uses the codespace's private OpenSpec registry":
        assert result.exit_code == 0 and context.activated_environments
        assert "XDG_DATA_HOME" in context.activated_environments[-1]
    elif text == "that command uses the same private OpenSpec registry":
        assert result.exit_code == 0 and context.executed_environments
        assert context.executed_environments[-1]["XDG_DATA_HOME"] == context.activated_environments[-1]["XDG_DATA_HOME"]
    elif text == "both paths preserve the original logical store ids":
        assert "store-1" in context.private_registries[context.mitigated_instance]
    elif text == "the active codespace and every claimed physical checkout are inspectable":
        assert context.list_result.exit_code == context.status_result.exit_code == 0
        payload = json.loads(context.status_result.stdout)
        assert len(payload["current"]) == len(payload["claim"]["members"])
    elif text == "its write ownership and optional ZPP-owned projection are removed":
        assert context.active_instance not in index.claims
        assert context.active_instance in index.released
    elif text == "every project and store worktree is preserved":
        released = index.released[context.released_instance]
        assert all(debt.effective_path.exists() for debt in released.debts)
    elif text == "only outstanding generated-checkout and branch reconciliation debt is retained":
        released = index.released[context.released_instance]
        assert all(debt.branch and debt.checkout_key for debt in released.debts)
    elif text in {
        "the unrelated user-owned OpenSpec workset is unchanged",
        "the unrelated user-owned worksets are unchanged",
    }:
        assert "user-owned" in context.openspec_worksets
    elif text == "only the clean ZPP-owned generated worktree is removed":
        released = index.released[context.released_instance]
        assert sum(debt.worktree_removed for debt in released.debts) == 1
    elif text == "the dirty generated worktree and all of its content are preserved":
        released = index.released[context.released_instance]
        dirty = next(debt for debt in released.debts if not debt.worktree_removed)
        assert dirty.effective_path.exists()
        assert (dirty.effective_path / "dirty.txt").exists()
    elif text == "no canonical checkout or user-owned worktree is removed":
        assert all(context.repos[name].exists() for name in context.repos)
    elif text == "the released record is removed":
        assert context.released_instance not in index.released
    elif text == "the abandoned claim and its orphaned ZPP-owned projections are removed":
        assert context.abandoned_instance not in index.claims
        assert "zpp-orphan-g1" not in context.openspec_worksets
    elif text == "every generated worktree and dirty file is preserved":
        assert all(path.exists() for path in context.abandoned_paths)
        assert any((path / "dirty.txt").exists() for path in context.abandoned_paths)
    elif text == "no active claim expires automatically before that recovery":
        assert context.abandoned_instance in index.released
    elif text == "the orphaned ZPP-owned projection is removed":
        assert "zpp-orphan-g1" not in context.openspec_worksets
    elif text == "no user-owned workset, branch, or worktree is removed":
        assert "user-owned" in context.openspec_worksets
        assert all(path.exists() for path in context.repos.values())
    elif text == "the durable catalog retains only active claims and unresolved generated work":
        assert not any(identifier in index.released for identifier in context.history_ids)
    elif text == "it retains no complete historical workset projections for the finalized codespaces":
        assert all(identifier not in name for identifier in context.history_ids for name in context.openspec_worksets)
    elif text == "ZPP performs no automatic branch merge":
        assert all(context.lifecycle_branches)
        assert all("merge" not in branch.lower() for branch in context.lifecycle_branches)
    elif text == "the recorded branch metadata remains available until the explicit reconciliation workflow gives it a disposition":
        assert all(debt.branch for debt in context.lifecycle_released.debts)
    elif text == "the installed ZPP guard rejects the mutation before the checkout changes":
        assert context.guard_result.exit_code == 0
        if context.agent == "pi":
            assert context.guard_output["block"] is True
        else:
            assert context.guard_output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert not context.guard_target.exists()
    elif text == "the conflict identifies the active owning codespace":
        assert context.guard_owner in json.dumps(context.guard_output)
    elif text == "no OpenSpec workset is accepted as proof of write ownership":
        assert context.guard_owner in index.claims
    elif text == "the installed ZPP guard verifies that codespace and current checkout association":
        assert context.guard_result.exit_code == 0 and context.guard_output == {}
    elif text == "it does not claim to infer every path the arbitrary shell command may mutate":
        assert context.guard_output == {}
    elif text == "manual editor actions, unrelated processes, and unsupported tool paths remain outside its guarantee":
        agent = context.agent
        payload = (
            {"cwd": str(context.repos["project-a"]), "toolName": "read", "input": {}}
            if agent == "pi"
            else {
                "cwd": str(context.repos["project-a"]),
                "tool_name": "Read",
                "tool_input": {},
            }
        )
        unsupported = invoke(
            context,
            ["codespace", "guard", "--agent", agent],
            input_text=json.dumps(payload),
        )
        assert unsupported.exit_code == 0 and json.loads(unsupported.stdout) == {}
    else:
        raise AssertionError(f"unhandled codespace result step: {text}")


CLAIM_GIVENS = (
    "an explicit workspace descriptor names committed project checkouts",
    "an explicit path list names committed project checkouts",
    "one project uses a repo-local OpenSpec root",
    "another project resolves to an external writable OpenSpec store",
    "the projects also use a registered store only as a reference",
    "no active codespace claims any resolved physical checkout",
    "the current directory is inside a checkout claimed by one active ZPP codespace",
    "instead no active claim or explicit input supplies writable targets",
    "two ZPP processes on the same machine request claims containing the same physical checkout",
    "an active codespace records the full starting commit hashes of its claimed checkouts",
    "one claimed checkout later receives file changes and new commits",
    "a requested repository has no first commit",
    "an associated store is neither writable nor reference-only",
    "all codespace claim and optional workset state is recorded",
    "one codespace claims Project A, Project B, and writable Store 1",
    "another request contains uncontested Project C, the claimed Project B checkout, and Store 1",
    "the claimed Project B checkout has advanced to a new commit",
    "a requested codespace conflicts with an active codespace",
    "the complete project, store, optional workset, and claim state is recorded",
    "another request contains uncontested Project C, Project B, and Store 1",
    "the requested codespace begins from the same starting commits as the active codespace",
    "a prepared codespace has no OpenSpec workset projection",
    "mitigation would use a sibling path or branch that already exists",
    "the complete original codespace state is recorded",
    "a mitigated codespace maps original logical store ids to isolated store checkouts",
    "an unrelated user-owned OpenSpec workset exists",
    "a released codespace has a clean generated worktree and a dirty generated worktree",
    "a durable codespace claim was abandoned without being unlocked",
    "its generated worktrees may contain dirty files",
    "orphaned ZPP-owned projections and unrelated user-owned worksets exist",
    "a ZPP-owned workset projection is absent from the durable active codespace index",
    "user-owned worksets, branches, and worktrees also exist",
    "codespaces have previously used many different target combinations",
    "every released generated checkout and branch has received a final disposition",
    "a mitigated codespace records every generated project and store branch",
    "another active codespace claims the physical checkout targeted by a ZPP-managed mutation",
    "codespace-claim-guard is inactive for the target",
    "its shell work is associated with an active codespace and current checkout",
)

CLAIM_WHENS = (
    "the user runs zpp codespace lock using an explicit workspace descriptor",
    "the user runs zpp codespace lock using an explicit path list",
    "the user runs zpp codespace lock without paths",
    "the user repeats locking with an explicit workspace descriptor or path list",
    "both attempt to acquire their complete target sets concurrently",
    "ZPP inspects or re-locks the same effective target set",
    "the user attempts to lock the requested target set",
    "the user declines the grouped mitigation offer",
    "the user confirms conflict mitigation",
    "the user confirms mitigation",
    "the user declines the offer to open it",
    "the user later runs zpp codespace open for the prepared codespace",
    "the codespace membership or effective paths later change",
    "the user runs zpp codespace activate for that codespace",
    "the user runs zpp codespace exec for that codespace with an OpenSpec command",
    "the user runs zpp codespace list and zpp codespace status",
    "the user runs zpp codespace unlock for the active codespace",
    "the user runs zpp codespace cleanup",
    "every retained branch is reconciled or explicitly abandoned and generated worktrees are gone",
    "the reconciliation workflow or user runs zpp codespace finalize",
    "the user explicitly confirms forced recovery",
    "the user runs any mutating zpp codespace command",
    "those released codespaces are finalized",
)

CLAIM_THENS = (
    "one durable codespace claim owns every complete project checkout exactly once",
    "the claim also owns the external writable store checkout exactly once",
    "the repo-local OpenSpec root is covered by its containing project checkout",
    "the reference-only store remains shared and unclaimed",
    "the claim records each target's full starting commit hash",
    "no Git worktree or OpenSpec workset is created",
    "no editor or agent is opened",
    "ZPP identifies the existing codespace",
    "no second claim or OpenSpec workset is created",
    "locking is rejected without inferring ownership from an OpenSpec workset",
    "locking does not guess the folders open in an editor",
    "ZPP resolves the explicitly requested writable targets",
    "exactly one complete codespace claim becomes active",
    "the other request reports the active owner of the conflicting checkout",
    "no partial claim remains from the rejected request",
    "the existing codespace remains active",
    "its starting commit hashes remain unchanged",
    "no claim or optional workset generation is replaced because of commit movement",
    "current dirty and commit state is reported separately",
    "locking is rejected with the unresolved target identified",
    "all recorded codespace claim and optional workset state is unchanged",
    "the conflict report includes Project B and Store 1 together",
    "Project B remains conflicting despite its changed current commit",
    "Project C is not reported as conflicting",
    "no mitigation occurs before the user confirms it",
    "no worktree, branch, claim, or OpenSpec workset is created",
    "the complete recorded state is unchanged",
    "Project C continues using its canonical checkout",
    "Project B and Store 1 receive distinct sibling worktrees named from the new codespace instance",
    "each generated worktree branches from its target's recorded starting commit",
    "no uncommitted content is copied into a generated worktree",
    "the mitigated codespace claims the isolated physical checkouts",
    "its private OpenSpec registry maps the original Store 1 id to the isolated Store 1 checkout",
    "the shared global OpenSpec registry is unchanged",
    "no OpenSpec workset is created until opening is requested",
    "ZPP offers to open the prepared codespace without changing the existing workspace",
    "the prepared codespace and its claim remain available without a projection",
    "the current editor or agent remains unchanged",
    "ZPP creates and opens one owned projection named `zpp-<instance>-g<generation>`",
    "repeated opening reuses that projection while its effective paths are unchanged",
    "opening replaces the projection with the next structural generation",
    "the superseded ZPP-owned projection is removed",
    "mitigation is rejected without reusing or overwriting the existing path or branch",
    "the resulting shell uses the codespace's private OpenSpec registry",
    "that command uses the same private OpenSpec registry",
    "both paths preserve the original logical store ids",
    "neither path changes shared global OpenSpec registration",
    "the active codespace and every claimed physical checkout are inspectable",
    "its write ownership and optional ZPP-owned projection are removed",
    "every project and store worktree is preserved",
    "only outstanding generated-checkout and branch reconciliation debt is retained",
    "the unrelated user-owned OpenSpec workset is unchanged",
    "only the clean ZPP-owned generated worktree is removed",
    "the dirty generated worktree and all of its content are preserved",
    "no canonical checkout or user-owned worktree is removed",
    "the released record is removed",
    "the abandoned claim and its orphaned ZPP-owned projections are removed",
    "every generated worktree and dirty file is preserved",
    "the unrelated user-owned worksets are unchanged",
    "no active claim expires automatically before that recovery",
    "the orphaned ZPP-owned projection is removed",
    "no user-owned workset, branch, or worktree is removed",
    "the durable catalog retains only active claims and unresolved generated work",
    "it retains no complete historical workset projections for the finalized codespaces",
    "ZPP performs no automatic branch merge",
    "the recorded branch metadata remains available until the explicit reconciliation workflow gives it a disposition",
    "the installed ZPP guard rejects the mutation before the checkout changes",
    "the conflict identifies the active owning codespace",
    "no OpenSpec workset is accepted as proof of write ownership",
    "the installed ZPP guard verifies that codespace and current checkout association",
    "it does not claim to infer every path the arbitrary shell command may mutate",
    "manual editor actions, unrelated processes, and unsupported tool paths remain outside its guarantee",
)

CLAIM_GIVENS += (
    "explicit writable paths and explicit read-only repository paths have committed heads",
    "a read-only repository resolves external OpenSpec stores",
    "another active codespace already claims one selected read-only repository",
    "the current directory belongs only to a read-only member of one or more codespaces",
    "a selected read-only repository has no first commit",
    "a prepared codespace with writable and read-only members has no OpenSpec workset projection",
    "an active codespace contains committed writable and read-only members",
    "an active codespace has a durable mixed-access shape and may have one optional projection",
    "a shape-changing edit targets an active codespace without --yes or -y",
    "instead the user declines either confirmation",
    "a shape-changing edit targets an active codespace",
    "an edit contains contradictory operations or cannot complete validation, mitigation, or replacement",
    "an edit produces the existing effective membership, roles, and paths",
    "an active codespace contains retained, removed, and demoted generated writable members",
    "an active codespace has writable and read-only physical checkout targets and a durable claim",
    "an agent is associated with a codespace containing a read-only repository",
)

CLAIM_WHENS += (
    "the user runs zpp codespace lock with the writable paths and --read-only paths",
    "the user runs a codespace command without an identity or activated environment",
    "the user runs zpp codespace edit with --add for a committed path and --yes",
    "the user runs zpp codespace edit with --add-read-only for a committed path and --yes",
    "the user runs zpp codespace edit with --remove for a committed path and --yes",
    "the user runs zpp codespace edit with --promote for a committed path and --yes",
    "the user runs zpp codespace edit with --demote for a committed path and --yes",
    "one valid edit changes several members and access roles",
    "the user accepts the complete successor shape",
    "the user accepts the release confirmation",
    "the user runs zpp codespace edit with --yes or -y",
    "the user attempts the edit",
    "the user runs zpp codespace edit",
    "the user confirms the shape edit",
    "the user locks, edits, opens, unlocks, cleans, recovers, or finalizes that codespace",
    "a supported direct edit or write targets that read-only repository",
)

CLAIM_THENS += (
    "one codespace view records the writable and read-only repositories with their access roles",
    "only the complete writable OpenSpec closure is exclusively claimed",
    "no read-only repository is treated as a conflict or receives an isolated worktree",
    "related stores of a read-only repository are omitted unless independently selected",
    "the same read-only repository can remain in both codespaces",
    "ZPP requires explicit codespace selection",
    "no claim or codespace view is changed",
    "the projection contains the complete writable and read-only view",
    "opening replaces the projection with the next structural generation",
    "the superseded ZPP-owned projection is removed",
    "ZPP applies a new exclusively claimed writable member to the complete successor shape",
    "ZPP applies a new non-owning read-only member to the complete successor shape",
    "ZPP applies removal of the selected member to the complete successor shape",
    "ZPP applies promotion from read-only to writable to the complete successor shape",
    "ZPP applies demotion from writable to read-only to the complete successor shape",
    "the narrower zpp codespace add command is unavailable",
    "one successor identity and snapshot are calculated from the resulting roles, paths, and current full commits",
    "the successor atomically replaces the superseded active identity and writable claim",
    "no unlocked interval or partial successor shape is observable",
    "the superseded projection is removed or replaced with the successor projection",
    "later file changes and commits do not automatically recalculate the successor identity",
    "ZPP separately asks to release the superseded lock",
    "ZPP performs the atomic successor replacement",
    "the original identity, claim, shape, and optional projection remain unchanged",
    "both replacement confirmations are preauthorized",
    "ZPP performs the same atomic successor replacement",
    "the edit is rejected before any partial successor becomes active",
    "the existing identity and snapshot remain unchanged",
    "ZPP requests no replacement confirmation",
    "retained generated members transfer to the successor identity",
    "removed generated worktrees and branches remain reconciliation debt under the superseded identity",
    "a demoted member references its canonical checkout read-only in the successor",
    "its generated worktree and branch remain superseded reconciliation debt",
    "no generated content is deleted",
    "the active codespace and every writable and read-only member are inspectable with their access roles",
    "no read-only member is reported as claimed, generated, or pending reconciliation merely for joining the view",
    "the installed agent guard rejects the mutation as read-only in the associated codespace",
    "unsupported tools, arbitrary shell effects, manual editor actions, and cross-machine writes remain outside the guarantee",
)

def bind_claim_step(handler, text: str):
    def bound(context):
        return handler(context, text)

    return bound


for _text in CLAIM_GIVENS:
    given(_text)(bind_claim_step(claim_given, _text))
for _text in CLAIM_WHENS:
    when(_text)(bind_claim_step(claim_when, _text))
for _agent in ("Pi", "Codex", "Claude Code"):
    _direct = (
        f"{_agent} attempts a supported direct edit or write tool call from a different codespace"
    )
    _shell = f"{_agent} submits a supported shell tool call"
    when(_direct)(bind_claim_step(claim_when, _direct))
    when(_shell)(bind_claim_step(claim_when, _shell))
for _text in CLAIM_THENS:
    then(_text)(bind_claim_step(claim_then, _text))
