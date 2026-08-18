"""ZPP-owned coordination over the OpenLease library API.

Agents reach every topology, session, permit, and disposition operation through
this adapter, so no session locates or interrogates a provider executable.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from openlease import OpenLease
from openlease.core.graph import AccessRole
from openlease.utils.git_adapter import GitAdapter

from zpp.core.coordination import (
    AffectedClaim,
    ClosureConflict,
    ClosureReport,
    CoordinationError,
    DestructiveOperation,
    WorktreeIdentity,
    closure_fingerprint,
    derive_session_identity,
    derive_worktree_identity,
    require_destructive_authority,
)

_WORKTREE_PATH = "."


@dataclass(frozen=True, slots=True)
class EstablishedSession:
    space_id: str
    session_identity: str
    worktree: WorktreeIdentity


@dataclass(frozen=True, slots=True)
class PermitGrant:
    space_id: str
    authority_ids: tuple[str, ...]


class OpenLeaseCoordination:
    """Narrow ZPP-owned surface over one OpenLease lifecycle."""

    def __init__(self, lifecycle: OpenLease, *, git: GitAdapter | None = None) -> None:
        self._lifecycle = lifecycle
        self._git = git or GitAdapter()

    # -- topology ---------------------------------------------------------

    def ensure_registered(self, worktree: Path) -> WorktreeIdentity:
        """Register the repository and its worktree authority exactly once."""
        checkout = self._git.inspect(worktree)
        derived = derive_worktree_identity(checkout.common_dir)
        state = self._lifecycle.snapshot()
        common = Path(checkout.common_dir).resolve()
        existing = tuple(
            item
            for item in state.repositories
            if item.common_dir is not None and Path(item.common_dir).resolve() == common
        )
        if len(existing) > 1:
            raise CoordinationError(
                f"worktree matches more than one registered repository: {worktree}"
            )
        if existing:
            repository_id = existing[0].identifier
        else:
            repository_id = derived.repository_id
            self._lifecycle.register_repository(repository_id, checkout.root)
        return WorktreeIdentity(
            repository_id, self._ensure_authority(repository_id, derived.authority_id)
        )

    def _ensure_authority(self, repository_id: str, authority_id: str) -> str:
        state = self._lifecycle.snapshot()
        for item in state.authorities:
            if item.repository_id != repository_id:
                continue
            if item.identifier == authority_id or item.path == _WORKTREE_PATH:
                return item.identifier
        self._lifecycle.register_authority(authority_id, repository_id, _WORKTREE_PATH)
        return authority_id

    def declare_parent(self, child_id: str, parent_id: str) -> object:
        return self._lifecycle.relate_parent(child_id, parent_id).data

    def declare_dependency(
        self, consumer_id: str, authority_id: str, access: str
    ) -> object:
        try:
            role = AccessRole(access)
        except ValueError as error:
            allowed = ", ".join(item.value for item in AccessRole)
            raise CoordinationError(
                f"dependency access must be one of {allowed}"
            ) from error
        return self._lifecycle.relate_dependency(consumer_id, authority_id, role).data

    def register_authority(self, repository_id: str, relative_path: str) -> object:
        identifier = f"{repository_id}-{relative_path.strip('/').replace('/', '-')}"
        return self._lifecycle.register_authority(
            identifier, repository_id, relative_path
        ).data

    # -- session ----------------------------------------------------------

    def establish_session(
        self, worktree: Path, name: str | None = None
    ) -> EstablishedSession:
        """Establish the worktree's session, registering topology if needed.

        The session is an ordinary space named deterministically from the
        worktree. A temporary space cannot serve, because OpenLease clears the
        temporary descriptor as soon as durable configuration binds to a space,
        so a session carrying space-scoped trait sources would stop matching
        and a fresh session would be created on the next invocation.
        """
        identity = self.ensure_registered(worktree)
        session_identity = derive_session_identity(identity, name)
        state = self._lifecycle.snapshot()
        if not any(item.identifier == session_identity for item in state.spaces):
            self._lifecycle.create_space(session_identity)
        self._lifecycle.associate(session_identity, (identity.repository_id,))
        return EstablishedSession(session_identity, session_identity, identity)

    def status(self, space_id: str | None = None) -> object:
        return self._lifecycle.status(space_id).data

    # -- claim and permit -------------------------------------------------

    def declare_claim(self, space_id: str, claim: AffectedClaim) -> object:
        self._require_declared_relationships(space_id, claim)
        return self._lifecycle.set_affected(
            space_id,
            repository_ids=claim.repository_ids,
            authority_ids=claim.authority_ids,
        ).data

    def _require_declared_relationships(
        self, space_id: str, claim: AffectedClaim
    ) -> None:
        """A relationship, not mere registration, makes work cross-repository."""
        state = self._lifecycle.snapshot()
        own = self._session_repositories(state, space_id)
        owner_of = {item.identifier: item.repository_id for item in state.authorities}
        claimed = set(claim.repository_ids)
        claimed.update(
            owner_of[item] for item in claim.authority_ids if item in owner_of
        )
        related = set(own)
        for item in state.parents:
            if item.child_id in related:
                related.add(item.parent_id)
            if item.parent_id in related:
                related.add(item.child_id)
        for item in state.dependencies:
            authority_owner = owner_of.get(item.authority_id)
            if item.consumer_id in related and authority_owner is not None:
                related.add(authority_owner)
            if authority_owner in related:
                related.add(item.consumer_id)
        outside = sorted(claimed - related)
        if outside:
            raise CoordinationError(
                "claim names a repository with no declared relationship: "
                f"{', '.join(outside)}; declare a parent or dependency relationship "
                "before this session may claim it"
            )

    @staticmethod
    def _session_repositories(state: object, space_id: str) -> tuple[str, ...]:
        space = next(
            (item for item in state.spaces if item.identifier == space_id), None
        )
        if space is None:
            raise CoordinationError(f"session is not established: {space_id}")
        if space.associated_repository_ids:
            return tuple(space.associated_repository_ids)
        temporary = space.temporary
        return (temporary.repository_id,) if temporary is not None else ()

    def resolve_closure(self, space_id: str) -> ClosureReport:
        """Expand the declared claim to its closure and evaluate lockability."""
        data = self._lifecycle.lockable(space_id).data
        plan = data["plan"]
        conflicts = tuple(
            ClosureConflict(item.authority_id, item.owner_id)
            for item in data["conflicts"]
        )
        return ClosureReport(
            lockable=bool(data["lockable"]),
            authority_ids=tuple(plan.held_authorities),
            conflicts=conflicts,
            blockers=tuple(data["blockers"]),
            promotion_issues=tuple(str(item) for item in data["promotion_issues"]),
        )

    def acquire_permit(self, space_id: str, fingerprint: str) -> PermitGrant:
        """Acquire only against the exact closure the caller was shown."""
        current = self.resolve_closure(space_id)
        if closure_fingerprint(current) != fingerprint:
            raise CoordinationError(
                "the resolved closure changed since it was reported; "
                "re-evaluate lockability and give a new go-ahead"
            )
        if not current.lockable:
            raise CoordinationError("the resolved closure is not lockable")
        space = self._lifecycle.lock(space_id).data
        return PermitGrant(space_id, tuple(space.held_authority_ids))

    def release_permit(self, space_id: str) -> object:
        return self._lifecycle.release(space_id).data

    def force_release(self, space_id: str, authority: str | None) -> object:
        require_destructive_authority(
            DestructiveOperation.RECOVER_FORCED, authority, (space_id,)
        )
        return self._lifecycle.recover(space_id, force=True).data

    # -- reconciliation and disposition -----------------------------------

    def reconcile_plan(self, space_id: str, repository_id: str) -> object:
        return self._lifecycle.reconcile_plan(space_id, repository_id).data

    def reconcile_apply(self, space_id: str, repository_id: str) -> object:
        return self._lifecycle.reconcile_apply(space_id, repository_id).data

    def finalize(self, space_id: str) -> object:
        return self._lifecycle.finalize(space_id).data

    def handoff(self, space_id: str, disposition: str, authority: str | None) -> object:
        require_destructive_authority(
            DestructiveOperation.HANDOFF, authority, (space_id,)
        )
        return self._lifecycle.set_handoff_disposition(space_id, disposition).data

    def abandon(
        self, space_id: str, repository_id: str, authority: str | None
    ) -> object:
        require_destructive_authority(
            DestructiveOperation.ABANDON, authority, (space_id, repository_id)
        )
        return self._lifecycle.abandon_member(space_id, repository_id).data

    def cleanup(
        self, space_id: str, repository_id: str, authority: str | None
    ) -> object:
        require_destructive_authority(
            DestructiveOperation.CLEANUP, authority, (space_id, repository_id)
        )
        return self._lifecycle.cleanup_worktree(space_id, repository_id).data

    def preparation_resume(self, space_id: str) -> object:
        return self._lifecycle.resume_preparation(space_id).data

    def preparation_rollback(self, space_id: str, authority: str | None) -> object:
        require_destructive_authority(
            DestructiveOperation.PREPARATION_ROLLBACK, authority, (space_id,)
        )
        return self._lifecycle.rollback_preparation(space_id).data


def unsupported_operation(name: str, available: Sequence[str]) -> CoordinationError:
    """Report an absent operation without pointing at a provider executable."""
    return CoordinationError(
        f"coordination operation is not available through ZPP: {name}; "
        f"available operations are {', '.join(sorted(available))}"
    )
