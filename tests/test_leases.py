from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from zpp.core import leases


NOW = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


def test_canonical_key_is_stable_for_equivalent_roots(tmp_path):
    root = tmp_path / "governance"
    root.mkdir()

    first = leases.canonical_key(root, "project-a/feature-x")
    second = leases.canonical_key(root / ".", "project-a/feature-x")

    assert first == second
    assert first["branch"] == "project-a/feature-x"
    assert len(first["id"]) == 64


def test_two_readers_share_one_branch(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()

    one = leases.acquire(root, "project-a/feature-x", "read", "session-one", now=NOW)
    two = leases.acquire(root, "project-a/feature-x", "read", "session-two", now=NOW)

    assert one["state"] == two["state"] == "live"
    assert {h["session_id"] for h in leases.status(root, "project-a/feature-x", now=NOW)["holders"]} == {
        "session-one",
        "session-two",
    }


def test_second_writer_is_blocked_with_holder_evidence(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()
    leases.acquire(root, "project-a/feature-x", "write", "session-one", now=NOW)

    with pytest.raises(leases.LeaseConflictError) as caught:
        leases.acquire(root, "project-a/feature-x", "write", "session-two", now=NOW)

    assert caught.value.holders[0]["session_id"] == "session-one"


def test_writers_on_different_branches_do_not_conflict(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()

    one = leases.acquire(root, "project-a/feature-x", "write", "one", now=NOW)
    two = leases.acquire(root, "project-a/feature-y", "write", "two", now=NOW)

    assert one["key"]["id"] != two["key"]["id"]


def test_upgrade_requires_reader_exclusivity_and_release_is_idempotent(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()
    leases.acquire(root, "main", "read", "one", now=NOW)
    leases.acquire(root, "main", "read", "two", now=NOW)

    with pytest.raises(leases.LeaseConflictError):
        leases.acquire(root, "main", "write", "one", now=NOW)

    assert leases.release(root, "main", "two")["released"] is True
    upgraded = leases.acquire(root, "main", "write", "one", now=NOW)
    assert upgraded["holder"]["mode"] == "write"
    assert leases.release(root, "main", "one")["released"] is True
    assert leases.release(root, "main", "one")["released"] is False


def test_stale_lease_requires_explicit_recovery(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()
    leases.acquire(root, "main", "write", "dead", ttl_seconds=30, now=NOW)
    later = NOW + timedelta(seconds=31)

    assert leases.status(root, "main", now=later)["state"] == "stale"
    with pytest.raises(leases.StaleLeaseError):
        leases.acquire(root, "main", "write", "new", now=later)
    with pytest.raises(leases.StaleLeaseError):
        leases.recover_stale(root, "main", confirm=False, now=later)

    recovered = leases.recover_stale(root, "main", confirm=True, now=later)
    assert recovered["recovered"] == ["dead"]
    assert leases.acquire(root, "main", "write", "new", now=later)["state"] == "live"


def test_renew_updates_timestamp(tmp_path, zpp_home):
    root = tmp_path / "governance"
    root.mkdir()
    leases.acquire(root, "main", "read", "one", now=NOW)

    renewed = leases.renew(root, "main", "one", now=NOW + timedelta(seconds=10))

    assert renewed["holder"]["renewed_at"] == "2026-07-24T12:00:10+00:00"

