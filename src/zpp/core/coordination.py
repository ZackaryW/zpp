"""Pure coordination primitives for OpenLease topology, sessions, and permits.

This module owns derivation and validation only. It imports no provider and
performs no state mutation, so every rule here is verifiable in isolation.
"""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

_DIGEST_LENGTH = 12
_SLUG_SEPARATORS = re.compile(r"[^a-z0-9]+")


class CoordinationError(ValueError):
    """A coordination input is missing, malformed, or unauthorized."""


@dataclass(frozen=True, slots=True)
class WorktreeIdentity:
    repository_id: str
    authority_id: str


@dataclass(frozen=True, slots=True)
class AffectedClaim:
    repository_ids: tuple[str, ...]
    authority_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClosureConflict:
    authority_id: str
    owner_id: str


@dataclass(frozen=True, slots=True)
class ClosureReport:
    lockable: bool
    authority_ids: tuple[str, ...]
    conflicts: tuple[ClosureConflict, ...]
    blockers: tuple[str, ...]
    promotion_issues: tuple[str, ...]


class DestructiveOperation(StrEnum):
    ABANDON = "abandon"
    CLEANUP = "cleanup"
    HANDOFF = "handoff"
    RECOVER_FORCED = "recover-forced"
    PREPARATION_ROLLBACK = "preparation-rollback"


def _slug(value: str) -> str:
    return _SLUG_SEPARATORS.sub("-", value.lower()).strip("-")


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:_DIGEST_LENGTH]


def derive_worktree_identity(common_dir: Path) -> WorktreeIdentity:
    """Derive stable identifiers for the repository behind one Git common dir.

    The digest uses the POSIX form of the absolute path so the same worktree
    yields one identity regardless of the separator style it was written with.
    """
    absolute = Path(os.path.abspath(os.fspath(common_dir)))
    canonical = absolute.as_posix()
    name = absolute.parent.name if absolute.name == ".git" else absolute.name
    prefix = _slug(name) or "repository"
    repository_id = f"{prefix}-{_digest(canonical)}"
    return WorktreeIdentity(repository_id, f"{repository_id}-worktree")


def derive_session_identity(
    worktree: WorktreeIdentity,
    name: str | None = None,
) -> str:
    """Key a session to its worktree unless the caller names a distinct one."""
    if name is None:
        return f"{worktree.repository_id}-session"
    slug = _slug(name)
    if not slug:
        raise CoordinationError("an explicit session name must not be empty")
    return f"{worktree.repository_id}-session-{slug}"


def _identifiers(values: Sequence[str], label: str) -> tuple[str, ...]:
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise CoordinationError(f"{label} identifiers must be non-empty strings")
        cleaned.append(value)
    return tuple(dict.fromkeys(cleaned))


def parse_affected_claim(
    repository_ids: Sequence[str],
    authority_ids: Sequence[str],
) -> AffectedClaim:
    """Validate a declared blast surface, preserving first-seen order."""
    repositories = _identifiers(repository_ids, "repository")
    authorities = _identifiers(authority_ids, "authority")
    if not repositories and not authorities:
        raise CoordinationError("an explicit affected claim is required")
    return AffectedClaim(repositories, authorities)


def closure_fingerprint(report: ClosureReport) -> str:
    """Digest a resolved closure so a stale one cannot be acquired against.

    Membership is order-insensitive; lockability, conflicts, blockers, and
    promotion issues all participate, because any of them changing means the
    closure the caller was shown is no longer the closure being acquired.
    """
    parts = [
        "lockable" if report.lockable else "blocked",
        ",".join(sorted(report.authority_ids)),
        ",".join(
            sorted(f"{item.authority_id}@{item.owner_id}" for item in report.conflicts)
        ),
        ",".join(sorted(report.blockers)),
        ",".join(sorted(report.promotion_issues)),
    ]
    return _digest("\n".join(parts))


def require_destructive_authority(
    operation: DestructiveOperation,
    authority: str | None,
    targets: Sequence[str],
) -> None:
    """Gate a destructive operation on a validated argument and named targets.

    Only this check satisfies the gate. A skill instruction, resolved trait
    body, workflow stage, or established session never does.
    """
    if not isinstance(authority, str) or not authority.strip():
        raise CoordinationError(
            f"{operation.value} requires explicit authority; "
            "no instruction or workflow stage can supply it"
        )
    if not _identifiers(targets, "target"):
        raise CoordinationError(f"{operation.value} requires every target to be named")
