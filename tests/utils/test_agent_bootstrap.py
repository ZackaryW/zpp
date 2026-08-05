import json
from pathlib import Path

import pytest

from zpp.utils.agent_bootstrap import (
    AgentIntegrationInspection,
    bootstrap_claude_code,
    bootstrap_codex,
    bootstrap_pi,
    inspect_pi_extension,
    install_pi_extension,
    inspect_agent_integrations,
    load_packaged_pi_extension,
    plan_agent_integrations,
    preflight_claude_code,
    preflight_codex,
    preflight_pi,
)
from zpp.utils.filesystem_mutation import apply_mutation_plan
from zpp.utils.models import ManagedStateError, PackagedPiExtension


def test_agent_bootstraps_write_only_global_user_home_integrations(tmp_path: Path) -> None:
    artifact = PackagedPiExtension("export default function zpp() {}\n")

    results = (
        bootstrap_pi(tmp_path, artifact),
        bootstrap_codex(tmp_path),
        bootstrap_claude_code(tmp_path),
    )

    pi_path = tmp_path / ".pi" / "agent" / "extensions" / "zpp" / "index.ts"
    codex_path = tmp_path / ".codex" / "hooks.json"
    claude_path = tmp_path / ".claude" / "settings.json"
    assert pi_path.read_text(encoding="utf-8") == artifact.source
    assert results == (None, None, None)
    codex_hooks = json.loads(codex_path.read_text(encoding="utf-8"))["hooks"]
    claude_hooks = json.loads(claude_path.read_text(encoding="utf-8"))["hooks"]
    assert codex_hooks["SessionStart"] and codex_hooks["PreToolUse"]
    assert claude_hooks["SessionStart"] and claude_hooks["PreToolUse"]
    assert inspect_pi_extension(pi_path, artifact) == "identical"
    assert not (tmp_path / ".codex" / "skills").exists()
    assert not (tmp_path / ".claude" / "skills").exists()

    pi_path.write_text("unmanaged\n", encoding="utf-8")
    with pytest.raises(ManagedStateError):
        bootstrap_pi(tmp_path, artifact)


def test_packaged_pi_extension_resolves_fresh_traits_on_each_agent_start(
    tmp_path: Path,
) -> None:
    artifact = load_packaged_pi_extension()

    bootstrap_pi(tmp_path, artifact)
    destination = tmp_path / ".pi" / "agent" / "extensions" / "zpp" / "index.ts"

    assert destination.read_text(encoding="utf-8") == artifact.source
    assert 'pi.on("before_agent_start"' in artifact.source
    assert 'execFile("zpp", ["resolve", "--agent", "pi"]' in artifact.source
    assert "resolveTraits(event.systemPromptOptions.cwd)" in artifact.source
    assert "{ cwd, encoding:" in artifact.source
    assert "event.systemPrompt" in artifact.source
    assert "if (!traits)" in artifact.source
    assert ".trim()" not in artifact.source
    assert 'pi.on("tool_call"' in artifact.source
    assert '["codespace", "guard", "--agent", "pi"]' in artifact.source
    assert "JSON.stringify({ cwd, toolName, input })" in artifact.source


def test_pi_extension_install_is_idempotent_and_rejects_unmanaged_state(
    tmp_path: Path,
) -> None:
    artifact = PackagedPiExtension("π extension\n")
    destination = tmp_path / "nested" / "zpp" / "index.ts"

    install_pi_extension(destination, artifact)
    first_mtime = destination.stat().st_mtime_ns
    install_pi_extension(destination, artifact)

    assert destination.read_text(encoding="utf-8") == artifact.source
    assert destination.stat().st_mtime_ns == first_mtime

    destination.write_text("unmanaged\n", encoding="utf-8")
    with pytest.raises(ManagedStateError):
        install_pi_extension(destination, artifact)
    assert destination.read_text(encoding="utf-8") == "unmanaged\n"


def test_agent_preflights_detect_a_later_conflict_without_any_agent_write(
    tmp_path: Path,
) -> None:
    artifact = PackagedPiExtension("extension\n")
    codex_path = tmp_path / ".codex" / "hooks.json"
    codex_path.parent.mkdir()
    conflicting = {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup",
                    "hooks": [{"type": "command", "command": "zpp resolve"}],
                }
            ]
        }
    }
    codex_source = json.dumps(conflicting, ensure_ascii=False)
    codex_path.write_text(codex_source, encoding="utf-8")

    preflight_pi(tmp_path, artifact)
    preflight_claude_code(tmp_path)
    with pytest.raises(ManagedStateError):
        preflight_codex(tmp_path)

    assert codex_path.read_text(encoding="utf-8") == codex_source
    assert not (tmp_path / ".pi").exists()
    assert not (tmp_path / ".claude").exists()


