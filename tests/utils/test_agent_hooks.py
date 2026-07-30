from copy import deepcopy

import pytest

from zpp.utils.agent_hooks import (
    claude_session_start_hook,
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
