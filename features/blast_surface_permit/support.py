"""Capability-local verification subjects for the blast-surface permit."""

from __future__ import annotations

from features.support.coordination import CoordinationEnvironment


def environment() -> CoordinationEnvironment:
    return CoordinationEnvironment()


def session(env: CoordinationEnvironment, name: str | None = None) -> dict:
    root = env.worktree("project" if name is None else name)
    arguments = ["session", str(root)]
    return env.workspace_json(*arguments) | {"root": str(root)}


def claim_own_authority(env: CoordinationEnvironment, session: dict):
    return env.workspace(
        "claim", "--space", session["space"], "--authority", session["authority"]
    )


def closure(env: CoordinationEnvironment, session: dict) -> dict:
    return env.workspace_json("closure", "--space", session["space"])


def acquire(env: CoordinationEnvironment, session: dict, fingerprint: str):
    return env.workspace(
        "permit", "--space", session["space"], "--fingerprint", fingerprint
    )


def leases(env: CoordinationEnvironment) -> list[dict]:
    return env.state()["leases"]


def dependent_authority(env: CoordinationEnvironment, session: dict) -> str:
    """A writable dependency pulls its authority into the resolved closure."""
    created = env.workspace_json(
        "relate",
        "--child",
        session["repository"],
        "--dependency",
        session["authority"],
        "--access",
        "writable",
    )
    del created
    return session["authority"]
