from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict

from zpp.utils.codespace_models import CodespaceIndex
from zpp.utils.codespace_members import read_only_members, writable_members


AgentName = Literal["pi", "codex", "claude"]
_PATCH_PATH = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)


class UnsupportedGuardTool(ValueError):
    pass


class GuardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["direct_write", "shell"]
    cwd: Path
    target_paths: tuple[Path, ...] = ()


class GuardDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed: bool
    owner_id: str | None = None
    associated_codespace: str | None = None
    reason: str | None = None


def _contains(root: Path, target: Path) -> bool:
    canonical_root = os.path.normcase(str(root.resolve()))
    canonical_target = os.path.normcase(str(target.resolve()))
    try:
        return os.path.commonpath((canonical_root, canonical_target)) == canonical_root
    except ValueError:
        return False


def _writable_owner(index: CodespaceIndex, target: Path) -> str | None:
    owners = {
        claim.instance_id
        for claim in index.claims.values()
        if any(
            _contains(member.effective_path, target)
            for member in writable_members(claim.members)
        )
    }
    if len(owners) > 1:
        raise ValueError("target belongs to multiple active codespace claims")
    return next(iter(owners), None)


def evaluate_codespace_guard(
    request: GuardRequest,
    index: CodespaceIndex,
    *,
    associated_codespace: str | None = None,
) -> GuardDecision:
    current = associated_codespace or _writable_owner(index, request.cwd)
    if current is not None and current not in index.claims:
        raise ValueError(f"associated codespace does not exist: {current}")
    if request.kind == "shell":
        return GuardDecision(allowed=True, associated_codespace=current)

    for target in request.target_paths:
        if current is not None and any(
            _contains(member.effective_path, target)
            for member in read_only_members(index.claims[current].members)
        ):
            return GuardDecision(
                allowed=False,
                associated_codespace=current,
                reason=f"target is read-only in codespace {current}: {target}",
            )
        owner = _writable_owner(index, target)
        if owner is not None and owner != current:
            return GuardDecision(
                allowed=False,
                owner_id=owner,
                associated_codespace=current,
                reason=f"target is claimed by codespace {owner}: {target}",
            )
    return GuardDecision(allowed=True, associated_codespace=current)


def _object(value: object, description: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{description} must be an object")
    return value


def _path(cwd: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("supported direct-write tool has no target path")
    candidate = Path(value)
    return (candidate if candidate.is_absolute() else cwd / candidate).resolve()


def decode_agent_guard_request(
    agent: AgentName,
    payload: Mapping[str, object],
) -> GuardRequest:
    cwd_value = payload.get("cwd")
    if not isinstance(cwd_value, str) or not cwd_value:
        raise ValueError("agent guard payload has no working directory")
    cwd = Path(cwd_value).resolve()
    tool_name = payload.get("toolName" if agent == "pi" else "tool_name")
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("agent guard payload has no tool name")
    tool_input = _object(
        payload.get("input" if agent == "pi" else "tool_input"),
        "agent tool input",
    )

    if tool_name.lower() in {"bash", "shell"}:
        return GuardRequest(kind="shell", cwd=cwd)

    targets: tuple[Path, ...]
    if agent == "codex" and tool_name == "apply_patch":
        command = tool_input.get("command")
        if not isinstance(command, str):
            raise ValueError("Codex apply_patch input has no command")
        paths = _PATCH_PATH.findall(command)
        if not paths:
            raise ValueError("Codex apply_patch input has no target path")
        targets = tuple(_path(cwd, path) for path in paths)
    elif tool_name in {"Write", "Edit", "MultiEdit", "write", "edit"}:
        targets = (_path(cwd, tool_input.get("file_path", tool_input.get("path"))),)
    elif tool_name in {"NotebookEdit", "notebook_edit"}:
        targets = (_path(cwd, tool_input.get("notebook_path")),)
    else:
        raise UnsupportedGuardTool(f"unsupported agent guard tool: {tool_name}")
    return GuardRequest(kind="direct_write", cwd=cwd, target_paths=targets)


def encode_agent_guard_decision(
    agent: AgentName,
    decision: GuardDecision,
) -> Mapping[str, object]:
    if decision.allowed:
        return {}
    reason = decision.reason or "write blocked by an active ZPP codespace claim"
    if agent == "pi":
        return {"block": True, "reason": reason}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
