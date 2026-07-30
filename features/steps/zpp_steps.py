from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from unittest.mock import patch

import yaml
from behave import given, then, use_step_matcher, when

from zpp.cli import app
from zpp.utils.models import CancelledAgentSelection, ConfirmedAgentSelection


def invoke(context, arguments: list[str], *, input_text: str | None = None):
    def select(choices):
        context.selector_offers.append(tuple(choices))
        if context.selector_answer is None:
            return CancelledAgentSelection()
        return ConfirmedAgentSelection(tuple(context.selector_answer))

    with (
        patch("zpp.cli.interactive_terminal_available", return_value=context.interactive),
        patch("zpp.cli.select_agents", side_effect=select),
    ):
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
    result = invoke(context, ["resolve", str(context.project)])
    context.injected = [result.stdout] if result.exit_code == 0 and result.stdout else []


use_step_matcher("parse")


@then("ZPP resolves the current working directory")
def step_hook_cwd(context):
    assert context.result.exit_code == 0


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
    assert snapshot(context.home / ".pi") == context.pi_before


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


@then(r'the diagnostic identifies (?P<subject>the invalid profile name|the invalid saved name|the invalid managed source|".+")')
def step_diagnostic_subject(context, subject):
    subject = subject.strip()
    if subject == "the invalid profile name" or subject == "the invalid saved name":
        expected = "Invalid"
    elif subject == "the invalid managed source":
        assert_diagnostic_path(context.result.stderr, context.invalid_source)
        return
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
