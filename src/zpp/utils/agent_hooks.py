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
        "hooks": [{"type": "command", "command": "zpp resolve --agent codex"}],
    }


def claude_session_start_hook() -> ClaudeHookRecord:
    return {
        "matcher": "startup|resume|clear|compact|fork",
        "hooks": [{"type": "command", "command": "zpp resolve --agent claude"}],
    }


def codex_pre_tool_use_hook() -> CodexHookRecord:
    return {
        "matcher": "Bash|apply_patch|Edit|Write",
        "hooks": [
            {
                "type": "command",
                "command": "zpp codespace guard --agent codex",
            }
        ],
    }


def claude_pre_tool_use_hook() -> ClaudeHookRecord:
    return {
        "matcher": "Bash|Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
            {
                "type": "command",
                "command": "zpp codespace guard --agent claude",
            }
        ],
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

    expected_command = _managed_command(expected)
    expected_kind = _managed_command_kind(expected_command)
    expected_event = "SessionStart" if expected_kind == "resolve" else "PreToolUse"
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
                command = handler.get("command")
                if (
                    isinstance(command, str)
                    and _managed_command_kind(command) == expected_kind
                ):
                    claims.append((event, group))

    if claims:
        if len(claims) == 1 and claims[0] == (expected_event, expected):
            return result
        raise ManagedStateError(
            f"a non-identical native hook claims {expected_command!r}"
        )

    event_groups = hooks.setdefault(expected_event, [])
    if not isinstance(event_groups, list):
        raise ManagedStateError(f"{expected_event} hooks are malformed")
    event_groups.append(deepcopy(expected))
    return result


def _managed_command(expected: dict[str, Any]) -> str:
    handlers = expected.get("hooks")
    if not isinstance(handlers, list) or len(handlers) != 1:
        raise ManagedStateError("managed native hook must have one handler")
    handler = handlers[0]
    if not isinstance(handler, dict) or not isinstance(handler.get("command"), str):
        raise ManagedStateError("managed native hook command is malformed")
    return handler["command"]


def _managed_command_kind(command: str) -> str:
    if command == "zpp resolve" or command.startswith("zpp resolve --agent "):
        return "resolve"
    if command.startswith("zpp codespace guard"):
        return "guard"
    return command