def test_agent_integration_plan_is_pure_and_applies_every_selected_agent(
    tmp_path: Path,
) -> None:
    plan = plan_agent_integrations(tmp_path, ("pi", "codex", "claude"))

    assert not (tmp_path / ".pi").exists()
    assert not (tmp_path / ".codex").exists()
    assert not (tmp_path / ".claude").exists()

    apply_mutation_plan(plan)

    assert (tmp_path / ".pi/agent/extensions/zpp/index.ts").is_file()
    assert json.loads((tmp_path / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert json.loads((tmp_path / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]


def test_agent_integration_inspection_reports_absent_destinations(
    tmp_path: Path,
) -> None:
    assert inspect_agent_integrations(tmp_path, ("pi", "codex", "claude")) == (
        AgentIntegrationInspection(
            "pi",
            tmp_path / ".pi/agent/extensions/zpp/index.ts",
            "absent",
        ),
        AgentIntegrationInspection(
            "codex",
            tmp_path / ".codex/hooks.json",
            "absent",
        ),
        AgentIntegrationInspection(
            "claude",
            tmp_path / ".claude/settings.json",
            "absent",
        ),
    )


def test_agent_integration_inspection_ignores_unrelated_native_configuration(
    tmp_path: Path,
) -> None:
    codex = tmp_path / ".codex/hooks.json"
    codex.parent.mkdir()
    codex.write_text(json.dumps({"theme": "dark", "hooks": {}}), encoding="utf-8")

    assert inspect_agent_integrations(tmp_path, ("codex",)) == (
        AgentIntegrationInspection("codex", codex, "absent"),
    )


def test_agent_integration_inspection_recognizes_current_managed_integrations(
    tmp_path: Path,
) -> None:
    apply_mutation_plan(plan_agent_integrations(tmp_path, ("pi", "codex", "claude")))

    assert tuple(
        item.status
        for item in inspect_agent_integrations(tmp_path, ("pi", "codex", "claude"))
    ) == ("current", "current", "current")


def test_agent_integration_inspection_recognizes_exact_historical_hook(
    tmp_path: Path,
) -> None:
    apply_mutation_plan(plan_agent_integrations(tmp_path, ("claude",)))
    destination = tmp_path / ".claude/settings.json"
    destination.write_text(
        destination.read_text(encoding="utf-8").replace(
            "zpp resolve --agent claude",
            "zpp resolve",
        ),
        encoding="utf-8",
    )

    assert inspect_agent_integrations(tmp_path, ("claude",)) == (
        AgentIntegrationInspection("claude", destination, "refreshable"),
    )


def test_agent_integration_inspection_recognizes_partial_managed_hooks(
    tmp_path: Path,
) -> None:
    apply_mutation_plan(plan_agent_integrations(tmp_path, ("codex",)))
    destination = tmp_path / ".codex/hooks.json"
    document = json.loads(destination.read_text(encoding="utf-8"))
    del document["hooks"]["PreToolUse"]
    destination.write_text(json.dumps(document), encoding="utf-8")

    assert inspect_agent_integrations(tmp_path, ("codex",))[0].status == "refreshable"


@pytest.mark.parametrize(
    "source",
    (
        "not-json",
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "wrong",
                            "hooks": [{"type": "command", "command": "zpp resolve"}],
                        }
                    ]
                }
            }
        ),
    ),
)
def test_agent_integration_inspection_reports_malformed_or_claiming_json_as_conflict(
    tmp_path: Path,
    source: str,
) -> None:
    destination = tmp_path / ".codex/hooks.json"
    destination.parent.mkdir()
    destination.write_text(source, encoding="utf-8")

    inspection = inspect_agent_integrations(tmp_path, ("codex",))[0]

    assert inspection.status == "conflict"
    assert inspection.reason


def test_agent_integration_inspection_reports_unmanaged_pi_extension_as_conflict(
    tmp_path: Path,
) -> None:
    destination = tmp_path / ".pi/agent/extensions/zpp/index.ts"
    destination.parent.mkdir(parents=True)
    destination.write_text("unmanaged\n", encoding="utf-8")

    inspection = inspect_agent_integrations(tmp_path, ("pi",))[0]

    assert inspection.status == "conflict"
    assert inspection.reason == "unmanaged Pi extension"
