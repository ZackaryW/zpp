from pathlib import Path

import pytest

from zpp.utils.codespace_claims import (
    CodespaceClaimConflictError,
    transition_codespace_claim,
)
from zpp.utils.codespace_models import (
    CodespaceClaim,
    CodespaceIndex,
    CodespaceMember,
    ReleasedCheckoutDebt,
    ReleasedCodespace,
)


def _member(root: Path, key: str, *, access: str = "writable") -> CodespaceMember:
    return CodespaceMember(
        name=root.name,
        original_path=root,
        effective_path=root,
        checkout_key=key,
        commit=f"commit-{key}",
        kind="project",
        access=access,
    )


def _claim(instance: str, *members: CodespaceMember) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance,
        snapshot_key=f"snapshot-{instance}",
        members=members,
    )


def test_transition_atomically_replaces_identity_and_retains_optional_debt(
    tmp_path: Path,
) -> None:
    shared = _member(tmp_path / "shared", "shared", access="read_only")
    current = _claim("current", _member(tmp_path / "current", "current"), shared)
    successor = _claim(
        "successor",
        _member(tmp_path / "current", "current"),
        shared,
        _member(tmp_path / "added", "added"),
    )
    released = ReleasedCodespace(
        instance_id="current",
        debts=(
            ReleasedCheckoutDebt(
                original_path=tmp_path / "generated",
                effective_path=tmp_path / "generated-current",
                checkout_key="generated",
                branch="zpp/current/0",
            ),
        ),
    )
    other = _claim(
        "other",
        _member(tmp_path / "other", "other"),
        shared,
    )
    index = CodespaceIndex(claims={"current": current, "other": other})

    transitioned = transition_codespace_claim(index, current, successor, released)

    assert set(transitioned.claims) == {"successor", "other"}
    assert transitioned.claims["successor"] == successor
    assert transitioned.released["current"] == released
    assert index.claims["current"] == current and "successor" not in index.claims


def test_transition_rechecks_expected_state_and_writable_conflicts(
    tmp_path: Path,
) -> None:
    current = _claim("current", _member(tmp_path / "current", "current"))
    advanced = current.model_copy(update={"snapshot_key": "advanced"})
    owner = _claim("owner", _member(tmp_path / "owner", "shared"))
    successor = _claim("successor", _member(tmp_path / "successor", "shared"))
    index = CodespaceIndex(claims={"current": advanced, "owner": owner})

    with pytest.raises(ValueError, match="changed since planning"):
        transition_codespace_claim(index, current, successor, None)
    with pytest.raises(CodespaceClaimConflictError):
        transition_codespace_claim(
            CodespaceIndex(claims={"current": current, "owner": owner}),
            current,
            successor,
            None,
        )


def test_transition_without_generated_debt_leaves_no_released_history(
    tmp_path: Path,
) -> None:
    current = _claim("current", _member(tmp_path / "current", "current"))
    successor = _claim("successor", _member(tmp_path / "successor", "successor"))

    transitioned = transition_codespace_claim(
        CodespaceIndex(claims={"current": current}),
        current,
        successor,
        None,
    )

    assert transitioned.claims == {"successor": successor}
    assert transitioned.released == {}
