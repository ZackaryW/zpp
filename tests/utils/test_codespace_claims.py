from pathlib import Path
import subprocess
import sys

import pytest

from zpp.utils.codespace_claims import (
    CodespaceClaimConflictError,
    claimed_checkout_owners,
    find_matching_codespace_claim,
    register_codespace_claim,
    update_codespace_claim,
)
from zpp.utils.codespace_models import CodespaceClaim, CodespaceIndex, CodespaceMember


def _claim(root: Path, instance_id: str, checkout_key: str) -> CodespaceClaim:
    return CodespaceClaim(
        instance_id=instance_id,
        snapshot_key=f"snapshot-{instance_id}",
        members=(
            CodespaceMember(
                name=instance_id,
                original_path=root,
                effective_path=root,
                checkout_key=checkout_key,
                commit="abc",
                kind="project",
            ),
        ),
    )


def test_claim_registration_reports_owner_and_never_partially_registers(
    tmp_path: Path,
) -> None:
    owner = _claim(tmp_path / "owner", "owner", "shared")
    contender = _claim(tmp_path / "contender", "contender", "shared")
    index = CodespaceIndex(claims={"owner": owner})

    assert claimed_checkout_owners(index, {"shared"})[0].owner_id == "owner"
    with pytest.raises(CodespaceClaimConflictError) as caught:
        register_codespace_claim(index, contender)

    assert caught.value.conflicts[0].checkout_key == "shared"
    assert index == CodespaceIndex(claims={"owner": owner})


def test_claim_matching_uses_the_complete_effective_checkout_key_set(
    tmp_path: Path,
) -> None:
    first = _claim(tmp_path / "first", "first", "key-first").members[0]
    second = _claim(tmp_path / "second", "second", "key-second").members[0]
    claim = CodespaceClaim(
        instance_id="current",
        snapshot_key="original-snapshot",
        members=(first, second),
    )
    index = CodespaceIndex(claims={"current": claim})

    assert find_matching_codespace_claim(
        index,
        [("key-second", "writable"), ("key-first", "writable")],
    ) == claim
    assert find_matching_codespace_claim(index, [("key-first", "writable")]) is None
    assert find_matching_codespace_claim(
        index,
        [
            ("key-first", "writable"),
            ("key-second", "writable"),
            ("key-third", "writable"),
        ],
    ) is None


def test_claim_matching_distinguishes_access_and_uses_source_identity(
    tmp_path: Path,
) -> None:
    generated = _claim(tmp_path / "source", "current", "effective").members[0].model_copy(
        update={
            "source_checkout_key": "source",
            "generated_worktree": True,
            "branch": "zpp/current/0",
        }
    )
    reference = _claim(tmp_path / "reference", "reference", "reference").members[0].model_copy(
        update={"access": "read_only"}
    )
    claim = CodespaceClaim(
        instance_id="current",
        snapshot_key="snapshot",
        members=(generated, reference),
    )
    index = CodespaceIndex(claims={"current": claim})

    assert find_matching_codespace_claim(
        index,
        [("source", "writable"), ("reference", "read_only")],
    ) == claim
    assert find_matching_codespace_claim(
        index,
        [("source", "writable"), ("reference", "writable")],
    ) is None


def test_same_identity_update_requires_the_expected_claim(tmp_path: Path) -> None:
    current = _claim(tmp_path / "current", "current", "key")
    replacement = current.model_copy(update={"snapshot_key": "updated"})
    index = CodespaceIndex(claims={"current": current})

    assert update_codespace_claim(index, current, replacement).claims == {
        "current": replacement
    }
    with pytest.raises(ValueError, match="changed since planning"):
        update_codespace_claim(index, replacement, current)


def test_competing_processes_cannot_both_register_one_checkout(
    tmp_path: Path,
) -> None:
    root = tmp_path / "codespaces"
    script = r'''
import sys
import time
from pathlib import Path
from zpp.utils.codespace_claims import CodespaceClaimConflictError, register_codespace_claim
from zpp.utils.codespace_models import CodespaceClaim, CodespaceMember
from zpp.utils.codespace_state import mutate_codespace_index

root = Path(sys.argv[1])
instance = sys.argv[2]
member_root = root.parent / instance
claim = CodespaceClaim(
    instance_id=instance,
    snapshot_key="snapshot",
    members=(CodespaceMember(
        name=instance,
        original_path=member_root,
        effective_path=member_root,
        checkout_key="shared",
        commit="abc",
        kind="project",
    ),),
)

def register(index):
    time.sleep(0.15)
    return register_codespace_claim(index, claim)

try:
    mutate_codespace_index(root, register)
except CodespaceClaimConflictError:
    raise SystemExit(3)
'''
    processes = [
        subprocess.Popen([sys.executable, "-c", script, str(root), instance])
        for instance in ("first", "second")
    ]

    assert sorted(process.wait(timeout=10) for process in processes) == [0, 3]
