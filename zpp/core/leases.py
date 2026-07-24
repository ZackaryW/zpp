"""Machine-local shared-read/exclusive-write governance leases."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..utils.paths import leases_dir


class LeaseError(RuntimeError):
    pass


class LeaseConflictError(LeaseError):
    def __init__(self, holders: list[dict]):
        self.holders = holders
        labels = ", ".join(f"{h['session_id']}:{h['mode']}" for h in holders)
        super().__init__(f"live governance lease conflict: {labels}")


class StaleLeaseError(LeaseError):
    pass


def _now(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc)


def _stamp(value: datetime) -> str:
    return value.isoformat()


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def canonical_key(root: Path, branch: str) -> dict[str, str]:
    canonical_root = os.path.normcase(str(Path(root).resolve()))
    payload = json.dumps(
        {"root": canonical_root, "branch": branch}, sort_keys=True, separators=(",", ":")
    )
    return {
        "id": hashlib.sha256(payload.encode()).hexdigest(),
        "root": canonical_root,
        "branch": branch,
    }


def _record_path(key: dict) -> Path:
    return leases_dir() / f"{key['id']}.json"


@contextmanager
def _transaction(key: dict):
    directory = leases_dir()
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / f"{key['id']}.lock"
    deadline = time.monotonic() + 2
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LeaseError(f"lease state is busy: {key['id']}")
            time.sleep(0.02)
    try:
        yield
    finally:
        lock.rmdir()


def _read(key: dict) -> dict:
    path = _record_path(key)
    if not path.is_file():
        return {"key": key, "holders": []}
    return json.loads(path.read_text())


def _write(record: dict) -> None:
    path = _record_path(record["key"])
    if not record["holders"]:
        path.unlink(missing_ok=True)
        return
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2, sort_keys=True))
    os.replace(tmp, path)


def _classified(record: dict, now: datetime) -> tuple[list[dict], list[dict]]:
    live, stale = [], []
    for holder in record["holders"]:
        (stale if _parse(holder["expires_at"]) <= now else live).append(holder)
    return live, stale


def status(root: Path, branch: str, *, now: datetime | None = None) -> dict:
    key = canonical_key(root, branch)
    current = _now(now)
    record = _read(key)
    live, stale = _classified(record, current)
    state = "stale" if stale else ("live" if live else "absent")
    return {"state": state, "key": key, "holders": live + stale,
            "live_holders": live, "stale_holders": stale}


def acquire(
    root: Path,
    branch: str,
    mode: str,
    session_id: str,
    *,
    ttl_seconds: int = 300,
    now: datetime | None = None,
) -> dict:
    if mode not in {"read", "write"}:
        raise LeaseError("lease mode must be 'read' or 'write'")
    key = canonical_key(root, branch)
    current = _now(now)
    with _transaction(key):
        record = _read(key)
        live, stale = _classified(record, current)
        if stale:
            raise StaleLeaseError("stale lease requires explicit recovery")
        others = [holder for holder in live if holder["session_id"] != session_id]
        if mode == "write" and others:
            raise LeaseConflictError(others)
        if mode == "read" and any(holder["mode"] == "write" for holder in others):
            raise LeaseConflictError(
                [holder for holder in others if holder["mode"] == "write"]
            )
        existing = next(
            (holder for holder in live if holder["session_id"] == session_id), None
        )
        expires = current + timedelta(seconds=ttl_seconds)
        if existing:
            existing["mode"] = mode
            existing["renewed_at"] = _stamp(current)
            existing["expires_at"] = _stamp(expires)
            holder = existing
        else:
            holder = {
                "session_id": session_id,
                "mode": mode,
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "acquired_at": _stamp(current),
                "renewed_at": _stamp(current),
                "expires_at": _stamp(expires),
            }
            live.append(holder)
        record["holders"] = live
        _write(record)
    return {"state": "live", "key": key, "holder": holder}


def renew(
    root: Path,
    branch: str,
    session_id: str,
    *,
    ttl_seconds: int = 300,
    now: datetime | None = None,
) -> dict:
    key = canonical_key(root, branch)
    current = _now(now)
    with _transaction(key):
        record = _read(key)
        holder = next(
            (item for item in record["holders"] if item["session_id"] == session_id),
            None,
        )
        if holder is None:
            raise LeaseError(f"session '{session_id}' holds no lease")
        if _parse(holder["expires_at"]) <= current:
            raise StaleLeaseError("stale lease requires explicit recovery")
        holder["renewed_at"] = _stamp(current)
        holder["expires_at"] = _stamp(current + timedelta(seconds=ttl_seconds))
        _write(record)
    return {"state": "live", "key": key, "holder": holder}


def release(root: Path, branch: str, session_id: str) -> dict:
    key = canonical_key(root, branch)
    with _transaction(key):
        record = _read(key)
        remaining = [
            holder for holder in record["holders"] if holder["session_id"] != session_id
        ]
        released = len(remaining) != len(record["holders"])
        record["holders"] = remaining
        _write(record)
    return {"key": key, "session_id": session_id, "released": released}


def recover_stale(
    root: Path,
    branch: str,
    *,
    confirm: bool,
    now: datetime | None = None,
) -> dict:
    key = canonical_key(root, branch)
    current = _now(now)
    with _transaction(key):
        record = _read(key)
        live, stale = _classified(record, current)
        if not stale:
            return {"key": key, "recovered": []}
        if not confirm:
            raise StaleLeaseError("pass explicit confirmation to recover stale leases")
        record["holders"] = live
        _write(record)
    return {"key": key, "recovered": [holder["session_id"] for holder in stale]}
