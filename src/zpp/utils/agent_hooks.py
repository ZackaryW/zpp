from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from zpp.utils.models import ManagedStateError


CodexHookRecord = dict[str, Any]
ClaudeHookRecord = dict[str, Any]


def codex_session_start_hook() -> CodexHookRecord:
    return {
        "matcher": "startup|resume|clear|compact",
        "hooks": [{"type": "command", "command": "zpp resolve"}],
    }


def claude_session_start_hook() -> ClaudeHookRecord:
    return {
        "matcher": "startup|resume|clear|compact|fork",
        "hooks": [{"type": "command", "command": "zpp resolve"}],
    }


def reconcile_codex_hooks(
    document: Mapping[str, Any] | None,
    expected: CodexHookRecord,
) -> dict[str, Any]:
    return _reconcile(document, expected)


def reconcile_claude_settings(
    document: Mapping[str, Any] | None,
    expected: ClaudeHookRecord,
) -> dict[str, Any]:
    return _reconcile(document, expected)


def _reconcile(
    document: Mapping[str, Any] | None,
    expected: dict[str, Any],
) -> dict[str, Any]:
    result = deepcopy(dict(document)) if document is not None else {}
    hooks = result.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ManagedStateError("native hooks value is not an object")

    claims: list[tuple[str, dict[str, Any]]] = []
    for event, groups in hooks.items():
        if not isinstance(event, str) or not isinstance(groups, list):
            raise ManagedStateError("native hook event groups are malformed")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise ManagedStateError("native hook matcher group is malformed")
            for handler in group["hooks"]:
                if not isinstance(handler, dict):
                    raise ManagedStateError("native hook handler is malformed")
                if handler.get("command") == "zpp resolve":
                    claims.append((event, group))

    if claims:
        if len(claims) == 1 and claims[0] == ("SessionStart", expected):
            return result
        raise ManagedStateError("a non-identical native hook claims 'zpp resolve'")

    session_start = hooks.setdefault("SessionStart", [])
    if not isinstance(session_start, list):
        raise ManagedStateError("SessionStart hooks are malformed")
    session_start.append(deepcopy(expected))
    return result
