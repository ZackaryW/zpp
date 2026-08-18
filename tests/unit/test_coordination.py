from pathlib import Path

import pytest

from zpp.core.coordination import (
    AffectedClaim,
    ClosureConflict,
    ClosureReport,
    CoordinationError,
    DestructiveOperation,
    closure_fingerprint,
    derive_session_identity,
    derive_worktree_identity,
    parse_affected_claim,
    require_destructive_authority,
)


def test_worktree_identity_is_stable_for_one_common_dir(tmp_path: Path) -> None:
    common = tmp_path / "project" / ".git"

    first = derive_worktree_identity(common)
    second = derive_worktree_identity(common)

    assert first == second
    assert first.repository_id
    assert first.authority_id
    assert first.repository_id != first.authority_id


def test_worktree_identity_differs_across_worktrees(tmp_path: Path) -> None:
    left = derive_worktree_identity(tmp_path / "left" / ".git")
    right = derive_worktree_identity(tmp_path / "right" / ".git")

    assert left.repository_id != right.repository_id
    assert left.authority_id != right.authority_id


def test_worktree_identity_ignores_separator_form(tmp_path: Path) -> None:
    common = tmp_path / "project" / ".git"

    assert derive_worktree_identity(common) == derive_worktree_identity(
        Path(common.as_posix())
    )


def test_worktree_identity_carries_a_readable_prefix(tmp_path: Path) -> None:
    identity = derive_worktree_identity(tmp_path / "My Project" / ".git")

    assert identity.repository_id.startswith("my-project-")


def test_session_identity_defaults_to_the_worktree(tmp_path: Path) -> None:
    worktree = derive_worktree_identity(tmp_path / "project" / ".git")

    assert derive_session_identity(worktree) == derive_session_identity(worktree)


def test_named_session_identity_is_distinct_from_the_default(tmp_path: Path) -> None:
    worktree = derive_worktree_identity(tmp_path / "project" / ".git")

    default = derive_session_identity(worktree)
    named = derive_session_identity(worktree, "review")

    assert named != default
    assert named == derive_session_identity(worktree, "review")


def test_distinct_session_names_are_distinct(tmp_path: Path) -> None:
    worktree = derive_worktree_identity(tmp_path / "project" / ".git")

    assert derive_session_identity(worktree, "a") != derive_session_identity(
        worktree, "b"
    )


def test_empty_session_name_is_rejected(tmp_path: Path) -> None:
    worktree = derive_worktree_identity(tmp_path / "project" / ".git")

    with pytest.raises(CoordinationError):
        derive_session_identity(worktree, "   ")


def test_claim_collapses_duplicates_and_keeps_first_seen_order() -> None:
    claim = parse_affected_claim(("beta", "alpha", "beta"), ("one", "one"))

    assert claim == AffectedClaim(("beta", "alpha"), ("one",))


def test_empty_claim_is_rejected() -> None:
    with pytest.raises(CoordinationError):
        parse_affected_claim((), ())


def test_blank_claim_identifier_is_rejected() -> None:
    with pytest.raises(CoordinationError):
        parse_affected_claim(("alpha", "  "), ())


def _report(*authority_ids: str, lockable: bool = True) -> ClosureReport:
    return ClosureReport(
        lockable=lockable,
        authority_ids=authority_ids,
        conflicts=(),
        blockers=(),
        promotion_issues=(),
    )


def test_closure_fingerprint_is_stable_for_equal_membership() -> None:
    assert closure_fingerprint(_report("a", "b")) == closure_fingerprint(
        _report("a", "b")
    )


def test_closure_fingerprint_ignores_membership_order() -> None:
    assert closure_fingerprint(_report("a", "b")) == closure_fingerprint(
        _report("b", "a")
    )


def test_closure_fingerprint_changes_with_membership() -> None:
    assert closure_fingerprint(_report("a", "b")) != closure_fingerprint(
        _report("a", "b", "c")
    )


def test_closure_fingerprint_changes_when_a_conflict_appears() -> None:
    conflicted = ClosureReport(
        lockable=False,
        authority_ids=("a",),
        conflicts=(ClosureConflict("a", "other"),),
        blockers=("other",),
        promotion_issues=(),
    )

    assert closure_fingerprint(conflicted) != closure_fingerprint(_report("a"))


@pytest.mark.parametrize("operation", list(DestructiveOperation))
def test_destructive_authority_is_required(operation: DestructiveOperation) -> None:
    with pytest.raises(CoordinationError) as error:
        require_destructive_authority(operation, None, ("space-1",))

    assert operation.value in str(error.value)


def test_destructive_authority_rejects_a_blank_argument() -> None:
    with pytest.raises(CoordinationError):
        require_destructive_authority(DestructiveOperation.CLEANUP, "  ", ("space-1",))


def test_destructive_authority_requires_named_targets() -> None:
    with pytest.raises(CoordinationError):
        require_destructive_authority(DestructiveOperation.CLEANUP, "confirm", ())


def test_destructive_authority_accepts_a_named_authorized_operation() -> None:
    require_destructive_authority(
        DestructiveOperation.CLEANUP, "confirm", ("space-1", "repo-1")
    )
