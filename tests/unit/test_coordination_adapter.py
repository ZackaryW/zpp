import subprocess
from pathlib import Path

import pytest
from openlease import OpenLease

from zpp.core.coordination import (
    CoordinationError,
    closure_fingerprint,
    parse_affected_claim,
)
from zpp.utils.coordination import OpenLeaseCoordination


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def worktree(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "--quiet", "-m", "base")
    return root


@pytest.fixture
def coordination(tmp_path: Path) -> OpenLeaseCoordination:
    return OpenLeaseCoordination(OpenLease(tmp_path / "state"))


def test_registration_creates_repository_and_worktree_authority(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    identity = coordination.ensure_registered(worktree)

    state = coordination._lifecycle.snapshot()
    assert [item.identifier for item in state.repositories] == [identity.repository_id]
    assert [item.identifier for item in state.authorities] == [identity.authority_id]


def test_registration_is_idempotent(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    first = coordination.ensure_registered(worktree)
    second = coordination.ensure_registered(worktree)

    state = coordination._lifecycle.snapshot()
    assert first == second
    assert len(state.repositories) == 1
    assert len(state.authorities) == 1


def test_registration_declares_no_relationship(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    coordination.ensure_registered(worktree)

    state = coordination._lifecycle.snapshot()
    assert state.parents == ()
    assert state.dependencies == ()


def test_session_is_reused_across_invocations(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    first = coordination.establish_session(worktree)
    second = coordination.establish_session(worktree)

    assert first == second
    assert len(coordination._lifecycle.snapshot().spaces) == 1


def test_named_session_is_distinct_and_does_not_displace_the_default(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    default = coordination.establish_session(worktree)
    named = coordination.establish_session(worktree, "review")

    assert named.space_id != default.space_id
    assert coordination.establish_session(worktree).space_id == default.space_id


def test_closure_requires_a_declared_claim(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)

    with pytest.raises(Exception) as error:
        coordination.resolve_closure(session.space_id)

    assert "affected claim" in str(error.value)


def test_declared_claim_resolves_a_lockable_closure(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)
    coordination.declare_claim(
        session.space_id, parse_affected_claim((), (session.worktree.authority_id,))
    )

    report = coordination.resolve_closure(session.space_id)

    assert report.lockable is True
    assert report.authority_ids == (session.worktree.authority_id,)
    assert report.conflicts == ()


def test_permit_is_acquired_against_the_reported_closure(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)
    coordination.declare_claim(
        session.space_id, parse_affected_claim((), (session.worktree.authority_id,))
    )
    report = coordination.resolve_closure(session.space_id)

    grant = coordination.acquire_permit(session.space_id, closure_fingerprint(report))

    assert grant.authority_ids == (session.worktree.authority_id,)
    leases = coordination._lifecycle.snapshot().leases
    assert [item.owner_id for item in leases] == [session.space_id]


def test_stale_closure_is_refused(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)
    coordination.declare_claim(
        session.space_id, parse_affected_claim((), (session.worktree.authority_id,))
    )
    stale = closure_fingerprint(coordination.resolve_closure(session.space_id))
    coordination.declare_claim(
        session.space_id,
        parse_affected_claim((session.worktree.repository_id,), ()),
    )

    with pytest.raises(CoordinationError) as error:
        coordination.acquire_permit(session.space_id, stale)

    assert "changed" in str(error.value)
    assert coordination._lifecycle.snapshot().leases == ()


def test_second_session_is_blocked_by_a_held_permit(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    holder = coordination.establish_session(worktree)
    coordination.declare_claim(
        holder.space_id, parse_affected_claim((), (holder.worktree.authority_id,))
    )
    coordination.acquire_permit(
        holder.space_id,
        closure_fingerprint(coordination.resolve_closure(holder.space_id)),
    )

    other = coordination.establish_session(worktree, "review")
    coordination.declare_claim(
        other.space_id, parse_affected_claim((), (other.worktree.authority_id,))
    )
    report = coordination.resolve_closure(other.space_id)

    assert report.lockable is False
    assert report.blockers == (holder.space_id,)


def test_release_drops_the_held_leases(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)
    coordination.declare_claim(
        session.space_id, parse_affected_claim((), (session.worktree.authority_id,))
    )
    coordination.acquire_permit(
        session.space_id,
        closure_fingerprint(coordination.resolve_closure(session.space_id)),
    )

    coordination.release_permit(session.space_id)

    assert coordination._lifecycle.snapshot().leases == ()


def test_forced_release_requires_explicit_authority(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)

    with pytest.raises(CoordinationError) as error:
        coordination.force_release(session.space_id, None)

    assert "explicit authority" in str(error.value)


def test_cleanup_requires_explicit_authority(
    coordination: OpenLeaseCoordination, worktree: Path
) -> None:
    session = coordination.establish_session(worktree)

    with pytest.raises(CoordinationError):
        coordination.cleanup(session.space_id, session.worktree.repository_id, None)
