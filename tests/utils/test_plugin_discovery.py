import json
from pathlib import Path

import pytest

from zpp.utils.models import ManagedStateError
from zpp.utils.plugin_discovery import (
    ActivePlugin,
    discover_active_plugins,
    parse_claude_plugin_list,
    parse_codex_plugin_list,
    parse_pi_plugin_list,
)
from zpp.utils.processes import ProcessResult


def test_editor_plugin_outputs_normalize_only_active_roots(tmp_path: Path) -> None:
    codex_active = tmp_path / ".codex" / "plugins" / "cache" / "market" / "alpha" / "1.2.0"
    codex_active.mkdir(parents=True)
    codex = parse_codex_plugin_list(
        json.dumps(
            {
                "installed": [
                    {
                        "pluginId": "alpha@market",
                        "name": "alpha",
                        "marketplaceName": "market",
                        "version": "1.2.0",
                        "installed": True,
                        "enabled": True,
                    },
                    {
                        "pluginId": "disabled@market",
                        "name": "disabled",
                        "marketplaceName": "market",
                        "version": "1.0.0",
                        "installed": True,
                        "enabled": False,
                    },
                ],
                "available": [{"pluginId": "available@market"}],
            }
        ),
        home=tmp_path,
    )

    claude_root = tmp_path / ".claude" / "plugins" / "cache" / "market" / "beta" / "2.0.0"
    claude_root.mkdir(parents=True)
    claude = parse_claude_plugin_list(
        json.dumps(
            [
                {
                    "id": "beta@market",
                    "version": "2.0.0",
                    "enabled": True,
                    "installPath": str(claude_root),
                },
                {
                    "id": "disabled@market",
                    "version": "2.0.0",
                    "enabled": False,
                    "installPath": str(claude_root.parent / "disabled"),
                },
            ]
        )
    )

    pi_root = tmp_path / ".pi" / "agent" / "npm" / "node_modules" / "gamma"
    pi_root.mkdir(parents=True)
    pi = parse_pi_plugin_list(f"User packages:\n  npm:gamma@3.1.0\n    {pi_root}\n")

    assert codex == (ActivePlugin("codex", "alpha@market", "1.2.0", codex_active.resolve()),)
    assert claude == (ActivePlugin("claude", "beta@market", "2.0.0", claude_root.resolve()),)
    assert pi == (ActivePlugin("pi", "npm:gamma", "3.1.0", pi_root.resolve()),)


def test_discovery_invokes_only_the_selected_agent_and_sorts_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / ".codex" / "plugins" / "cache" / "market" / "alpha" / "1"
    second = tmp_path / ".codex" / "plugins" / "cache" / "market" / "zeta" / "1"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    payload = json.dumps(
        {
            "installed": [
                {"pluginId": "zeta@market", "name": "zeta", "marketplaceName": "market", "version": "1", "installed": True, "enabled": True},
                {"pluginId": "alpha@market", "name": "alpha", "marketplaceName": "market", "version": "1", "installed": True, "enabled": True},
            ],
            "available": [],
        }
    )
    calls: list[tuple[tuple[str, ...], Path | None]] = []

    def fake_run(argv, *, cwd=None, env=None):
        calls.append((tuple(argv), cwd))
        return ProcessResult(tuple(argv), 0, payload, "")

    monkeypatch.setattr("zpp.utils.plugin_discovery.run_process", fake_run)

    plugins = discover_active_plugins("codex", home=tmp_path, target=tmp_path)

    assert [plugin.identity for plugin in plugins] == ["alpha@market", "zeta@market"]
    assert calls == [(('codex', 'plugin', 'list', '--json'), tmp_path)]


@pytest.mark.parametrize(
    "payload",
    (
        "not-json",
        json.dumps(
            {
                "installed": [
                    {
                        "pluginId": "missing-fields",
                        "installed": True,
                        "enabled": True,
                    }
                ]
            }
        ),
        json.dumps(
            {
                "installed": [
                    {"pluginId": "same", "name": "one", "marketplaceName": "market", "version": "1", "installed": True, "enabled": True},
                    {"pluginId": "same", "name": "two", "marketplaceName": "market", "version": "1", "installed": True, "enabled": True},
                ]
            }
        ),
    ),
)
def test_codex_plugin_output_rejects_malformed_or_duplicate_active_state(
    tmp_path: Path,
    payload: str,
) -> None:
    with pytest.raises(ManagedStateError):
        parse_codex_plugin_list(payload, home=tmp_path)


def test_discovery_rejects_agent_command_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "zpp.utils.plugin_discovery.run_process",
        lambda argv, **kwargs: ProcessResult(tuple(argv), 9, "", "broken"),
    )

    with pytest.raises(ManagedStateError, match="broken"):
        discover_active_plugins("pi", home=tmp_path, target=tmp_path)
