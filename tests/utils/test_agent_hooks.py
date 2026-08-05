from copy import deepcopy

import pytest

from zpp.utils.agent_hooks import (
    claude_pre_tool_use_hook,
    claude_session_start_hook,
    codex_pre_tool_use_hook,
    codex_session_start_hook,
    reconcile_claude_settings,
    reconcile_codex_hooks,
)
from zpp.utils.models import ManagedStateError


def test_native_hook_reconciliation_is_exact_idempotent_and_non_mutating() -> None:
    codex_expected = codex_session_start_hook()
    claude_expected = claude_session_start_hook()
    codex_source = {"description": "保留", "hooks": {"Stop": []}}
    claude_source = {"theme": "dark", "hooks": {"PreToolUse": []}}
    codex_original = deepcopy(codex_source)
    claude_original = deepcopy(claude_source)

    codex = reconcile_codex_hooks(codex_source, codex_expected)
    claude = reconcile_claude_settings(claude_source, claude_expected)

    assert codex["hooks"]["SessionStart"] == [codex_expected]
    assert claude["hooks"]["SessionStart"] == [claude_expected]
    assert reconcile_codex_hooks(codex, codex_expected) == codex
    assert reconcile_claude_settings(claude, claude_expected) == claude
    assert codex_source == codex_original and claude_source == claude_original


def test_native_session_hooks_pass_their_own_agent_identity() -> None:
    codex = codex_session_start_hook()
    claude = claude_session_start_hook()

    assert codex["hooks"] == [
        {"type": "command", "command": "zpp resolve --agent codex"}
    ]
    assert claude["hooks"] == [
        {"type": "command", "command": "zpp resolve --agent claude"}
    ]


def test_native_hook_reconciliation_rejects_a_competing_zpp_command() -> None:
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

    with pytest.raises(ManagedStateError):
        reconcile_codex_hooks(conflicting, codex_session_start_hook())


def test_native_hook_reconciliation_upgrades_only_the_exact_historical_record() -> None:
    expected = claude_session_start_hook()
    historical = deepcopy(expected)
    historical["hooks"][0]["command"] = "zpp resolve"
    source = {"theme": "dark", "hooks": {"SessionStart": [historical]}}

    reconciled = reconcile_claude_settings(source, expected)

    assert reconciled["hooks"]["SessionStart"] == [expected]
    assert reconciled["theme"] == "dark"


def test_native_hook_reconciliation_adds_one_managed_pre_tool_guard() -> None:
    codex = reconcile_codex_hooks(None, codex_session_start_hook())
    codex = reconcile_codex_hooks(codex, codex_pre_tool_use_hook())
    claude = reconcile_claude_settings(None, claude_session_start_hook())
    claude = reconcile_claude_settings(claude, claude_pre_tool_use_hook())

    assert codex["hooks"]["PreToolUse"] == [codex_pre_tool_use_hook()]
    assert claude["hooks"]["PreToolUse"] == [claude_pre_tool_use_hook()]
    assert reconcile_codex_hooks(codex, codex_pre_tool_use_hook()) == codex
    assert reconcile_claude_settings(claude, claude_pre_tool_use_hook()) == claude


def test_native_hook_reconciliation_rejects_a_competing_guard_record() -> None:
    conflicting = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "zpp codespace guard --agent codex",
                        }
                    ],
                }
            ]
        }
    }

    with pytest.raises(ManagedStateError, match="non-identical"):
        reconcile_codex_hooks(conflicting, codex_pre_tool_use_hook())
