from pathlib import Path

import pytest

from zpp.utils.codespace_guard import (
    GuardDecision,
    GuardRequest,
    UnsupportedGuardTool,
    decode_agent_guard_request,
    encode_agent_guard_decision,
    evaluate_codespace_guard,
)
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember


def _claim(root: Path, instance_id: str) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance_id,
        snapshot_key=f"snapshot-{instance_id}",
        members=(
            CodespaceMember(
                name=instance_id,
                original_path=root,
                effective_path=root,
                checkout_key=f"key-{instance_id}",
                commit="abc",
                kind="project",
            ),
        ),
    )


def test_direct_write_guard_blocks_only_another_claims_explicit_target(
    tmp_path: Path,
) -> None:
    current_root = tmp_path / "current"
    other_root = tmp_path / "other"
    index = CodespaceIndex(
        claims={
            "current": _claim(current_root, "current"),
            "other": _claim(other_root, "other"),
        }
    )

    blocked = evaluate_codespace_guard(
        GuardRequest(
            kind="direct_write",
            cwd=current_root,
            target_paths=(other_root / "nested" / "file.py",),
        ),
        index,
    )
    allowed = evaluate_codespace_guard(
        GuardRequest(
            kind="direct_write",
            cwd=current_root,
            target_paths=(current_root / "file.py", tmp_path / "unclaimed.txt"),
        ),
        index,
    )

    assert not blocked.allowed and blocked.owner_id == "other"
    assert allowed.allowed and allowed.associated_codespace == "current"


@pytest.mark.parametrize(
    ("agent", "payload"),
    [
        (
            "codex",
            {
                "cwd": "ROOT",
                "tool_name": "apply_patch",
                "tool_input": {"command": "*** Update File: target.py"},
            },
        ),
        (
            "claude",
            {
                "cwd": "ROOT",
                "tool_name": "Write",
                "tool_input": {"file_path": "target.py"},
            },
        ),
        (
            "pi",
            {
                "cwd": "ROOT",
                "toolName": "write",
                "input": {"path": "target.py"},
            },
        ),
    ],
)
def test_native_guard_adapters_normalize_and_block_direct_writes(
    tmp_path: Path,
    agent: str,
    payload: dict[str, object],
) -> None:
    payload["cwd"] = str(tmp_path)

    request = decode_agent_guard_request(agent, payload)
    output = encode_agent_guard_decision(
        agent,
        GuardDecision(allowed=False, owner_id="owner", reason="claimed"),
    )

    assert request == GuardRequest(
        kind="direct_write",
        cwd=tmp_path,
        target_paths=((tmp_path / "target.py").resolve(),),
    )
    if agent == "pi":
        assert output == {"block": True, "reason": "claimed"}
    else:
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_shell_guard_verifies_cwd_without_parsing_the_command(tmp_path: Path) -> None:
    claim = _claim(tmp_path / "project", "current")
    request = decode_agent_guard_request(
        "codex",
        {
            "cwd": str(tmp_path / "project"),
            "tool_name": "Bash",
            "tool_input": {"command": "anything can appear here"},
        },
    )

    decision = evaluate_codespace_guard(
        request,
        CodespaceIndex(claims={"current": claim}),
    )

    assert request.kind == "shell" and request.target_paths == ()
    assert decision.allowed and decision.associated_codespace == "current"
    assert encode_agent_guard_decision("codex", decision) == {}


def test_malformed_supported_direct_write_payload_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no target path") as caught:
        decode_agent_guard_request(
            "codex",
            {
                "cwd": str(tmp_path),
                "tool_name": "apply_patch",
                "tool_input": {"command": "*** Begin Patch\n*** End Patch"},
            },
        )

    assert not isinstance(caught.value, UnsupportedGuardTool)


@pytest.mark.parametrize(
    ("agent", "payload"),
    [
        (
            "codex",
            {"tool_name": "read_file", "tool_input": {}},
        ),
        (
            "claude",
            {"tool_name": "Read", "tool_input": {}},
        ),
        (
            "pi",
            {"toolName": "read", "input": {}},
        ),
    ],
)
def test_unsupported_agent_tools_are_outside_the_guard_contract(
    tmp_path: Path,
    agent: str,
    payload: dict[str, object],
) -> None:
    payload["cwd"] = str(tmp_path)

    with pytest.raises(UnsupportedGuardTool, match="unsupported agent guard tool"):
        decode_agent_guard_request(agent, payload)
